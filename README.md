# Network Scanner and ARP Spoofing Tool

A comprehensive Python tool for network analysis, device discovery, ARP spoofing, and packet sniffing. This tool is designed for educational purposes and authorized network testing.

## ⚠️ WARNING

**This tool is for educational and authorized testing purposes only.**
- Only use on networks you own or have explicit written permission to test
- Unauthorized use may violate laws and terms of service
- The authors are not responsible for any misuse of this tool

## Features

- **Network Discovery**: Scan local networks to find active devices using ARP requests
- **Device Information**: Gather hostname and MAC vendor information for discovered devices
- **ARP Spoofing**: Perform ARP spoofing attacks for network control and analysis
- **Packet Sniffing**: Real-time packet capture and analysis
- **Comprehensive Logging**: Detailed logging of all activities
- **Interactive Interface**: User-friendly command-line interface
- **Threading Support**: Non-blocking operations for concurrent tasks

## Prerequisites

### System Requirements
- Linux operating system (recommended)
- Python 3.7 or higher
- Root/administrator privileges (required for raw socket operations)

### System Dependencies
Install the following system packages:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev libpcap-dev tcpdump net-tools

# CentOS/RHEL/Fedora
sudo yum install python3-devel libpcap-devel tcpdump net-tools
# or for newer versions:
sudo dnf install python3-devel libpcap-devel tcpdump net-tools

# Arch Linux
sudo pacman -S python libpcap tcpdump net-tools
```

## Installation

1. **Clone or download the repository:**
   ```bash
   git clone <repository-url>
   cd network-scanner
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Make the script executable:**
   ```bash
   chmod +x network_scanner.py
   ```

## Configuration

Before running the tool, you must configure the network parameters in the `main()` function:

```python
# Configuration - MODIFY THESE VALUES FOR YOUR NETWORK
ip_range = "192.168.1.0/24"        # Your network range
router_ip = "192.168.1.1"          # Your router's IP address
router_mac = "00:00:00:00:00:00"   # Your router's MAC address
attacker_ip = "192.168.1.2"        # Your machine's IP address
interface = "eth0"                  # Your network interface
```

### Finding Your Network Configuration

1. **Find your network interface:**
   ```bash
   ip link show
   # or
   ifconfig
   ```

2. **Find your IP range:**
   ```bash
   ip route show
   # Look for your local network (e.g., 192.168.1.0/24)
   ```

3. **Find your router's IP and MAC:**
   ```bash
   ip route | grep default
   # Then ping the router and check ARP table:
   ping <router_ip>
   arp -a | grep <router_ip>
   ```

## Usage

### Basic Usage

Run the script with root privileges:

```bash
sudo python3 network_scanner.py
```

### Interactive Commands

Once the tool starts, you'll see an interactive menu:

1. **Enter IP address**: Start ARP spoofing and packet sniffing for a specific device
2. **Enter 'scan'**: Rescan the network for devices
3. **Enter 'list'**: Display the current list of discovered devices
4. **Enter 'exit'**: Quit the program

### Example Session

```
============================================================
NETWORK SCANNER AND ARP SPOOFING TOOL
============================================================
WARNING: This tool is for educational purposes only!
Only use on networks you own or have permission to test.
============================================================
Scanning network...
Found 5 active devices

================================================================================
DISCOVERED DEVICES
================================================================================
IP Address       MAC Address         Hostname             Vendor                   
--------------------------------------------------------------------------------
192.168.1.1      aa:bb:cc:dd:ee:ff   router.local         Cisco Systems, Inc.      
192.168.1.2      ff:ee:dd:cc:bb:aa   laptop.local         Apple, Inc.              
192.168.1.3      11:22:33:44:55:66   phone.local          Samsung Electronics Co.  
192.168.1.4      77:88:99:aa:bb:cc   desktop.local        Intel Corporate          
192.168.1.5      dd:ee:ff:00:11:22   tablet.local         Amazon Technologies Inc. 
================================================================================

============================================================
CONTROL OPTIONS:
1. Enter IP address to control (ARP spoof + sniff)
2. Enter 'scan' to rescan network
3. Enter 'list' to show devices again
4. Enter 'exit' to quit
============================================================

Enter your choice: 192.168.1.3

Controlling 192.168.1.3...
Starting ARP spoofing and packet sniffing...
Press Ctrl+C to stop and return to menu
IP Packet: 192.168.1.3 -> 8.8.8.8 (Protocol: 1)
ARP Packet: 192.168.1.1 -> 192.168.1.3 (Op: 2)
```

## Features Explained

### Network Scanning
- Uses ARP requests to discover active devices on the network
- Provides IP address, MAC address, hostname, and vendor information
- Non-intrusive scanning method

### ARP Spoofing
- Performs man-in-the-middle attacks by spoofing ARP responses
- Redirects traffic between target and gateway through your machine
- Enables traffic interception and analysis

### Packet Sniffing
- Captures and displays network packets in real-time
- Shows IP and ARP packet information
- Useful for network analysis and monitoring

### Logging
- All activities are logged to `network_scan.log`
- Includes timestamps and detailed information
- Useful for analysis and debugging

## Troubleshooting

### Common Issues

1. **Permission Denied Error:**
   ```bash
   # Solution: Run with sudo
   sudo python3 network_scanner.py
   ```

2. **No Devices Found:**
   - Check your network configuration
   - Ensure you're on the correct network
   - Verify the IP range is correct

3. **Interface Not Found:**
   - Check available interfaces: `ip link show`
   - Update the interface parameter in the script

4. **Import Errors:**
   - Install missing dependencies: `pip3 install -r requirements.txt`
   - Install system dependencies (see Prerequisites)

### Debug Mode

Enable verbose logging by modifying the logging level:

```python
logging.basicConfig(
    filename='network_scan.log', 
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Legal and Ethical Considerations

- **Authorization**: Only use on networks you own or have explicit permission to test
- **Legal Compliance**: Ensure compliance with local laws and regulations
- **Ethical Use**: Use responsibly and for legitimate purposes only
- **Documentation**: Keep records of authorized testing activities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes only. Use at your own risk and ensure compliance with applicable laws and regulations.

## Disclaimer

The authors and contributors of this tool are not responsible for any misuse, damage, or legal issues arising from the use of this software. Users are solely responsible for ensuring they have proper authorization before using this tool on any network.