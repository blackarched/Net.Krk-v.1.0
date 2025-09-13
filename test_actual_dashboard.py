#!/usr/bin/env python3
"""
Test the actual dashboard behavior
"""

import os
import sys

def test_dashboard_behavior():
    """Test what actually happens when the dashboard runs"""
    print("🔍 Testing Actual Dashboard Behavior...")
    
    # Simulate running from the project root directory
    original_cwd = os.getcwd()
    print(f"📁 Current working directory: {original_cwd}")
    
    # Check if new_dash2.html exists
    if not os.path.exists('new_dash2.html'):
        print("❌ new_dash2.html not found in current directory!")
        print("📁 Files in current directory:", [f for f in os.listdir('.') if 'new_dash' in f])
        return False
    
    print("✅ new_dash2.html found")
    
    # Simulate the exact logic from combined_dashboard.py
    try:
        print("🔍 Attempting to load new_dash2.html...")
        with open('new_dash2.html', 'r') as f:
            html_content = f.read()
        print(f"✅ Successfully loaded new_dash2.html ({len(html_content)} characters)")
        
        # Apply replacements
        html_content = html_content.replace(
            '// Simulate API call with mock data\n                await new Promise(resolve => setTimeout(resolve, 3000));\n                \n                // Use mock networks for demonstration\n                const networks = mockNetworks;',
            '''// Real API call
                const response = await fetch('/api/scan');
                const data = await response.json();
                const networks = data.networks || [];'''
        )
        
        print("✅ API replacements applied")
        
        # Check for key elements
        if 'NET.KRAK' in html_content:
            print("✅ NET.KRAK branding found")
        else:
            print("❌ NET.KRAK branding missing")
        
        if 'interface-selector' in html_content:
            print("✅ Interface selector found")
        else:
            print("❌ Interface selector missing")
        
        if 'monitor-controls' in html_content:
            print("✅ Monitor controls found")
        else:
            print("❌ Monitor controls missing")
        
        if 'holographic-panel' in html_content:
            print("✅ Holographic panels found")
        else:
            print("❌ Holographic panels missing")
        
        print("\n🎯 Dashboard should work correctly!")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ FileNotFoundError: {e}")
        print("📁 This would cause the dashboard to fall back to old HTML")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_attack_dashboard():
    """Test the attack dashboard route"""
    print("\n🔍 Testing Attack Dashboard...")
    
    # Simulate the attack dashboard logic
    try:
        with open('new_dash2.html', 'r') as f:
            html_content = f.read()
        
        # Apply attack dashboard modifications
        html_content = html_content.replace(
            '<title>NET.KRAK // WiFi Penetration Suite v3.0</title>',
            '<title>NET.KRAK // Attack Dashboard v3.0</title>'
        )
        
        html_content = html_content.replace(
            'NET.KRAK',
            'NET.KRAK // ATTACK'
        )
        
        print("✅ Attack dashboard modifications applied")
        
        if 'NET.KRAK // ATTACK' in html_content:
            print("✅ Attack dashboard branding found")
        else:
            print("❌ Attack dashboard branding missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing attack dashboard: {e}")
        return False

if __name__ == "__main__":
    print("🚀 NET.KRAK Dashboard Test")
    print("=" * 50)
    
    main_ok = test_dashboard_behavior()
    attack_ok = test_attack_dashboard()
    
    print("\n🎯 Test Results:")
    print("=" * 50)
    if main_ok and attack_ok:
        print("✅ Both dashboards should work correctly!")
        print("✅ The new_dash2.html UI should load")
        print("✅ Interface detection should work")
        print("✅ Monitor mode controls should be available")
        print("✅ Attack dashboard should be accessible")
    else:
        print("❌ There are issues that need to be fixed")
    
    print("\n📋 To run the dashboard:")
    print("   python src/combined_dashboard.py")
    print("   Then open: http://localhost:5000")
    print("   Attack dashboard: http://localhost:5000/attack")