#!/usr/bin/env python3
"""
Test script to check file loading without Flask
"""

import os
import sys

def test_file_loading():
    """Test if new_dash2.html can be loaded from different directories"""
    print("🔍 Testing file loading...")
    
    # Test from root directory
    print("\n📁 Testing from root directory:")
    try:
        with open('new_dash2.html', 'r') as f:
            content = f.read()
        print(f"✅ new_dash2.html found ({len(content)} characters)")
        print(f"✅ Contains NET.KRAK: {'NET.KRAK' in content}")
        print(f"✅ Contains holographic: {'holographic' in content}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test from src directory
    print("\n📁 Testing from src directory:")
    try:
        with open('../new_dash2.html', 'r') as f:
            content = f.read()
        print(f"✅ ../new_dash2.html found ({len(content)} characters)")
        print(f"✅ Contains NET.KRAK: {'NET.KRAK' in content}")
        print(f"✅ Contains holographic: {'holographic' in content}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test absolute path
    print("\n📁 Testing absolute path:")
    try:
        abs_path = os.path.abspath('new_dash2.html')
        with open(abs_path, 'r') as f:
            content = f.read()
        print(f"✅ {abs_path} found ({len(content)} characters)")
        print(f"✅ Contains NET.KRAK: {'NET.KRAK' in content}")
        print(f"✅ Contains holographic: {'holographic' in content}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_dashboard_logic():
    """Test the dashboard loading logic"""
    print("\n🔧 Testing dashboard loading logic...")
    
    # Simulate the dashboard logic
    try:
        print("📁 Current working directory:", os.getcwd())
        print("📁 Files in current directory:", os.listdir('.'))
        
        # Try the path the dashboard uses
        file_path = '../new_dash2.html'
        print(f"🔍 Trying to open: {file_path}")
        
        with open(file_path, 'r') as f:
            html_content = f.read()
        
        print(f"✅ Successfully loaded {file_path} ({len(html_content)} characters)")
        
        # Check for key elements
        checks = [
            ('NET.KRAK', 'Main branding'),
            ('holographic-panel', 'Holographic panels'),
            ('interface-selector', 'Interface selector'),
            ('monitor-controls', 'Monitor controls'),
            ('loadInterfaces', 'Interface detection function')
        ]
        
        for check, description in checks:
            if check in html_content:
                print(f"✅ {description}: Found")
            else:
                print(f"❌ {description}: Missing")
                
    except Exception as e:
        print(f"❌ Error in dashboard logic: {e}")

if __name__ == "__main__":
    test_file_loading()
    test_dashboard_logic()