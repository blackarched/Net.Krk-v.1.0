# NET.KRAK // WiFi Penetration Suite v3.0

<div align="center">

![NET.KRAK Logo](https://img.shields.io/badge/NET.KRAK-v3.0-00f3ff?style=for-the-badge&logo=wifi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-00ff9d?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-ff00ff?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-bd00ff?style=for-the-badge)

**Professional WiFi Penetration Testing Suite with Advanced 3D Visualization**

[![Dashboard Preview](https://img.shields.io/badge/Dashboard-Preview-00f3ff?style=for-the-badge)](http://localhost:5000)
[![Attack Dashboard](https://img.shields.io/badge/Attack-Dashboard-ff00ff?style=for-the-badge)](http://localhost:5000/attack)
[![Analytics Dashboard](https://img.shields.io/badge/Analytics-Dashboard-00ff9d?style=for-the-badge)](http://localhost:5000)

</div>

---

## 🎯 **Overview**

NET.KRAK v3.0 is a comprehensive WiFi penetration testing suite featuring advanced 3D network visualization, real-time scanning, and professional attack capabilities. Built with modern web technologies and designed for both desktop and mobile environments.

### ✨ **Key Features**

- 🌐 **3D Network Visualization** - Interactive Three.js network mapping
- 📡 **Real-time WiFi Scanning** - Live network discovery using `iwlist`
- ⚡ **Advanced Attack Vectors** - Deauth, Handshake, Evil Twin, WPS, and more
- 🎨 **Holographic UI** - Cyberpunk-inspired interface with neon effects
- 📱 **Mobile Optimized** - Full compatibility with Pydroid and mobile devices
- 🔒 **Professional Security** - Enterprise-grade penetration testing tools
- 📊 **Real-time Analytics** - Live statistics and network monitoring

---

## 🚀 **Quick Start Guide**

### **Prerequisites**

- Python 3.8 or higher
- Linux/Android environment (for WiFi scanning)
- WiFi interface in monitor mode (for attack capabilities)

### **Installation**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/blackarched/Net.Krk-v.1.0.git
   cd Net.Krk-v.1.0
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set WiFi Interface to Monitor Mode** (Required for attacks)
   ```bash
   sudo airmon-ng start wlan0
   # Note: Replace 'wlan0' with your WiFi interface name
   ```

---

## 🎮 **How to Run the Application**

### **Method 1: Combined Dashboard (Recommended)**

The combined dashboard provides access to both analytics and attack capabilities in a single interface.

```bash
# Navigate to the project directory
cd /path/to/Net.Krk-v.1.0

# Run the combined dashboard
python src/combined_dashboard.py
```

**Access URLs:**
- **Main Dashboard**: http://localhost:5000
- **Attack Dashboard**: http://localhost:5000/attack

### **Method 2: Separate Dashboards**

Run individual dashboard components for specific use cases.

#### **Analytics Dashboard Only**
```bash
python src/analytics_dashboard.py
```
- **URL**: http://localhost:5000
- **Purpose**: Network discovery and analysis

#### **Attack Dashboard Only**
```bash
python src/attack_dashboard.py
```
- **URL**: http://localhost:5001
- **Purpose**: Penetration testing and attack execution

---

## 📱 **Mobile Usage (Pydroid)**

### **For Android Development with Pydroid**

1. **Install Pydroid 3** from Google Play Store
2. **Install Dependencies** in Pydroid:
   ```python
   # In Pydroid terminal
   pip install flask
   ```

3. **Upload Project Files** to Pydroid workspace
4. **Run the Application**:
   ```python
   # In Pydroid
   exec(open('src/combined_dashboard.py').read())
   ```

5. **Access Dashboard**:
   - Open browser in Pydroid
   - Navigate to: `http://localhost:5000`

---

## 🎨 **Dashboard Interface Guide**

### **Main Dashboard Features**

#### **1. Network Discovery Panel**
- **WiFi Interface Input**: Enter your monitor mode interface (e.g., `wlan0mon`)
- **SCAN NETWORKS Button**: Initiates real-time WiFi scanning
- **STATUS Button**: Shows system status and statistics
- **Network List**: Displays discovered networks with details

#### **2. Target Analysis Panel**
- **Target Selection**: Click on discovered networks to select targets
- **Attack Vectors**: Choose from available attack methods:
  - 🔴 **Deauthentication Attack**
  - 🔵 **Handshake Capture**
  - 🟡 **Evil Twin**
  - 🟢 **Credential Capture**
  - 🟣 **WPS Attack**
  - 🟠 **Fragmentation Attack**

#### **3. Attack Execution Panel**
- **EXECUTE ATTACK Button**: Launches selected attack vectors
- **STOP ALL Button**: Immediately stops all active attacks
- **Attack Status**: Real-time attack progress and results

#### **4. Activity Log Panel**
- **Real-time Logging**: Live operation monitoring
- **Color-coded Messages**: Different log types (info, success, error, attack)
- **Scrollable History**: Complete operation history

#### **5. Interface Configuration Panel**
- **WiFi Interface**: Set your monitor mode interface
- **System Status**: Real-time system monitoring
- **Configuration Options**: Advanced settings and preferences

### **3D Network Visualization**

The dashboard includes an advanced 3D network map featuring:
- **Interactive 3D Nodes**: Representing discovered devices
- **Signal Visualization**: Color-coded signal strength
- **Network Topology**: Dynamic connection mapping
- **Real-time Updates**: Live network changes
- **Camera Controls**: Zoom, pan, and rotate
- **Device Information**: Hover for detailed device data

---

## 🔧 **API Endpoints**

### **Network Scanning**
```http
GET /api/scan
```
**Response:**
```json
{
  "status": "success",
  "networks": [
    {
      "ssid": "WiFiNetwork",
      "bssid": "00:11:22:33:44:55",
      "channel": 6,
      "security": "WPA2",
      "signal": -45,
      "quality": "Excellent"
    }
  ]
}
```

### **System Statistics**
```http
GET /api/stats
```
**Response:**
```json
{
  "total_networks": 15,
  "hidden_networks": 3,
  "open_networks": 2,
  "secured_networks": 10,
  "strongest_signal": -30,
  "scan_time": "14:30:25",
  "is_scanning": false
}
```

### **Attack Execution**
```http
POST /api/execute-attack
Content-Type: application/json

{
  "attack_type": "deauth",
  "target": {
    "ssid": "TargetNetwork",
    "bssid": "00:11:22:33:44:55"
  }
}
```

### **Target Selection**
```http
GET /api/targets
```
**Response:**
```json
{
  "status": "success",
  "targets": [
    {
      "ssid": "TargetNetwork",
      "bssid": "00:11:22:33:44:55",
      "channel": 6,
      "security": "WPA2",
      "signal": -45
    }
  ]
}
```

### **Attack Statistics**
```http
GET /api/attack-stats
```
**Response:**
```json
{
  "total_attacks": 5,
  "successful_attacks": 3,
  "active_attacks": 1,
  "attack_types": ["deauth", "handshake"]
}
```

---

## 🎯 **Usage Instructions**

### **Step 1: Initial Setup**
1. **Start the Application**:
   ```bash
   python src/combined_dashboard.py
   ```

2. **Open Your Browser**:
   - Navigate to: `http://localhost:5000`
   - You'll see the main dashboard interface

### **Step 2: Configure WiFi Interface**
1. **Enter Interface Name**:
   - In the "Interface Config" panel
   - Enter your monitor mode interface (e.g., `wlan0mon`)
   - Click "STATUS" to verify system status

### **Step 3: Discover Networks**
1. **Click "SCAN NETWORKS"**:
   - The system will scan for available WiFi networks
   - Networks will appear in the "Network Discovery" panel
   - Each network shows SSID, BSSID, channel, security, and signal strength

### **Step 4: Select Target**
1. **Click on a Network**:
   - Select your target network from the discovered list
   - Target details will appear in the "Target Analysis" panel
   - Verify target information is correct

### **Step 5: Choose Attack Vectors**
1. **Select Attack Methods**:
   - Click on desired attack vectors in the "Target Analysis" panel
   - Active vectors will be highlighted
   - Choose multiple vectors for comprehensive testing

### **Step 6: Execute Attack**
1. **Click "EXECUTE ATTACK"**:
   - A confirmation dialog will appear
   - Review target and attack vectors
   - Click "CONFIRM" to proceed
   - Monitor progress in the "Activity Log" panel

### **Step 7: Monitor Results**
1. **Watch Activity Log**:
   - Real-time attack progress and results
   - Success/failure notifications
   - Detailed error messages if issues occur

---

## 🔒 **Security and Legal Notice**

### **⚠️ IMPORTANT DISCLAIMER**

This tool is designed for **authorized penetration testing only**. Users must:

- ✅ **Only test networks they own or have explicit permission to test**
- ✅ **Comply with all local laws and regulations**
- ✅ **Use responsibly and ethically**
- ❌ **Never use for malicious purposes**
- ❌ **Never test networks without permission**

### **Legal Requirements**

- **Authorization Required**: Only test networks you own or have written permission
- **Local Laws**: Ensure compliance with your jurisdiction's laws
- **Ethical Use**: Use for legitimate security testing purposes only
- **Professional Responsibility**: Use your professional judgment and ethics

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **"No networks found" Error**
- **Solution**: Ensure WiFi interface is in monitor mode
- **Command**: `sudo airmon-ng start wlan0`

#### **"Permission denied" Error**
- **Solution**: Run with appropriate permissions
- **Command**: `sudo python src/combined_dashboard.py`

#### **"Interface not found" Error**
- **Solution**: Check interface name and availability
- **Command**: `iwconfig` or `ip link show`

#### **Mobile/Pydroid Issues**
- **Solution**: Ensure all dependencies are installed
- **Check**: Python version compatibility
- **Verify**: File permissions and paths

### **Performance Optimization**

- **Close Unused Applications**: Free up system resources
- **Use Wired Connection**: For stable network access
- **Monitor System Resources**: Check CPU and memory usage
- **Update Dependencies**: Keep packages current

---

## 📊 **Technical Specifications**

### **System Requirements**
- **OS**: Linux (Ubuntu/Debian recommended)
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB free space
- **Network**: WiFi interface with monitor mode support

### **Dependencies**
- **Flask**: Web framework
- **Scapy**: Network packet manipulation
- **Three.js**: 3D visualization (CDN)
- **Chart.js**: Data visualization (CDN)

### **Supported Attack Vectors**
- **Deauthentication**: Disconnect clients from networks
- **Handshake Capture**: Capture WPA/WPA2 handshakes
- **Evil Twin**: Create fake access points
- **Credential Harvesting**: Capture login credentials
- **WPS Attacks**: Exploit WPS vulnerabilities
- **Fragmentation**: Exploit fragmentation vulnerabilities

---

## 🤝 **Support and Contributing**

### **Getting Help**
- **Issues**: Report bugs and request features on GitHub
- **Documentation**: Check this README for common solutions
- **Community**: Join discussions in the project repository

### **Contributing**
1. **Fork the Repository**
2. **Create Feature Branch**
3. **Make Changes**
4. **Test Thoroughly**
5. **Submit Pull Request**

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 **Acknowledgments**

- **Three.js Community** for 3D visualization capabilities
- **Flask Team** for the excellent web framework
- **Security Community** for continuous improvement and feedback

---

<div align="center">

**NET.KRAK v3.0 - Professional WiFi Penetration Testing Suite**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-00f3ff?style=for-the-badge&logo=github)](https://github.com/blackarched/Net.Krk-v.1.0)
[![Issues](https://img.shields.io/badge/Issues-Report-ff00ff?style=for-the-badge&logo=github)](https://github.com/blackarched/Net.Krk-v.1.0/issues)
[![License](https://img.shields.io/badge/License-MIT-00ff9d?style=for-the-badge)](LICENSE)

**Built with ❤️ for the Security Community**

</div>