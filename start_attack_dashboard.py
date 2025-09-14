#!/usr/bin/env python3
"""
Start Attack Dashboard Server
Real-world ready attack dashboard with actual attack functionality
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import scapy
        from scapy.layers.dot11 import Dot11, Dot11Deauth, RadioTap
        logger.info("✅ Scapy available for packet manipulation")
    except ImportError as e:
        logger.error(f"❌ Scapy not available: {e}")
        logger.error("Install with: pip install scapy")
        return False
    
    try:
        import psutil
        logger.info("✅ psutil available for system monitoring")
    except ImportError as e:
        logger.error(f"❌ psutil not available: {e}")
        logger.error("Install with: pip install psutil")
        return False
    
    return True

def check_interface():
    """Check if network interface is available"""
    try:
        from scapy.all import get_if_list
        interfaces = get_if_list()
        logger.info(f"Available interfaces: {interfaces}")
        
        # Look for wireless interfaces
        wireless_interfaces = [iface for iface in interfaces if iface.startswith(('wlan', 'wifi', 'mon'))]
        if wireless_interfaces:
            logger.info(f"✅ Wireless interfaces found: {wireless_interfaces}")
            return True
        else:
            logger.warning("⚠️  No wireless interfaces found. Attacks may not work properly.")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking interfaces: {e}")
        return False

def main():
    """Main function to start attack dashboard"""
    logger.info("🚀 Starting NET.KRAK Attack Dashboard...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Missing dependencies. Please install required packages.")
        sys.exit(1)
    
    # Check network interface
    check_interface()
    
    try:
        # Import and start attack dashboard
        from attack_dashboard import app
        
        logger.info("✅ Attack Dashboard loaded successfully")
        logger.info("🌐 Starting server on http://localhost:5001")
        logger.info("⚡ Real attack functionality enabled")
        logger.info("🛡️  Use responsibly and only on authorized networks")
        
        # Start Flask server
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start attack dashboard: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()