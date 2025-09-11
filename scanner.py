"""
scanner.py - WiFi scanning and parsing logic for net.krak
"""
import logging
import shutil
import subprocess

import scapy.all as scapy
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt, Dot11ProbeResp


def set_monitor_mode(interface, logger):
    """Activates monitor mode on the specified interface using secure subprocess calls."""
    for tool in ["ifconfig", "iwconfig"]:
        if shutil.which(tool) is None:
            logger.error(
                f"'{tool}' not found. Please install net-tools or equivalent."
            )
            return False
    try:
        # Bring interface down before changing mode to prevent issues
        subprocess.run(
            ["ifconfig", interface, "down"],
            check=True,
            capture_output=True,
            text=True,
        )
        # Set the interface to monitor mode
        subprocess.run(
            ["iwconfig", interface, "mode", "monitor"],
            check=True,
            capture_output=True,
            text=True,
        )
        # Bring the interface back up
        subprocess.run(
            ["ifconfig", interface, "up"], check=True, capture_output=True, text=True
        )
        logger.info(f"Successfully set interface '{interface}' to monitor mode.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set monitor mode on '{interface}'.")
        logger.error(f"Command '{e.cmd}' failed with exit code {e.returncode}.")
        logger.error(f"Stderr: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        logger.error(
            f"Command not found. Ensure net-tools are installed and in your PATH."
        )
        return False


def scan_networks(interface, scan_time=15, logger=None):
    """
    Scans for WiFi networks using scapy. Returns a list of dictionaries.

    Args:
        interface (str): The network interface to use for scanning.
        scan_time (int): The total duration in seconds to scan for networks.
        logger (logging.Logger): The logger instance for logging events.

    Returns:
        list: A list of dictionaries, where each dictionary represents a found network.
    """
    if logger is None:
        logger = logging.getLogger("netkrak.scanner")

    if not set_monitor_mode(interface, logger):
        return []

    networks = {}

    def handle_packet(pkt):
        # We only care about beacon and probe response frames
        if not (pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp)):
            return

        bssid = pkt[Dot11].addr2
        ssid = None
        channel = None
        security = set()

        # Traverse all Dot11Elt layers to find SSID, channel, and security info
        elt_layer = pkt.getlayer(Dot11Elt)
        while elt_layer:
            if elt_layer.ID == 0:  # SSID
                try:
                    # Decode SSID, ignoring errors for malformed names
                    ssid = elt_layer.info.decode(errors="ignore").strip()
                except Exception:
                    pass
            elif elt_layer.ID == 3:  # DSset (channel)
                channel = int(elt_layer.info[0])
            elif elt_layer.ID == 48:  # RSN Information (WPA2/WPA3)
                security.add("WPA2") # Can be refined for WPA3
            elif elt_layer.ID == 221 and elt_layer.info.startswith(
                b"\x00P\xf2\x01\x01\x00"
            ):  # Vendor Specific (WPA)
                security.add("WPA")

            elt_layer = elt_layer.payload.getlayer(Dot11Elt)

        # If SSID is empty or broadcast, it's a "hidden" network
        if not ssid:
            ssid = "<hidden>"

        # Fallback to check beacon capabilities for WEP if no WPA/WPA2 was found
        if not security:
            if pkt.haslayer(Dot11Beacon) and pkt[Dot11Beacon].cap.privacy:
                security.add("WEP")
            else:
                security.add("Open")

        if bssid and ssid:
            # Prioritize stronger security protocols in the final display string
            sec_str = (
                "WPA2"
                if "WPA2" in security
                else "WPA"
                if "WPA" in security
                else "WEP"
                if "WEP" in security
                else "Open"
            )
            networks[bssid] = {
                "ssid": ssid,
                "bssid": bssid,
                "channel": channel,
                "security": sec_str,
            }

    try:
        # Sniff packets for the specified duration
        scapy.sniff(iface=interface, prn=handle_packet, store=0, timeout=scan_time)
    except Exception as e:
        logger.error(
            f"An error occurred during sniffing on interface '{interface}': {e}"
        )
        logger.error("Ensure the interface exists and you have sufficient permissions.")
        return []

    logger.info(f"Scan complete. Found {len(networks)} unique networks.")
    return list(networks.values())