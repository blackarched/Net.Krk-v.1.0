#!/bin/bash

# NET.KRAK v3.0 Setup and Run Script
echo "🚀 NET.KRAK v3.0 Setup and Run Script"
echo "======================================"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    PYTHON_CMD="python"
else
    echo "⚠️  No virtual environment detected"
    echo "   Using system Python (may require sudo for WiFi access)"
    PYTHON_CMD="python3"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    pip install flask flask_cors scapy psutil
else
    echo "   Installing system-wide (may require sudo)..."
    sudo pip install flask flask_cors scapy psutil
fi

# Check if dependencies are installed
echo ""
echo "🔍 Checking dependencies..."
$PYTHON_CMD -c "import flask, flask_cors, scapy, psutil; print('✅ All dependencies available')" 2>/dev/null || {
    echo "❌ Some dependencies missing. Please install manually:"
    echo "   pip install flask flask_cors scapy psutil"
    exit 1
}

# Check for WiFi interface
echo ""
echo "📡 Checking WiFi interface..."
if command -v iwconfig &> /dev/null; then
    echo "Available WiFi interfaces:"
    iwconfig 2>/dev/null | grep -E "IEEE 802.11|ESSID" || echo "   No WiFi interfaces found"
else
    echo "⚠️  iwconfig not found. WiFi scanning may not work."
fi

# Run the application
echo ""
echo "🎯 Starting NET.KRAK v3.0..."
echo "   Dashboard will be available at: http://localhost:5000"
echo "   Attack dashboard at: http://localhost:5000/attack"
echo "   Press Ctrl+C to stop"
echo ""

# Try to run without sudo first
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "🚀 Running with virtual environment Python..."
    $PYTHON_CMD src/combined_dashboard.py
else
    echo "🚀 Running with system Python..."
    $PYTHON_CMD src/combined_dashboard.py
fi