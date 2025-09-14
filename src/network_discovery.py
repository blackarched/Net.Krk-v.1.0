#!/usr/bin/env python3
"""
Advanced Network Discovery Module for NET.KRAK
Provides comprehensive network scanning, analysis, and monitoring capabilities
"""

import subprocess
import re
import time
import json
import os
import threading
import queue
import psutil
import socket
import struct
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkDiscovery:
    """Advanced network discovery and analysis class"""
    
    def __init__(self):
        self.is_scanning = False
        self.discovered_networks = []
        self.network_history = []
        self.scan_queue = queue.Queue()
        self.monitor_thread = None
        self.continuous_monitoring = False
        self.scan_interval = 30  # seconds
        self.last_scan_time = None
        self.interface_info = {}
        self.signal_strength_history = {}
        
    def get_available_interfaces(self) -> List[Dict]:
        """Get all available network interfaces"""
        interfaces = []
        try:
            # Get network interfaces using psutil
            for interface, addrs in psutil.net_if_addrs().items():
                if interface.startswith(('wlan', 'wifi', 'eth', 'en')):
                    interface_data = {
                        'name': interface,
                        'type': 'wireless' if interface.startswith(('wlan', 'wifi')) else 'wired',
                        'addresses': [],
                        'is_up': False,
                        'monitor_mode': False
                    }
                    
                    for addr in addrs:
                        if addr.family == socket.AF_INET:  # IPv4
                            interface_data['addresses'].append(addr.address)
                            interface_data['is_up'] = True
                    
                    # Check if interface supports monitor mode
                    interface_data['monitor_mode'] = self._check_monitor_mode_support(interface)
                    interfaces.append(interface_data)
                    
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            
        return interfaces
    
    def _check_monitor_mode_support(self, interface: str) -> bool:
        """Check if interface supports monitor mode"""
        try:
            result = subprocess.run(['iw', interface, 'info'], 
                                  capture_output=True, text=True, timeout=5)
            return 'monitor' in result.stdout.lower()
        except:
            return False
    
    def start_continuous_monitoring(self, interface: str, interval: int = 30):
        """Start continuous network monitoring"""
        if self.continuous_monitoring:
            return False
            
        self.continuous_monitoring = True
        self.scan_interval = interval
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interface,), 
            daemon=True
        )
        self.monitor_thread.start()
        return True
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        self.continuous_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self, interface: str):
        """Background monitoring loop"""
        while self.continuous_monitoring:
            try:
                self.scan_networks(interface)
                time.sleep(self.scan_interval)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)
    
    def scan_networks(self, interface: str = 'wlan0') -> List[Dict]:
        """Perform comprehensive network scan"""
        self.is_scanning = True
        self.last_scan_time = datetime.now()
        
        try:
            # Try multiple scanning methods
            networks = []
            
            # Method 1: iwlist (most comprehensive)
            networks.extend(self._scan_with_iwlist(interface))
            
            # Method 2: iw (faster, modern)
            if not networks:
                networks.extend(self._scan_with_iw(interface))
            
            # Method 3: nmcli (NetworkManager)
            if not networks:
                networks.extend(self._scan_with_nmcli())
            
            # Enhance network data
            enhanced_networks = []
            for network in networks:
                enhanced = self._enhance_network_data(network)
                enhanced_networks.append(enhanced)
            
            # Update discovered networks
            self.discovered_networks = enhanced_networks
            
            # Update history
            self._update_network_history(enhanced_networks)
            
            logger.info(f"Discovered {len(enhanced_networks)} networks")
            return enhanced_networks
            
        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            return []
        finally:
            self.is_scanning = False
    
    def _scan_with_iwlist(self, interface: str) -> List[Dict]:
        """Scan using iwlist (most comprehensive)"""
        networks = []
        try:
            result = subprocess.run(
                ['iwlist', interface, 'scan'], 
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                networks = self._parse_iwlist_output(result.stdout)
                
        except subprocess.TimeoutExpired:
            logger.warning("iwlist scan timed out")
        except Exception as e:
            logger.error(f"iwlist scan error: {e}")
            
        return networks
    
    def _scan_with_iw(self, interface: str) -> List[Dict]:
        """Scan using iw (modern, faster)"""
        networks = []
        try:
            result = subprocess.run(
                ['iw', 'dev', interface, 'scan'], 
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                networks = self._parse_iw_output(result.stdout)
                
        except subprocess.TimeoutExpired:
            logger.warning("iw scan timed out")
        except Exception as e:
            logger.error(f"iw scan error: {e}")
            
        return networks
    
    def _scan_with_nmcli(self) -> List[Dict]:
        """Scan using nmcli (NetworkManager)"""
        networks = []
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,BSSID,MODE,CHAN,FREQ,RATE,SIGNAL,SECURITY', 'dev', 'wifi', 'list'], 
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                networks = self._parse_nmcli_output(result.stdout)
                
        except subprocess.TimeoutExpired:
            logger.warning("nmcli scan timed out")
        except Exception as e:
            logger.error(f"nmcli scan error: {e}")
            
        return networks
    
    def _parse_iwlist_output(self, output: str) -> List[Dict]:
        """Parse iwlist scan output"""
        networks = []
        current = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'Cell' in line and 'Address:' in line:
                if current:
                    networks.append(current)
                current = {}
                bssid_match = re.search(r'Address: ([0-9A-Fa-f:]{17})', line)
                if bssid_match:
                    current['bssid'] = bssid_match.group(1)
                    
            elif 'ESSID:' in line:
                ssid_match = re.search(r'ESSID:"([^"]*)"', line)
                if ssid_match:
                    current['ssid'] = ssid_match.group(1) or 'Hidden Network'
                    
            elif 'Signal level=' in line:
                signal_match = re.search(r'Signal level=(-?\d+)', line)
                if signal_match:
                    current['signal'] = int(signal_match.group(1))
                    
            elif 'Frequency:' in line:
                freq_match = re.search(r'Frequency:(\d+\.\d+)', line)
                if freq_match:
                    freq = float(freq_match.group(1))
                    current['frequency'] = freq
                    current['channel'] = self._frequency_to_channel(freq)
                    
            elif 'Encryption key:' in line:
                current['security'] = 'WPA2' if 'on' in line else 'Open'
                
            elif 'IE:' in line and 'WPA' in line:
                if 'WPA2' in line:
                    current['security'] = 'WPA2'
                elif 'WPA3' in line:
                    current['security'] = 'WPA3'
                else:
                    current['security'] = 'WPA'
                    
            elif 'Quality=' in line:
                quality_match = re.search(r'Quality=(\d+)/(\d+)', line)
                if quality_match:
                    quality = int(quality_match.group(1))
                    max_quality = int(quality_match.group(2))
                    current['quality'] = (quality / max_quality) * 100
        
        if current:
            networks.append(current)
            
        return networks
    
    def _parse_iw_output(self, output: str) -> List[Dict]:
        """Parse iw scan output"""
        networks = []
        current = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith('BSS'):
                if current:
                    networks.append(current)
                current = {}
                bssid_match = re.search(r'BSS ([0-9A-Fa-f:]{17})', line)
                if bssid_match:
                    current['bssid'] = bssid_match.group(1)
                    
            elif 'SSID:' in line:
                ssid_match = re.search(r'SSID: (.+)', line)
                if ssid_match:
                    current['ssid'] = ssid_match.group(1) or 'Hidden Network'
                    
            elif 'signal:' in line:
                signal_match = re.search(r'signal: (-?\d+)', line)
                if signal_match:
                    current['signal'] = int(signal_match.group(1))
                    
            elif 'freq:' in line:
                freq_match = re.search(r'freq: (\d+)', line)
                if freq_match:
                    freq = int(freq_match.group(1))
                    current['frequency'] = freq
                    current['channel'] = self._frequency_to_channel(freq)
                    
            elif 'WPA:' in line:
                current['security'] = 'WPA'
            elif 'WPA2:' in line:
                current['security'] = 'WPA2'
            elif 'WPA3:' in line:
                current['security'] = 'WPA3'
            elif 'RSN:' in line:
                current['security'] = 'WPA2'
        
        if current:
            networks.append(current)
            
        return networks
    
    def _parse_nmcli_output(self, output: str) -> List[Dict]:
        """Parse nmcli scan output"""
        networks = []
        
        for line in output.split('\n'):
            if not line.strip():
                continue
                
            parts = line.split(':')
            if len(parts) >= 8:
                network = {
                    'ssid': parts[0] or 'Hidden Network',
                    'bssid': parts[1],
                    'mode': parts[2],
                    'channel': parts[3],
                    'frequency': parts[4],
                    'rate': parts[5],
                    'signal': int(parts[6]) if parts[6].isdigit() else 0,
                    'security': parts[7] if parts[7] else 'Open'
                }
                networks.append(network)
                
        return networks
    
    def _frequency_to_channel(self, freq: float) -> int:
        """Convert frequency to channel number"""
        if 2412 <= freq <= 2484:
            return int((freq - 2412) / 5) + 1
        elif 5170 <= freq <= 5825:
            return int((freq - 5000) / 5)
        elif 5000 <= freq <= 6000:
            return int((freq - 5000) / 5)
        return 0
    
    def _enhance_network_data(self, network: Dict) -> Dict:
        """Enhance network data with additional analysis"""
        enhanced = network.copy()
        
        # Add timestamp
        enhanced['discovered_at'] = datetime.now().isoformat()
        
        # Calculate signal quality percentage
        signal = enhanced.get('signal', -100)
        if signal > -30:
            enhanced['quality'] = 100
        elif signal > -50:
            enhanced['quality'] = 80
        elif signal > -70:
            enhanced['quality'] = 60
        elif signal > -80:
            enhanced['quality'] = 40
        elif signal > -90:
            enhanced['quality'] = 20
        else:
            enhanced['quality'] = 10
            
        # Determine frequency band
        freq = enhanced.get('frequency', 0)
        if 2400 <= freq <= 2500:
            enhanced['band'] = '2.4GHz'
        elif 5000 <= freq <= 6000:
            enhanced['band'] = '5GHz'
        else:
            enhanced['band'] = 'Unknown'
            
        # Security analysis
        security = enhanced.get('security', 'Open')
        if 'WPA3' in security:
            enhanced['security_level'] = 'High'
            enhanced['encryption'] = 'AES-256'
        elif 'WPA2' in security:
            enhanced['security_level'] = 'Medium'
            enhanced['encryption'] = 'AES-128'
        elif 'WPA' in security:
            enhanced['security_level'] = 'Low'
            enhanced['encryption'] = 'TKIP'
        else:
            enhanced['security_level'] = 'None'
            enhanced['encryption'] = 'None'
            
        # Add vulnerability assessment
        enhanced['vulnerabilities'] = self._assess_vulnerabilities(enhanced)
        
        # Add network type classification
        enhanced['network_type'] = self._classify_network_type(enhanced)
        
        return enhanced
    
    def _assess_vulnerabilities(self, network: Dict) -> List[str]:
        """Assess network vulnerabilities"""
        vulnerabilities = []
        
        security = network.get('security', 'Open')
        signal = network.get('signal', -100)
        
        if security == 'Open':
            vulnerabilities.extend(['Open Network', 'No Encryption', 'Data Interception Risk'])
        elif 'WEP' in security:
            vulnerabilities.extend(['WEP Encryption', 'Weak Security', 'Easily Crackable'])
        elif 'WPA' in security and 'WPA2' not in security:
            vulnerabilities.extend(['WPA Only', 'TKIP Vulnerability', 'Weak Security'])
        elif 'WPS' in str(network):
            vulnerabilities.append('WPS Enabled')
            
        if signal > -50:
            vulnerabilities.append('Strong Signal - Easy Target')
            
        return vulnerabilities
    
    def _classify_network_type(self, network: Dict) -> str:
        """Classify network type based on characteristics"""
        ssid = network.get('ssid', '').lower()
        security = network.get('security', 'Open')
        
        if 'guest' in ssid or 'public' in ssid:
            return 'Public/Guest'
        elif 'corp' in ssid or 'office' in ssid or 'enterprise' in ssid:
            return 'Corporate'
        elif 'home' in ssid or 'house' in ssid:
            return 'Residential'
        elif security == 'Open':
            return 'Public'
        else:
            return 'Private'
    
    def _update_network_history(self, networks: List[Dict]):
        """Update network discovery history"""
        timestamp = datetime.now()
        
        for network in networks:
            bssid = network.get('bssid')
            if bssid:
                if bssid not in self.signal_strength_history:
                    self.signal_strength_history[bssid] = []
                
                self.signal_strength_history[bssid].append({
                    'timestamp': timestamp,
                    'signal': network.get('signal', -100),
                    'quality': network.get('quality', 0)
                })
                
                # Keep only last 100 readings
                if len(self.signal_strength_history[bssid]) > 100:
                    self.signal_strength_history[bssid] = self.signal_strength_history[bssid][-100:]
        
        # Update network history
        self.network_history.append({
            'timestamp': timestamp,
            'networks': networks,
            'count': len(networks)
        })
        
        # Keep only last 50 scans
        if len(self.network_history) > 50:
            self.network_history = self.network_history[-50:]
    
    def get_network_analytics(self) -> Dict:
        """Get comprehensive network analytics"""
        if not self.discovered_networks:
            return {}
        
        analytics = {
            'total_networks': len(self.discovered_networks),
            'security_distribution': {},
            'band_distribution': {},
            'signal_analysis': {},
            'channel_analysis': {},
            'network_types': {},
            'vulnerability_summary': {},
            'scan_history': len(self.network_history),
            'last_scan': self.last_scan_time.isoformat() if self.last_scan_time else None
        }
        
        # Security distribution
        for network in self.discovered_networks:
            security = network.get('security', 'Open')
            analytics['security_distribution'][security] = analytics['security_distribution'].get(security, 0) + 1
        
        # Band distribution
        for network in self.discovered_networks:
            band = network.get('band', 'Unknown')
            analytics['band_distribution'][band] = analytics['band_distribution'].get(band, 0) + 1
        
        # Signal analysis
        signals = [n.get('signal', -100) for n in self.discovered_networks if n.get('signal')]
        if signals:
            analytics['signal_analysis'] = {
                'min': min(signals),
                'max': max(signals),
                'avg': sum(signals) / len(signals),
                'strong_signals': len([s for s in signals if s > -50]),
                'weak_signals': len([s for s in signals if s < -80])
            }
        
        # Channel analysis
        channels = [n.get('channel', 0) for n in self.discovered_networks if n.get('channel')]
        if channels:
            analytics['channel_analysis'] = {
                'most_used': max(set(channels), key=channels.count),
                'channel_distribution': {ch: channels.count(ch) for ch in set(channels)},
                'congestion_level': len(set(channels)) / max(channels) if channels else 0
            }
        
        # Network types
        for network in self.discovered_networks:
            net_type = network.get('network_type', 'Unknown')
            analytics['network_types'][net_type] = analytics['network_types'].get(net_type, 0) + 1
        
        # Vulnerability summary
        all_vulns = []
        for network in self.discovered_networks:
            all_vulns.extend(network.get('vulnerabilities', []))
        
        vuln_counts = {}
        for vuln in all_vulns:
            vuln_counts[vuln] = vuln_counts.get(vuln, 0) + 1
        
        analytics['vulnerability_summary'] = vuln_counts
        
        return analytics
    
    def get_network_details(self, bssid: str) -> Optional[Dict]:
        """Get detailed information about a specific network"""
        for network in self.discovered_networks:
            if network.get('bssid') == bssid:
                # Add signal history
                network['signal_history'] = self.signal_strength_history.get(bssid, [])
                return network
        return None
    
    def search_networks(self, query: str) -> List[Dict]:
        """Search networks by SSID, BSSID, or other criteria"""
        results = []
        query_lower = query.lower()
        
        for network in self.discovered_networks:
            if (query_lower in network.get('ssid', '').lower() or
                query_lower in network.get('bssid', '').lower() or
                query_lower in network.get('security', '').lower()):
                results.append(network)
        
        return results
    
    def filter_networks(self, filters: Dict) -> List[Dict]:
        """Filter networks based on criteria"""
        results = self.discovered_networks.copy()
        
        if 'security' in filters:
            results = [n for n in results if filters['security'] in n.get('security', '')]
        
        if 'band' in filters:
            results = [n for n in results if n.get('band') == filters['band']]
        
        if 'min_signal' in filters:
            results = [n for n in results if n.get('signal', -100) >= filters['min_signal']]
        
        if 'max_signal' in filters:
            results = [n for n in results if n.get('signal', -100) <= filters['max_signal']]
        
        if 'network_type' in filters:
            results = [n for n in results if n.get('network_type') == filters['network_type']]
        
        return results

# Global instance
network_discovery = NetworkDiscovery()