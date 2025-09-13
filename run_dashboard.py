#!/usr/bin/env python3
"""
Simple script to run the NET.KRAK dashboard
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        print("✅ Flask installed")
    except ImportError:
        print("❌ Flask not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask'], check=True)
        print("✅ Flask installed")
    
    try:
        import flask_cors
        print("✅ Flask-CORS installed")
    except ImportError:
        print("❌ Flask-CORS not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask-cors'], check=True)
        print("✅ Flask-CORS installed")

def run_dashboard():
    """Run the dashboard"""
    print("🚀 Starting NET.KRAK Dashboard...")
    print("=" * 50)
    print("📊 Main Dashboard: http://localhost:5000")
    print("⚔️ Attack Dashboard: http://localhost:5000/attack")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Import and run the dashboard
        sys.path.append('src')
        from combined_dashboard import app
        
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in the project root directory")
        print("2. Check if new_dash2.html exists")
        print("3. Install dependencies: pip install flask flask-cors")

if __name__ == "__main__":
    print("🎯 NET.KRAK v3.0 Dashboard Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('new_dash2.html'):
        print("❌ new_dash2.html not found!")
        print("   Make sure you're in the project root directory")
        sys.exit(1)
    
    if not os.path.exists('src/combined_dashboard.py'):
        print("❌ src/combined_dashboard.py not found!")
        print("   Make sure you're in the project root directory")
        sys.exit(1)
    
    print("✅ Project files found")
    
    # Check and install dependencies
    check_dependencies()
    
    # Run the dashboard
    run_dashboard()