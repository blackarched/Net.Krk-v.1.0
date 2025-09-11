#!/usr/bin/env python3
"""
Simple test script for Pydroid to diagnose issues
"""

print("🔍 Testing Net.Krk setup for Pydroid...")
print("=" * 50)

# Test 1: Check Python version
import sys
print(f"✅ Python version: {sys.version}")

# Test 2: Check if we can import required modules
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import error: {e}")

try:
    import scapy
    print(f"✅ Scapy version: {scapy.__version__}")
except ImportError as e:
    print(f"❌ Scapy import error: {e}")

try:
    import psutil
    print(f"✅ Psutil version: {psutil.__version__}")
except ImportError as e:
    print(f"❌ Psutil import error: {e}")

# Test 3: Check current directory and files
import os
print(f"📁 Current directory: {os.getcwd()}")
print(f"📁 Files in current directory:")
for file in os.listdir('.'):
    if file.endswith('.py') or file.endswith('.html'):
        print(f"   - {file}")

# Test 4: Check if we can start a simple Flask app
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello from Net.Krk test!"
    
    print("✅ Flask app created successfully")
    print("🚀 Starting test server on port 5000...")
    print("📱 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
    
except Exception as e:
    print(f"❌ Flask startup error: {e}")
    print("💡 Try running: pip install flask")