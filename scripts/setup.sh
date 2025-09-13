#!/bin/bash

# Network Scanner Setup Script
# ============================

echo "=========================================="
echo "Network Scanner Setup Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script needs to be run with sudo privileges"
    echo "Usage: sudo ./setup.sh"
    exit 1
fi

# Update package lists
echo "Updating package lists..."
apt-get update

# Install system dependencies
echo "Installing system dependencies..."
apt-get install -y python3-dev libpcap-dev tcpdump net-tools python3-pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Make the script executable
echo "Making network_scanner.py executable..."
chmod +x network_scanner.py

# Create log directory if it doesn't exist
echo "Creating log directory..."
mkdir -p logs

echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "To run the network scanner:"
echo "  sudo python3 network_scanner.py"
echo ""
echo "Make sure to configure the network parameters in the script first!"
echo "=========================================="