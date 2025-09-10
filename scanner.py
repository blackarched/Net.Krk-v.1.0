"""
scanner.py - WiFi scanning and parsing logic for net.krak
"""
import scapy.all as scapy
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11ProbeResp, Dot11Elt
import subprocess
import logging
import shutil
import re
import tempfile
import time
import csv
import os
from pathlib import Path

def list_wifi_interfaces(logger=None):
    """
    Lists available wireless interfaces using iwconfig.
    """
    if logger is None:
        logger = logging.getLogger("scanner")
    if shutil.which("iwconfig") is None:
        logger.error("iwconfig not found. Cannot list wireless interfaces.")
        return []
    try:
        proc = subprocess.run(["iwconfig"], capture_output=True, text=True, check=True)
        # Regex to find interface names like wlan0, wlp3s0, etc.
        interfaces = re.findall(r"^([a-zA-Z0-9]+)\s+IEEE 802.11", proc.stdout, re.MULTILINE)
        logger.info(f"Found interfaces: {interfaces}")
        return interfaces
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Error listing wireless interfaces: {e}")
        return []

def scan_networks_airodump(interface, scan_time=15, logger=None):
    """
    Scan for WiFi networks using airodump-ng. More reliable than scapy.
    """
    if logger is None:
        logger = logging.getLogger("scanner")
    if shutil.which("airodump-ng") is None:
        logger.error("airodump-ng not found. Cannot scan with this method.")
        return []

    networks = {}
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, prefix='netkrak-scan-', suffix='.csv') as tmpfile:
        output_prefix = tmpfile.name.replace(".csv", "")
        # Command to run airodump-ng
        cmd = ["airodump-ng", "--output-format", "csv", "--write", output_prefix, interface]
        logger.info(f"Starting airodump-ng scan: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            proc.wait(timeout=scan_time)
        except subprocess.TimeoutExpired:
            logger.info(f"Scan time of {scan_time}s expired. Terminating airodump-ng.")
            proc.terminate()
            time.sleep(2) # Give airodump-ng a moment to write the file
            proc.kill()

        # airodump-ng creates a file named {prefix}-01.csv
        csv_path = f"{output_prefix}-01.csv"
        if not os.path.exists(csv_path):
            logger.error("airodump-ng did not produce an output file.")
            return []

        try:
            with open(csv_path, 'r', errors='ignore') as f:
                lines = f.read().splitlines()
                try:
                    client_header_index = lines.index('Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs')
                    ap_lines = lines[1:client_header_index]
                except ValueError:
                    ap_lines = lines[1:]

                csv_reader = csv.reader(ap_lines)
                for row in csv_reader:
                    if len(row) >= 14:
                        bssid = row[0].strip()
                        privacy = row[5].strip()
                        channel = row[3].strip()
                        ssid = row[13].strip()
                        if bssid and ssid:
                            networks[bssid] = {
                                "bssid": bssid,
                                "ssid": ssid,
                                "channel": int(channel),
                                "security": privacy
                            }
        except Exception as e:
            logger.error(f"Error parsing airodump-ng output file {csv_path}: {e}")
        finally:
            for f in Path(tempfile.gettempdir()).glob(f"{Path(output_prefix).name}*"):
                try:
                    os.remove(f)
                except OSError as e:
                    logger.warning(f"Failed to remove temp file {f}: {e}")

    logger.info(f"Found {len(networks)} networks using airodump-ng.")
    return list(networks.values())

def scan_networks_scapy(interface, scan_count=50, scan_time=None, logger=None):
    if logger is None:
        logger = logging.getLogger("scanner")

    networks = {}
    def handle(pkt):
        if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
            bssid = pkt[Dot11].addr2
            ssid, channel, security = None, None, set()
            elt = pkt.getlayer(Dot11Elt)
            while elt is not None:
                if elt.ID == 0:
                    try: ssid = elt.info.decode(errors="ignore")
                    except Exception: pass
                elif elt.ID == 3:
                    channel = elt.info[0] if elt.info else None
                elif elt.ID == 48:
                    security.add("WPA2")
                elif elt.ID == 221 and elt.info.startswith(b'\x00P\xf2\x01\x01\x00'):
                    security.add("WPA")
                elt = elt.payload.getlayer(Dot11Elt)
            
            if not security:
                if pkt.haslayer(Dot11Beacon) and pkt.getlayer(Dot11Beacon).cap.privacy:
                    security.add("WEP")
                else:
                    security.add("Open")

            if bssid and ssid is not None:
                networks[bssid] = {"ssid": ssid, "bssid": bssid, "channel": channel, "security": "/".join(sorted(list(security)))}

    sniff_kwargs = dict(iface=interface, prn=handle, store=0)
    if scan_time: sniff_kwargs["timeout"] = scan_time
    else: sniff_kwargs["count"] = scan_count
    
    try:
        scapy.sniff(**sniff_kwargs)
    except Exception as e:
        logger.error(f"Error during scapy sniff: {e}")

    logger.info(f"Found {len(networks)} networks using scapy.")
    return list(networks.values())

def scan_networks(interface, method="airodump", **kwargs):
    """
    Wrapper for WiFi scanning.
    :param interface: The wireless interface to use.
    :param method: 'airodump' or 'scapy'.
    :param kwargs: Arguments for the specific scanner function.
    """
    if method == "airodump":
        return scan_networks_airodump(interface, scan_time=kwargs.get("scan_time", 15), logger=kwargs.get("logger"))
    elif method == "scapy":
        return scan_networks_scapy(interface, scan_count=kwargs.get("scan_count", 50), scan_time=kwargs.get("scan_time"), logger=kwargs.get("logger"))
    else:
        if kwargs.get("logger"):
            kwargs.get("logger").error(f"Unknown scanner method: {method}")
        raise ValueError("Unknown scanner method specified.")
