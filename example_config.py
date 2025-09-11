#!/usr/bin/env python3
"""
Example Configuration for Network Scanner
=========================================

This file shows how to configure the network scanner for different scenarios.
Copy the relevant configuration to the main script before running.
"""

# Example Configuration 1: Home Network (192.168.1.x)
HOME_NETWORK_CONFIG = {
    "ip_range": "192.168.1.0/24",
    "router_ip": "192.168.1.1",
    "router_mac": "aa:bb:cc:dd:ee:ff",  # Replace with actual router MAC
    "attacker_ip": "192.168.1.100",     # Your machine's IP
    "interface": "eth0"                  # Your network interface
}

# Example Configuration 2: Office Network (10.0.0.x)
OFFICE_NETWORK_CONFIG = {
    "ip_range": "10.0.0.0/24",
    "router_ip": "10.0.0.1",
    "router_mac": "11:22:33:44:55:66",  # Replace with actual router MAC
    "attacker_ip": "10.0.0.50",         # Your machine's IP
    "interface": "enp0s3"                # Your network interface
}

# Example Configuration 3: Lab Network (172.16.0.x)
LAB_NETWORK_CONFIG = {
    "ip_range": "172.16.0.0/24",
    "router_ip": "172.16.0.1",
    "router_mac": "77:88:99:aa:bb:cc",  # Replace with actual router MAC
    "attacker_ip": "172.16.0.10",       # Your machine's IP
    "interface": "wlan0"                 # Your network interface
}

def get_network_info():
    """
    Helper function to automatically detect network configuration.
    Run this to get your current network settings.
    """
    import subprocess
    import re
    
    try:
        # Get default gateway
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True)
        gateway_line = result.stdout.split('\n')[0]
        gateway_ip = gateway_line.split()[2]
        
        # Get network interface
        interface = gateway_line.split()[4]
        
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
        
        print("Detected Network Configuration:")
        print(f"  Network Range: {network_range}")
        print(f"  Gateway IP: {gateway_ip}")
        print(f"  Your IP: {local_ip}")
        print(f"  Interface: {interface}")
        print(f"  Router MAC: Run 'arp -a | grep {gateway_ip}' to find this")
        
        return {
            "ip_range": network_range,
            "router_ip": gateway_ip,
            "router_mac": "REPLACE_WITH_ACTUAL_MAC",
            "attacker_ip": local_ip,
            "interface": interface
        }
        
    except Exception as e:
        print(f"Error detecting network info: {e}")
        return None

if __name__ == "__main__":
    print("Network Scanner Configuration Helper")
    print("=" * 40)
    config = get_network_info()
    
    if config:
        print("\nCopy this configuration to your main script:")
        print("=" * 40)
        for key, value in config.items():
            print(f'{key} = "{value}"')