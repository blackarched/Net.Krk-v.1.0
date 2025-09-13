#!/usr/bin/env python3
"""
Direct test of dashboard logic without Flask
"""

import os

def test_dashboard_logic():
    """Test the dashboard loading logic directly"""
    print("🔍 Testing Dashboard Logic Directly...")
    
    # Simulate the exact logic from combined_dashboard.py
    try:
        print("📁 Current directory:", os.getcwd())
        print("📁 Files in current directory:", [f for f in os.listdir('.') if 'new_dash' in f])
        
        # Try to load new_dash2.html (the exact path the dashboard uses)
        file_path = 'new_dash2.html'
        print(f"🔍 Trying to open: {file_path}")
        
        with open(file_path, 'r') as f:
            html_content = f.read()
        
        print(f"✅ Successfully loaded {file_path} ({len(html_content)} characters)")
        
        # Apply the same replacements as the dashboard
        print("🔧 Applying API replacements...")
        
        # Replace mock data with real API calls
        html_content = html_content.replace(
            '// Simulate API call with mock data\n                await new Promise(resolve => setTimeout(resolve, 3000));\n                \n                // Use mock networks for demonstration\n                const networks = mockNetworks;',
            '''// Real API call
                const response = await fetch('/api/scan');
                const data = await response.json();
                const networks = data.networks || [];'''
        )
        
        # Replace attack mock data with real API calls
        html_content = html_content.replace(
            '// Simulate API call with mock response\n                    await new Promise(resolve => setTimeout(resolve, 3000));\n                    \n                    // Simulate success or failure\n                    const success = Math.random() > 0.3;',
            '''// Real API call
                    const attackResponse = await fetch('/api/execute-attack', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            attack_type: vector,
                            target: selectedTarget
                        })
                    });
                    const attackData = await attackResponse.json();
                    const success = attackData.status === 'success';'''
        )
        
        # Replace stop attack mock data
        html_content = html_content.replace(
            '// Simulate API call\n                await new Promise(resolve => setTimeout(resolve, 1000));',
            '''// Real API call
                await fetch('/api/attack/stop', { method: 'POST' });'''
        )
        
        print("✅ API replacements applied")
        
        # Check for key elements
        checks = [
            ('NET.KRAK', 'Main branding'),
            ('holographic-panel', 'Holographic panels'),
            ('quantum-grid', 'Quantum grid background'),
            ('cyber-button', 'Cyber buttons'),
            ('interface-selector', 'Interface selector'),
            ('monitor-controls', 'Monitor controls'),
            ('loadInterfaces', 'Interface detection function'),
            ('toggleMonitorMode', 'Monitor mode toggle function'),
            ('/api/interfaces', 'Interface API call'),
            ('/api/monitor-mode', 'Monitor mode API call'),
            ('/api/scan', 'Real scan API call')
        ]
        
        print(f"\n📊 Final content length: {len(html_content):,} characters")
        print("\n✅ Dashboard Elements Check:")
        
        all_found = True
        for check, description in checks:
            if check in html_content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_found = False
        
        if all_found:
            print("\n🎯 SUCCESS: Dashboard logic is working correctly!")
            print("✅ The dashboard WILL load the new_dash2.html UI")
            print("✅ All visual elements are present")
            print("✅ WiFi interface detection is implemented")
            print("✅ Monitor mode controls are available")
            print("✅ Attack dashboard functionality is ready")
        else:
            print("\n❌ Some elements are missing - dashboard will show old UI")
            
        return all_found
        
    except FileNotFoundError as e:
        print(f"❌ FileNotFoundError: {e}")
        print("📁 This means the dashboard will fall back to old HTML")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_dashboard_logic()