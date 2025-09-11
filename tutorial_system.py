#!/usr/bin/env python3
"""
Interactive Tutorial System for Enhanced Network Scanner
=======================================================

This module provides comprehensive, interactive tutorials for all aspects
of network security testing and attack methodologies.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class TutorialStep:
    """Represents a single step in a tutorial."""
    title: str
    content: str
    code_example: str = ""
    interactive: bool = False
    question: str = ""
    correct_answer: str = ""

class TutorialSystem:
    """Interactive tutorial system for network security education."""
    
    def __init__(self):
        self.console = Console()
        self.tutorials = self._initialize_tutorials()
    
    def _initialize_tutorials(self) -> Dict[str, List[TutorialStep]]:
        """Initialize all available tutorials."""
        return {
            "network_discovery": self._get_network_discovery_tutorial(),
            "arp_spoofing": self._get_arp_spoofing_tutorial(),
            "packet_sniffing": self._get_packet_sniffing_tutorial(),
            "security_best_practices": self._get_security_best_practices_tutorial(),
            "attack_mitigation": self._get_attack_mitigation_tutorial(),
            "beginner_guide": self._get_beginner_guide_tutorial()
        }
    
    def show_tutorial_menu(self):
        """Display the main tutorial menu."""
        while True:
            self.console.print("\n" + "="*60)
            self.console.print("[bold blue]📚 INTERACTIVE TUTORIALS[/bold blue]")
            self.console.print("="*60)
            
            tutorials = [
                "1. 🌟 Beginner's Guide to Network Security",
                "2. 🔍 Network Discovery Fundamentals",
                "3. 🎯 ARP Spoofing Explained",
                "4. 📡 Packet Sniffing Guide",
                "5. 🛡️ Security Best Practices",
                "6. 🔧 Attack Mitigation Techniques",
                "7. 🎓 Advanced Topics",
                "8. ❌ Back to Main Menu"
            ]
            
            for tutorial in tutorials:
                self.console.print(tutorial)
            
            choice = Prompt.ask("\nSelect a tutorial", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                self._run_tutorial("beginner_guide")
            elif choice == "2":
                self._run_tutorial("network_discovery")
            elif choice == "3":
                self._run_tutorial("arp_spoofing")
            elif choice == "4":
                self._run_tutorial("packet_sniffing")
            elif choice == "5":
                self._run_tutorial("security_best_practices")
            elif choice == "6":
                self._run_tutorial("attack_mitigation")
            elif choice == "7":
                self._show_advanced_topics()
            elif choice == "8":
                break
    
    def _run_tutorial(self, tutorial_name: str):
        """Run a specific tutorial."""
        if tutorial_name not in self.tutorials:
            self.console.print(f"[red]Tutorial '{tutorial_name}' not found.[/red]")
            return
        
        tutorial_steps = self.tutorials[tutorial_name]
        
        self.console.print(f"\n[bold green]📚 Starting Tutorial: {tutorial_name.replace('_', ' ').title()}[/bold green]")
        
        for i, step in enumerate(tutorial_steps, 1):
            self._display_tutorial_step(step, i, len(tutorial_steps))
            
            if step.interactive and step.question:
                self._handle_interactive_step(step)
            
            if i < len(tutorial_steps):
                if not Confirm.ask("\nContinue to next step?"):
                    break
        
        self.console.print(f"\n[green]✅ Tutorial '{tutorial_name.replace('_', ' ').title()}' completed![/green]")
    
    def _display_tutorial_step(self, step: TutorialStep, step_num: int, total_steps: int):
        """Display a single tutorial step."""
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(Panel(f"Step {step_num} of {total_steps}", style="bold blue"), size=3),
            Layout(Panel(step.content, title=step.title, border_style="green"), size=10),
            Layout()
        )
        
        if step.code_example:
            code_panel = Panel(
                step.code_example,
                title="Code Example",
                border_style="yellow"
            )
            layout[2] = code_panel
        
        self.console.print(layout)
    
    def _handle_interactive_step(self, step: TutorialStep):
        """Handle interactive tutorial steps."""
        if step.question:
            answer = Prompt.ask(step.question)
            if step.correct_answer:
                if answer.lower() == step.correct_answer.lower():
                    self.console.print("[green]✅ Correct![/green]")
                else:
                    self.console.print(f"[red]❌ Incorrect. The correct answer is: {step.correct_answer}[/red]")
    
    def _get_beginner_guide_tutorial(self) -> List[TutorialStep]:
        """Beginner's guide to network security."""
        return [
            TutorialStep(
                title="What is Network Security?",
                content="""
Network security is the practice of protecting computer networks from unauthorized access, 
misuse, or attacks. It involves implementing various security measures to ensure the 
confidentiality, integrity, and availability of network resources.

Key Concepts:
• Confidentiality: Ensuring data is only accessible to authorized users
• Integrity: Ensuring data hasn't been tampered with
• Availability: Ensuring network resources are accessible when needed
                """,
                interactive=True,
                question="What are the three main principles of network security?",
                correct_answer="Confidentiality, Integrity, Availability"
            ),
            TutorialStep(
                title="Common Network Attacks",
                content="""
Understanding common attack types helps in both defense and ethical testing:

1. ARP Spoofing: Redirecting traffic by falsifying ARP responses
2. Man-in-the-Middle: Intercepting and potentially modifying communications
3. Packet Sniffing: Capturing and analyzing network traffic
4. DoS/DDoS: Denial of Service attacks to make services unavailable
5. Port Scanning: Discovering open ports and services

Each attack has different purposes and requires different defense strategies.
                """,
                interactive=True,
                question="What is the purpose of ARP spoofing?",
                correct_answer="Redirecting traffic by falsifying ARP responses"
            ),
            TutorialStep(
                title="Ethical Considerations",
                content="""
When conducting network security testing, always follow these principles:

✅ DO:
• Only test networks you own or have explicit permission to test
• Document all testing activities
• Use the minimum necessary force to achieve testing goals
• Report findings responsibly

❌ DON'T:
• Test networks without permission
• Cause damage or disruption beyond testing requirements
• Access or steal data
• Use testing tools for malicious purposes

Remember: With great power comes great responsibility!
                """
            )
        ]
    
    def _get_network_discovery_tutorial(self) -> List[TutorialStep]:
        """Network discovery tutorial."""
        return [
            TutorialStep(
                title="Understanding Network Discovery",
                content="""
Network discovery is the process of identifying active devices on a network. 
This is typically the first step in network security assessment.

Methods:
• ARP Scanning: Sends ARP requests to discover devices
• Ping Sweep: Sends ICMP echo requests
• Port Scanning: Checks for open ports on discovered devices
• Service Detection: Identifies running services

Our tool uses ARP scanning as it's fast, reliable, and non-intrusive.
                """,
                code_example="""
# ARP Scanning Example
from scapy.all import ARP, Ether, srp

# Create ARP request
arp = ARP(pdst="192.168.1.0/24")
ether = Ether(dst="ff:ff:ff:ff:ff:ff")
packet = ether/arp

# Send and receive responses
result = srp(packet, timeout=3, verbose=0)[0]
                """
            ),
            TutorialStep(
                title="Interpreting Results",
                content="""
When you scan a network, you'll get information about each discovered device:

• IP Address: The device's network identifier
• MAC Address: The device's hardware identifier
• Hostname: The device's name (if resolvable)
• Vendor: The manufacturer of the network interface
• Risk Score: Calculated based on various factors

Understanding this information helps you prioritize which devices to investigate further.
                """
            ),
            TutorialStep(
                title="Best Practices",
                content="""
For effective network discovery:

1. Start with a broad scan to get an overview
2. Focus on devices with high risk scores
3. Document all findings
4. Use multiple discovery methods for verification
5. Respect network resources and don't overwhelm the network

Remember: Discovery is just the beginning - analysis is key!
                """
            )
        ]
    
    def _get_arp_spoofing_tutorial(self) -> List[TutorialStep]:
        """ARP spoofing tutorial."""
        return [
            TutorialStep(
                title="What is ARP Spoofing?",
                content="""
ARP (Address Resolution Protocol) spoofing is a technique where an attacker sends 
falsified ARP messages to associate their MAC address with the IP address of a 
legitimate device.

How it works:
1. Attacker sends ARP response claiming to be the router
2. Target device updates its ARP table
3. Traffic intended for router goes to attacker
4. Attacker can intercept, modify, or forward traffic

This enables man-in-the-middle attacks.
                """,
                code_example="""
# ARP Spoofing Example
from scapy.all import ARP, send

# Spoof target device
arp_response = ARP(op=2, psrc="192.168.1.1", pdst="192.168.1.100")
send(arp_response, verbose=False)
                """
            ),
            TutorialStep(
                title="Detection and Prevention",
                content="""
Detecting ARP spoofing:
• Monitor ARP tables for duplicate entries
• Use ARP monitoring tools
• Watch for unusual network behavior
• Check for unexpected MAC addresses

Prevention methods:
• Static ARP entries
• ARP monitoring software
• Network segmentation
• Regular security audits
                """
            ),
            TutorialStep(
                title="Ethical Use",
                content="""
When using ARP spoofing for testing:

✅ Ethical practices:
• Only test networks you own or have permission to test
• Inform users about testing activities
• Use minimal disruption necessary
• Document all activities
• Stop immediately if issues arise

❌ Unethical practices:
• Testing without permission
• Causing service disruption
• Stealing or modifying data
• Using for malicious purposes

Always prioritize network stability and user experience!
                """
            )
        ]
    
    def _get_packet_sniffing_tutorial(self) -> List[TutorialStep]:
        """Packet sniffing tutorial."""
        return [
            TutorialStep(
                title="Understanding Packet Sniffing",
                content="""
Packet sniffing is the practice of capturing and analyzing network traffic. 
It's essential for network troubleshooting, security analysis, and learning.

Types of packets you might see:
• ARP: Address resolution protocol packets
• ICMP: Internet control message protocol (ping)
• TCP: Transmission control protocol
• UDP: User datagram protocol
• HTTP: Web traffic
• DNS: Domain name system queries

Each packet type reveals different information about network activity.
                """,
                code_example="""
# Packet Sniffing Example
from scapy.all import sniff

def packet_callback(packet):
    if IP in packet:
        print(f"IP: {packet[IP].src} -> {packet[IP].dst}")

# Start sniffing
sniff(iface="eth0", prn=packet_callback)
                """
            ),
            TutorialStep(
                title="Analyzing Captured Packets",
                content="""
When analyzing captured packets, look for:

1. Source and destination IPs
2. Protocol types
3. Port numbers
4. Data payloads (if not encrypted)
5. Timing patterns
6. Unusual traffic patterns

Common patterns to watch for:
• Repeated connection attempts (possible scanning)
• Large data transfers (possible data exfiltration)
• Unusual protocols or ports
• Traffic to suspicious destinations
                """
            ),
            TutorialStep(
                title="Legal and Ethical Considerations",
                content="""
Packet sniffing has legal implications:

Legal considerations:
• Only capture traffic you have permission to monitor
• Respect privacy laws and regulations
• Don't capture sensitive personal information
• Follow company policies and procedures

Ethical guidelines:
• Use for legitimate security testing only
• Protect captured data appropriately
• Don't share sensitive information
• Report findings responsibly

When in doubt, get explicit permission!
                """
            )
        ]
    
    def _get_security_best_practices_tutorial(self) -> List[TutorialStep]:
        """Security best practices tutorial."""
        return [
            TutorialStep(
                title="Network Security Fundamentals",
                content="""
Effective network security requires a layered approach:

1. Network Segmentation: Divide networks into smaller, isolated segments
2. Access Control: Implement proper authentication and authorization
3. Monitoring: Continuously monitor network activity
4. Encryption: Encrypt sensitive data in transit and at rest
5. Regular Updates: Keep all systems and software updated
6. Incident Response: Have a plan for security incidents

Each layer provides additional protection and reduces overall risk.
                """
            ),
            TutorialStep(
                title="Defense Against Common Attacks",
                content="""
Protecting against the attacks we've discussed:

Against ARP Spoofing:
• Use static ARP entries for critical devices
• Implement ARP monitoring and alerting
• Use network segmentation

Against Packet Sniffing:
• Encrypt all sensitive communications
• Use secure protocols (HTTPS, SSH, VPN)
• Monitor for unauthorized sniffing

Against Man-in-the-Middle:
• Use certificate pinning
• Implement mutual authentication
• Monitor for certificate anomalies
                """
            ),
            TutorialStep(
                title="Continuous Security",
                content="""
Security is not a one-time activity but an ongoing process:

Regular activities:
• Security assessments and penetration testing
• Vulnerability scanning and patching
• Security awareness training
• Incident response drills
• Security policy reviews

Remember: Security is everyone's responsibility!
                """
            )
        ]
    
    def _get_attack_mitigation_tutorial(self) -> List[TutorialStep]:
        """Attack mitigation tutorial."""
        return [
            TutorialStep(
                title="Incident Response Process",
                content="""
When a security incident occurs, follow these steps:

1. Detection: Identify that an incident has occurred
2. Assessment: Determine the scope and impact
3. Containment: Isolate affected systems
4. Eradication: Remove the threat
5. Recovery: Restore normal operations
6. Lessons Learned: Document and improve

Speed is critical in incident response!
                """
            ),
            TutorialStep(
                title="Immediate Response Actions",
                content="""
If you detect an attack in progress:

Immediate actions:
• Disconnect affected systems from the network
• Change all passwords and access credentials
• Preserve evidence for investigation
• Notify relevant stakeholders
• Document everything

Don't panic - follow your incident response plan!
                """
            ),
            TutorialStep(
                title="Long-term Mitigation",
                content="""
After an incident, focus on prevention:

• Conduct a thorough post-incident review
• Update security policies and procedures
• Implement additional security controls
• Provide additional training
• Test your incident response plan

Use incidents as learning opportunities to improve security!
                """
            )
        ]
    
    def _show_advanced_topics(self):
        """Show advanced tutorial topics."""
        self.console.print("\n[bold green]🎓 Advanced Topics[/bold green]")
        
        advanced_topics = [
            "Advanced Persistent Threats (APTs)",
            "Zero-day Exploits",
            "Advanced Evasion Techniques",
            "Cryptographic Attacks",
            "Social Engineering",
            "Physical Security",
            "Cloud Security",
            "IoT Security"
        ]
        
        for i, topic in enumerate(advanced_topics, 1):
            self.console.print(f"{i}. {topic}")
        
        self.console.print("\n[yellow]Advanced tutorials coming soon![/yellow]")

def main():
    """Main function for tutorial system."""
    tutorial_system = TutorialSystem()
    tutorial_system.show_tutorial_menu()

if __name__ == "__main__":
    main()