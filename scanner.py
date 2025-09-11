"""
scanner.py - Enhanced WiFi scanning and parsing logic for net.krak
Improved with better network detection, interface management, and performance
"""
import logging
import shutil
import subprocess
import time
import threading
import json
from pathlib import Path
from collections import defaultdict

import scapy.all as scapy
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt, Dot11ProbeResp, Dot11ProbeReq

class NetworkScanner:
    """Enhanced network scanner with better performance and reliability"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("netkrak.scanner")
        self.networks = {}
        self.clients = {}
        self.scan_active = False
        self.lock = threading.Lock()
        
    def _log_scan_event(self, event_type, **kwargs):
        """Log scan events with structured data"""
        event_data = {
            "timestamp": time.time(),
            "event_type": event_type,
            **kwargs
        }
        self.logger.info(json.dumps(event_data))
    
    def _validate_interface(self, interface):
        """Validate that the interface exists"""
        try:
            if interface not in scapy.get_if_list():
                raise ValueError(f"Interface {interface} not found")
            return True
        except Exception as e:
            raise ValueError(f"Interface validation failed: {e}")
    
    def _check_monitor_mode(self, interface):
        """Check if interface is in monitor mode"""
        try:
            result = subprocess.run(
                ["iwconfig", interface], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return "Mode:Monitor" in result.stdout
        except Exception:
            return False
    
    def set_monitor_mode(self, interface, logger=None):
        """
        Enhanced monitor mode activation with better error handling
        
        Args:
            interface: Network interface name
            logger: Logger instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        if logger is None:
            logger = self.logger
            
        # Check if required tools are available
        required_tools = ["ifconfig", "iwconfig", "iw"]
        for tool in required_tools:
            if shutil.which(tool) is None:
                logger.error(f"Required tool '{tool}' not found. Please install net-tools or equivalent.")
                return False
        
        try:
            # Validate interface exists
            self._validate_interface(interface)
            
            # Check if already in monitor mode
            if self._check_monitor_mode(interface):
                logger.info(f"Interface '{interface}' is already in monitor mode.")
                return True
            
            logger.info(f"Setting interface '{interface}' to monitor mode...")
            self._log_scan_event("monitor_mode_start", interface=interface)
            
            # Bring interface down
            result = subprocess.run(
                ["ifconfig", interface, "down"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Set to monitor mode using iw (preferred) or iwconfig
            if shutil.which("iw"):
                result = subprocess.run(
                    ["iw", "dev", interface, "set", "type", "monitor"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    ["iwconfig", interface, "mode", "monitor"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            # Bring interface back up
            result = subprocess.run(
                ["ifconfig", interface, "up"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Verify monitor mode was set
            if self._check_monitor_mode(interface):
                logger.info(f"Successfully set interface '{interface}' to monitor mode.")
                self._log_scan_event("monitor_mode_success", interface=interface)
                return True
            else:
                logger.error(f"Failed to verify monitor mode on '{interface}'.")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set monitor mode on '{interface}'.")
            logger.error(f"Command '{e.cmd}' failed with exit code {e.returncode}.")
            logger.error(f"Stderr: {e.stderr.strip()}")
            self._log_scan_event("monitor_mode_error", interface=interface, error=str(e))
            return False
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout setting monitor mode on '{interface}'.")
            self._log_scan_event("monitor_mode_timeout", interface=interface)
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting monitor mode: {e}")
            self._log_scan_event("monitor_mode_error", interface=interface, error=str(e))
            return False
    
    def _parse_beacon_frame(self, pkt):
        """Parse beacon frame to extract network information"""
        try:
            bssid = pkt[Dot11].addr2
            ssid = None
            channel = None
            security = set()
            rssi = None
            vendor_info = {}
            
            # Extract RSSI from RadioTap layer if available
            if pkt.haslayer(scapy.RadioTap):
                rssi = pkt[scapy.RadioTap].dBm_AntSignal
            
            # Parse information elements
            elt_layer = pkt.getlayer(Dot11Elt)
            while elt_layer:
                if elt_layer.ID == 0:  # SSID
                    try:
                        ssid = elt_layer.info.decode(errors="ignore").strip()
                    except Exception:
                        pass
                elif elt_layer.ID == 3:  # DSset (channel)
                    channel = int(elt_layer.info[0])
                elif elt_layer.ID == 48:  # RSN Information (WPA2/WPA3)
                    security.add("WPA2")
                elif elt_layer.ID == 221:  # Vendor Specific
                    if elt_layer.info.startswith(b"\x00P\xf2\x01\x01\x00"):  # WPA
                        security.add("WPA")
                    elif elt_layer.info.startswith(b"\x00P\xf2\x04\x01\x00"):  # WPA3
                        security.add("WPA3")
                elif elt_layer.ID == 61:  # HT Capabilities
                    security.add("802.11n")
                elif elt_layer.ID == 191:  # VHT Capabilities
                    security.add("802.11ac")
                elif elt_layer.ID == 195:  # HE Capabilities
                    security.add("802.11ax")
                
                elt_layer = elt_layer.payload.getlayer(Dot11Elt)
            
            # Determine security type
            if not security:
                if pkt.haslayer(Dot11Beacon) and pkt[Dot11Beacon].cap.privacy:
                    security.add("WEP")
                else:
                    security.add("Open")
            
            # Prioritize strongest security protocol
            sec_str = "WPA3" if "WPA3" in security else "WPA2" if "WPA2" in security else "WPA" if "WPA" in security else "WEP" if "WEP" in security else "Open"
            
            return {
                "bssid": bssid,
                "ssid": ssid or "<hidden>",
                "channel": channel,
                "security": sec_str,
                "rssi": rssi,
                "capabilities": list(security),
                "vendor_info": vendor_info
            }
        except Exception as e:
            self.logger.debug(f"Error parsing beacon frame: {e}")
            return None
    
    def _parse_probe_response(self, pkt):
        """Parse probe response frame"""
        return self._parse_beacon_frame(pkt)  # Same parsing logic
    
    def _parse_probe_request(self, pkt):
        """Parse probe request frame to identify clients"""
        try:
            client_mac = pkt[Dot11].addr2
            ssid = None
            
            # Extract SSID from probe request
            elt_layer = pkt.getlayer(Dot11Elt)
            while elt_layer:
                if elt_layer.ID == 0:  # SSID
                    try:
                        ssid = elt_layer.info.decode(errors="ignore").strip()
                    except Exception:
                        pass
                    break
                elt_layer = elt_layer.payload.getlayer(Dot11Elt)
            
            return {
                "client_mac": client_mac,
                "ssid": ssid or "<hidden>",
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.debug(f"Error parsing probe request: {e}")
            return None
    
    def _packet_handler(self, pkt):
        """Enhanced packet handler for network scanning"""
        try:
            if not pkt.haslayer(Dot11):
                return
            
            # Handle beacon frames
            if pkt.haslayer(Dot11Beacon):
                network_info = self._parse_beacon_frame(pkt)
                if network_info:
                    with self.lock:
                        self.networks[network_info["bssid"]] = network_info
            
            # Handle probe response frames
            elif pkt.haslayer(Dot11ProbeResp):
                network_info = self._parse_probe_response(pkt)
                if network_info:
                    with self.lock:
                        self.networks[network_info["bssid"]] = network_info
            
            # Handle probe request frames (client detection)
            elif pkt.haslayer(Dot11ProbeReq):
                client_info = self._parse_probe_request(pkt)
                if client_info:
                    with self.lock:
                        self.clients[client_info["client_mac"]] = client_info
                        
        except Exception as e:
            self.logger.debug(f"Error in packet handler: {e}")
    
    def scan_networks(self, interface, scan_time=15, method="scapy", logger=None):
        """
        Enhanced network scanning with multiple methods and better performance
        
        Args:
            interface: Network interface to use for scanning
            scan_time: Duration to scan in seconds
            method: Scanning method ("scapy" or "airodump")
            logger: Logger instance
            
        Returns:
            list: List of discovered networks
        """
        if logger is None:
            logger = self.logger
        
        try:
            # Validate interface
            self._validate_interface(interface)
            
            # Set monitor mode if needed
            if not self._check_monitor_mode(interface):
                if not self.set_monitor_mode(interface, logger):
                    logger.error(f"Failed to set monitor mode on {interface}")
                    return []
            
            logger.info(f"Starting network scan on {interface} using {method} for {scan_time} seconds...")
            self._log_scan_event("scan_start", interface=interface, method=method, scan_time=scan_time)
            
            # Clear previous results
            with self.lock:
                self.networks.clear()
                self.clients.clear()
            
            self.scan_active = True
            start_time = time.time()
            
            if method == "scapy":
                # Use scapy for scanning
                scapy.sniff(
                    iface=interface, 
                    prn=self._packet_handler, 
                    store=0, 
                    timeout=scan_time
                )
            elif method == "airodump":
                # Use airodump-ng for scanning
                self._scan_with_airodump(interface, scan_time, logger)
            else:
                raise ValueError(f"Unknown scanning method: {method}")
            
            self.scan_active = False
            duration = time.time() - start_time
            
            # Get final results
            with self.lock:
                networks = list(self.networks.values())
                clients = list(self.clients.values())
            
            logger.info(f"Scan complete. Found {len(networks)} networks and {len(clients)} clients in {duration:.2f}s")
            self._log_scan_event("scan_complete", 
                               interface=interface, 
                               networks_found=len(networks),
                               clients_found=len(clients),
                               duration=duration)
            
            return networks
            
        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            self._log_scan_event("scan_error", interface=interface, error=str(e))
            self.scan_active = False
            return []
    
    def _scan_with_airodump(self, interface, scan_time, logger):
        """Scan using airodump-ng for better performance"""
        try:
            # Create temporary output file
            output_file = f"/tmp/netkrak_scan_{int(time.time())}"
            
            cmd = ["airodump-ng", "-w", output_file, "--output-format", "csv", interface]
            
            # Start airodump-ng
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for scan to complete
            time.sleep(scan_time)
            
            # Terminate process
            process.terminate()
            process.wait()
            
            # Parse CSV output
            self._parse_airodump_output(output_file, logger)
            
            # Clean up
            try:
                os.remove(f"{output_file}-01.csv")
            except:
                pass
                
        except Exception as e:
            logger.error(f"Airodump scan failed: {e}")
    
    def _parse_airodump_output(self, output_file, logger):
        """Parse airodump-ng CSV output"""
        try:
            csv_file = f"{output_file}-01.csv"
            if not os.path.exists(csv_file):
                return
            
            with open(csv_file, 'r') as f:
                lines = f.readlines()
            
            # Find the start of network data
            start_idx = 0
            for i, line in enumerate(lines):
                if "BSSID" in line and "First time seen" in line:
                    start_idx = i + 1
                    break
            
            # Parse network data
            for line in lines[start_idx:]:
                if not line.strip() or line.startswith("Station MAC"):
                    break
                
                parts = line.split(',')
                if len(parts) >= 14:
                    bssid = parts[0].strip()
                    if bssid and bssid != "BSSID":
                        ssid = parts[13].strip()
                        channel = parts[3].strip()
                        security = parts[5].strip()
                        rssi = parts[10].strip()
                        
                        with self.lock:
                            self.networks[bssid] = {
                                "bssid": bssid,
                                "ssid": ssid or "<hidden>",
                                "channel": int(channel) if channel.isdigit() else None,
                                "security": security or "Unknown",
                                "rssi": int(rssi) if rssi.lstrip('-').isdigit() else None,
                                "capabilities": [],
                                "vendor_info": {}
                            }
        except Exception as e:
            logger.error(f"Error parsing airodump output: {e}")
    
    def get_network_info(self, bssid):
        """Get detailed information about a specific network"""
        with self.lock:
            return self.networks.get(bssid)
    
    def get_client_info(self, client_mac):
        """Get information about a specific client"""
        with self.lock:
            return self.clients.get(client_mac)
    
    def get_scan_status(self):
        """Get current scan status"""
        return {
            "active": self.scan_active,
            "networks_found": len(self.networks),
            "clients_found": len(self.clients)
        }

# Global scanner instance
scanner = NetworkScanner()

def set_monitor_mode(interface, logger=None):
    """Set interface to monitor mode"""
    return scanner.set_monitor_mode(interface, logger)

def scan_networks(interface, scan_time=15, method="scapy", logger=None):
    """Scan for WiFi networks"""
    return scanner.scan_networks(interface, scan_time, method, logger)

def list_wifi_interfaces(logger=None):
    """
    List available WiFi interfaces
    
    Args:
        logger: Logger instance
        
    Returns:
        list: List of available WiFi interfaces
    """
    if logger is None:
        logger = logging.getLogger("netkrak.scanner")
    
    interfaces = []
    try:
        # Get all interfaces
        all_interfaces = scapy.get_if_list()
        
        # Filter for wireless interfaces
        for iface in all_interfaces:
            try:
                # Check if interface supports wireless operations
                result = subprocess.run(
                    ["iwconfig", iface],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "IEEE 802.11" in result.stdout or "ESSID" in result.stdout:
                    interfaces.append(iface)
            except:
                continue
        
        logger.info(f"Found {len(interfaces)} WiFi interfaces: {interfaces}")
        return interfaces
        
    except Exception as e:
        logger.error(f"Error listing WiFi interfaces: {e}")
        return []

def get_network_info(bssid):
    """Get detailed information about a specific network"""
    return scanner.get_network_info(bssid)

def get_client_info(client_mac):
    """Get information about a specific client"""
    return scanner.get_client_info(client_mac)

def get_scan_status():
    """Get current scan status"""
    return scanner.get_scan_status()