# net.krak v2.0 - WiFi Penetration Testing Suite

A comprehensive, hardened WiFi penetration testing suite with enhanced attack vectors, improved performance, and a modern web-based dashboard.

## 🚀 Features

### Enhanced Attack Vectors
- **Deauthentication Attacks** - Forcefully disconnect clients from target APs
- **Handshake Capture** - Capture WPA/WPA2 handshakes for offline cracking
- **Evil Twin AP** - Create rogue access points to trick clients
- **Credential Capture** - Monitor and capture login credentials
- **WPS PIN Attacks** - Brute force WPS PINs using reaver/bully
- **Fragmentation Attacks** - Exploit fragmentation vulnerabilities

### Advanced Scanning
- **Multi-method Scanning** - Scapy and airodump-ng support
- **Real-time Network Discovery** - Live network monitoring
- **Client Detection** - Identify connected devices
- **Signal Strength Analysis** - RSSI monitoring and analysis
- **Security Protocol Detection** - WEP, WPA, WPA2, WPA3 identification

### Modern Dashboard
- **Holographic UI** - Futuristic, responsive web interface
- **Real-time Monitoring** - Live status updates and activity logs
- **Attack Management** - Visual attack vector selection and execution
- **System Status** - Comprehensive system health monitoring
- **Mobile Responsive** - Works on desktop and mobile devices

### Enhanced Security
- **Authorization Checks** - Legal compliance and safety measures
- **Process Management** - Secure process isolation and cleanup
- **Input Validation** - Comprehensive parameter validation
- **Error Handling** - Robust error handling and recovery
- **Audit Logging** - Detailed JSON-structured logging

## 📋 Requirements

### System Requirements
- Linux (Ubuntu 20.04+ recommended)
- Python 3.7+
- 2GB+ RAM
- 1GB+ free disk space
- 2+ CPU cores
- Root privileges for network operations

### Hardware Requirements
- WiFi adapter supporting monitor mode
- Compatible wireless drivers
- Sufficient antenna range for target networks

### Software Dependencies
- aircrack-ng suite
- reaver (for WPS attacks)
- bully (alternative WPS tool)
- iw (wireless tools)
- net-tools
- Docker (optional)

## 🛠️ Installation

> **📋 Installation Matrix**: For detailed installation instructions across different environments, see [INSTALLATION_MATRIX.md](INSTALLATION_MATRIX.md)

### Quick Start (Docker)

#### Docker Compose (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd net.krak

# Build and run with Docker Compose
sudo docker-compose up -d

# Access the dashboard
open http://localhost:5000
```

#### Docker Run (Manual)
For full functionality, use these specific flags:
```bash
# Full functionality with all capabilities
docker run -it --rm \
  --cap-add=NET_ADMIN --cap-add=NET_RAW \
  --device /dev/net/tun \
  --network host \
  -v /path/to/captures:/app/captures \
  -v /var/run/dbus:/var/run/dbus \
  --name netkrak netkrak:latest

# Alternative without --network host (limited functionality)
docker run -it --rm \
  --cap-add=NET_ADMIN --cap-add=NET_RAW \
  --device /dev/net/tun \
  -v /path/to/captures:/app/captures \
  -v /var/run/dbus:/var/run/dbus \
  --name netkrak netkrak:latest
```

**Important Docker Flags Explained:**
- `--cap-add=NET_ADMIN --cap-add=NET_RAW`: Required for wireless interface management and packet capture
- `--device /dev/net/tun`: Access to TUN/TAP devices for network operations
- `--network host`: **Required for many wireless operations** - allows container to see host network interfaces
- `-v /path/to/captures:/app/captures`: Persistent storage for captured handshakes and data
- `-v /var/run/dbus:/var/run/dbus`: Access to system D-Bus for hardware management

**Why --network host is required:**
The `--network host` flag is essential for wireless penetration testing because:
- Wireless interfaces (wlan0, wlan0mon) are typically only visible on the host network
- Many wireless tools (airodump-ng, aircrack-ng) require direct access to physical interfaces
- Monitor mode operations need raw access to the host's network stack
- If you must avoid `--network host`, you'll need to manually map hardware interfaces using `--device` flags

### Manual Installation
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y aircrack-ng reaver bully iw net-tools

# Install Python dependencies
pip install -r requirements.txt

# Run the application
sudo python3 dashboard_api.py
```

### Desktop Shortcuts
```bash
# Install desktop shortcuts
./setup_desktop.sh

# Or run manually
./start_netkrak.sh    # Start the suite
./stop_netkrak.sh     # Stop the suite
```

## 🎯 Usage

### Web Dashboard
1. Open your browser to `http://localhost:5000`
2. Enter your WiFi interface (e.g., `wlan0mon`)
3. Click "SCAN NETWORKS" to discover targets
4. Select a target network
5. Choose attack vectors
6. Click "EXECUTE ATTACK" and confirm

### Command Line Interface
```bash
# Run system diagnostics (NEW!)
sudo python3 orchestrator.py diagnostics

# List available interfaces
sudo python3 orchestrator.py list-interfaces

# Scan for networks
sudo python3 orchestrator.py scan wlan0mon --scan-time 30

# Execute attacks
sudo python3 orchestrator.py attack wlan0mon \
    --bssid "00:11:22:33:44:55" \
    --ssid "TargetNetwork" \
    --channel 6 \
    --attack-type deauth \
    --authorized

# Get system status
sudo python3 orchestrator.py status

# Clean up processes
sudo python3 orchestrator.py cleanup
```

### API Endpoints
```bash
# System information
curl http://localhost:5000/system/info

# Scan networks
curl "http://localhost:5000/scan?interface=wlan0mon&scan_time=15"

# Execute attack
curl -X POST http://localhost:5000/attack \
    -H "Content-Type: application/json" \
    -d '{"interface":"wlan0mon","bssid":"00:11:22:33:44:55","ssid":"Target","attack_type":"deauth"}'

# Stop attacks
curl -X POST http://localhost:5000/attack/stop

# Get logs
curl http://localhost:5000/logs
```

## 🔧 Configuration

### Environment Variables
```bash
export NETKRAK_LOG_FILE="/path/to/logs/netkrak.jsonlog"
export PYTHONPATH="/path/to/netkrak"
```

### Configuration File
Create `.netkrak_config.json`:
```json
{
  "max_scan_time": 300,
  "max_attack_duration": 3600,
  "auto_cleanup": true,
  "log_level": "INFO",
  "safety_checks": true
}
```

## 🧪 Testing

### Run Test Suite
```bash
# Run comprehensive tests
python3 test_comprehensive.py

# Run specific test modules
python3 -m unittest test_attacks.py
python3 -m unittest test_scanner.py
python3 -m unittest test_orchestrator.py
```

### Performance Optimization
```bash
# Run system optimization
python3 optimize.py

# Benchmark performance
python3 -c "from optimize import NetKrakOptimizer; NetKrakOptimizer().benchmark_performance()"
```

## 📊 Monitoring

### Real-time Monitoring
The dashboard provides real-time monitoring of:
- Network discovery status
- Active attack processes
- System resource usage
- Error logs and warnings
- Performance metrics

### Log Analysis
Logs are stored in JSON format for easy analysis:
```bash
# View recent logs
tail -f logs/netkrak.jsonlog | jq .

# Filter by event type
grep "attack_start" logs/netkrak.jsonlog | jq .
```

## 🛡️ Security & Legal

### Legal Compliance
- **Authorization Required** - All attacks require explicit authorization
- **Target Confirmation** - Interactive confirmation for attack targets
- **Audit Logging** - Comprehensive logging of all activities
- **Safety Checks** - Built-in safety measures and warnings

### Security Features
- **Process Isolation** - Attacks run in isolated processes
- **Input Validation** - Comprehensive parameter validation
- **Error Handling** - Secure error handling and recovery
- **Resource Limits** - Memory and CPU usage limits

## 🔍 Troubleshooting

### Common Issues

#### Interface Not Found
```bash
# Check available interfaces
iwconfig
ip link show

# Set interface to monitor mode
sudo airmon-ng start wlan0
```

#### Permission Denied
```bash
# Ensure running as root
sudo python3 dashboard_api.py

# Check capabilities
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/python3
```

#### No Networks Found
```bash
# Verify monitor mode
iwconfig wlan0mon

# Check interface status
ip link show wlan0mon

# Test with airodump-ng
sudo airodump-ng wlan0mon
```

### Performance Issues
```bash
# Run optimization
python3 optimize.py

# Check system resources
htop
iostat -x 1

# Monitor network usage
iftop -i wlan0mon
```

## 📈 Performance

### Optimization Features
- **Multi-threading** - Parallel processing for better performance
- **Memory Management** - Efficient memory usage and garbage collection
- **Process Pooling** - Reusable process pools for external tools
- **Caching** - Intelligent caching of scan results
- **Resource Limits** - Configurable resource usage limits

### Benchmarks
Typical performance on modern hardware:
- Network scan: 15-30 seconds for 50+ networks
- Attack execution: <1 second startup time
- Memory usage: 50-200MB depending on activity
- CPU usage: 10-50% during active scanning

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python3 test_comprehensive.py

# Format code
black *.py

# Lint code
flake8 *.py
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document all public functions
- Write comprehensive tests
- Use meaningful variable names

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and authorized testing purposes only. Users are responsible for ensuring they have proper authorization before testing any networks. The authors are not responsible for any misuse of this software.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the test suite for examples
- Examine the log files for error details
- Ensure all dependencies are properly installed

## 🔄 Changelog

### v2.0.0
- Complete rewrite with enhanced security
- New attack vectors (WPS, fragmentation)
- Modern holographic dashboard
- Improved performance and reliability
- Comprehensive test suite
- Desktop shortcut integration
- Real-time monitoring system

### v1.0.0
- Initial release
- Basic attack vectors
- Simple web interface
- Command-line interface