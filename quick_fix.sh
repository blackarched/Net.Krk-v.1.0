#!/bin/bash

# Quick fix for flask_cors issue
echo "🔧 Quick Fix for flask_cors Issue"
echo "================================="

# Method 1: Install in virtual environment
echo "📦 Installing flask_cors in virtual environment..."
pip install flask_cors

# Method 2: If that doesn't work, install system-wide
echo "📦 Installing flask_cors system-wide..."
sudo pip install flask_cors

# Method 3: Alternative - run without sudo
echo ""
echo "🚀 Try running without sudo:"
echo "   python src/combined_dashboard.py"
echo ""
echo "   Or if you need WiFi access:"
echo "   sudo $(which python) src/combined_dashboard.py"