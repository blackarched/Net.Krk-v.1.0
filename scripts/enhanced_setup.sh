#!/bin/bash

# Enhanced Network Scanner Setup Script
# =====================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script needs to be run with sudo privileges"
        echo "Usage: sudo ./enhanced_setup.sh"
        exit 1
    fi
}

# Check system requirements
check_system() {
    print_header "Checking System Requirements"
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Linux system detected ✓"
    else
        print_error "This script is designed for Linux systems"
        exit 1
    fi
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_status "Python $PYTHON_VERSION found ✓"
        
        # Check if version is 3.7+
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 7) else 1)'; then
            print_status "Python version is compatible ✓"
        else
            print_error "Python 3.7 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check for pip
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found ✓"
    else
        print_warning "pip3 not found, installing..."
        apt-get update
        apt-get install -y python3-pip
    fi
}

# Install system dependencies
install_system_deps() {
    print_header "Installing System Dependencies"
    
    print_status "Updating package lists..."
    apt-get update
    
    print_status "Installing core networking tools..."
    apt-get install -y \
        python3-dev \
        libpcap-dev \
        tcpdump \
        net-tools \
        iputils-ping \
        nmap \
        netcat-openbsd \
        wireshark-common \
        tshark
    
    print_status "Installing additional utilities..."
    apt-get install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        tree \
        jq
    
    print_status "System dependencies installed ✓"
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    print_status "Upgrading pip..."
    pip3 install --upgrade pip
    
    print_status "Installing core Python packages..."
    pip3 install -r enhanced_requirements.txt
    
    print_status "Installing additional packages for enhanced features..."
    pip3 install \
        colorama \
        psutil \
        netifaces \
        python-nmap \
        pandas \
        matplotlib \
        pyyaml \
        loguru
    
    print_status "Python dependencies installed ✓"
}

# Configure system settings
configure_system() {
    print_header "Configuring System Settings"
    
    # Enable IP forwarding (needed for some attacks)
    print_status "Enabling IP forwarding..."
    echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
    sysctl -p
    
    # Set up proper permissions
    print_status "Setting up permissions..."
    chmod +x enhanced_network_scanner.py
    chmod +x tutorial_system.py
    chmod +x real_time_monitor.py
    
    # Create log directory
    print_status "Creating log directory..."
    mkdir -p /var/log/network_scanner
    chmod 755 /var/log/network_scanner
    
    # Create configuration directory
    print_status "Creating configuration directory..."
    mkdir -p /etc/network_scanner
    chmod 755 /etc/network_scanner
    
    print_status "System configuration completed ✓"
}

# Create desktop shortcuts
create_shortcuts() {
    print_header "Creating Desktop Shortcuts"
    
    # Create desktop entry for enhanced scanner
    cat > /usr/share/applications/enhanced-network-scanner.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Enhanced Network Scanner
Comment=User-friendly network security testing tool
Exec=sudo python3 /workspace/enhanced_network_scanner.py
Icon=applications-internet
Terminal=true
Categories=Network;Security;
Keywords=network;security;scanner;penetration;testing;
EOF
    
    # Create desktop entry for tutorial system
    cat > /usr/share/applications/network-tutorials.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Network Security Tutorials
Comment=Interactive tutorials for network security
Exec=python3 /workspace/tutorial_system.py
Icon=applications-education
Terminal=true
Categories=Education;Network;Security;
Keywords=tutorial;education;network;security;
EOF
    
    chmod +x /usr/share/applications/enhanced-network-scanner.desktop
    chmod +x /usr/share/applications/network-tutorials.desktop
    
    print_status "Desktop shortcuts created ✓"
}

# Create configuration files
create_configs() {
    print_header "Creating Configuration Files"
    
    # Create main configuration file
    cat > /etc/network_scanner/config.yaml << EOF
# Enhanced Network Scanner Configuration
# =====================================

# Network Settings
network:
  auto_detect: true
  default_interface: "eth0"
  scan_timeout: 3
  max_retries: 3

# UI Settings
ui:
  theme: "default"
  refresh_rate: 2
  show_progress: true
  verbose_logging: false

# Security Settings
security:
  require_confirmation: true
  log_all_activities: true
  max_concurrent_attacks: 3
  rate_limit: true

# Monitoring Settings
monitoring:
  real_time_updates: true
  save_session_data: true
  analytics_enabled: true
  export_format: "json"
EOF
    
    # Create log rotation configuration
    cat > /etc/logrotate.d/network_scanner << EOF
/var/log/network_scanner/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
    
    print_status "Configuration files created ✓"
}

# Run system tests
run_tests() {
    print_header "Running System Tests"
    
    print_status "Testing Python imports..."
    python3 -c "
import sys
try:
    from scapy.all import *
    from rich.console import Console
    from rich.panel import Panel
    import requests
    import psutil
    print('✓ All Python imports successful')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    print_status "Testing network tools..."
    if command -v tcpdump &> /dev/null; then
        print_status "✓ tcpdump available"
    else
        print_warning "tcpdump not available"
    fi
    
    if command -v nmap &> /dev/null; then
        print_status "✓ nmap available"
    else
        print_warning "nmap not available"
    fi
    
    print_status "Testing file permissions..."
    if [ -x enhanced_network_scanner.py ]; then
        print_status "✓ Enhanced scanner executable"
    else
        print_error "Enhanced scanner not executable"
    fi
    
    print_status "System tests completed ✓"
}

# Display completion message
show_completion() {
    print_header "Installation Complete!"
    
    echo -e "${GREEN}🎉 Enhanced Network Scanner has been successfully installed!${NC}"
    echo ""
    echo -e "${CYAN}📋 What's been installed:${NC}"
    echo "  • Enhanced Network Scanner with user-friendly interface"
    echo "  • Interactive Tutorial System"
    echo "  • Real-time Monitoring Dashboard"
    echo "  • All required dependencies and tools"
    echo "  • Desktop shortcuts and configuration files"
    echo ""
    echo -e "${CYAN}🚀 How to get started:${NC}"
    echo "  1. Run the enhanced scanner:"
    echo "     ${YELLOW}sudo python3 enhanced_network_scanner.py${NC}"
    echo ""
    echo "  2. Access tutorials:"
    echo "     ${YELLOW}python3 tutorial_system.py${NC}"
    echo ""
    echo "  3. View real-time monitoring:"
    echo "     ${YELLOW}python3 real_time_monitor.py${NC}"
    echo ""
    echo -e "${CYAN}📚 Documentation:${NC}"
    echo "  • README.md - Complete usage guide"
    echo "  • Interactive tutorials - Built-in learning system"
    echo "  • Desktop shortcuts - Easy access from applications menu"
    echo ""
    echo -e "${RED}⚠️  IMPORTANT REMINDERS:${NC}"
    echo "  • Only use on networks you own or have permission to test"
    echo "  • Always follow ethical guidelines and local laws"
    echo "  • Keep your system updated for security"
    echo ""
    echo -e "${GREEN}Happy network testing! 🔍${NC}"
}

# Main execution
main() {
    print_header "Enhanced Network Scanner Setup"
    echo -e "${PURPLE}Setting up the most user-friendly network security testing tool!${NC}"
    echo ""
    
    check_root
    check_system
    install_system_deps
    install_python_deps
    configure_system
    create_shortcuts
    create_configs
    run_tests
    show_completion
}

# Run main function
main "$@"