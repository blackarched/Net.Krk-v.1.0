#!/usr/bin/env python3
"""
Simple test server to verify the dashboard works
"""

import os
import sys

def create_test_dashboard():
    """Create a test dashboard that definitely loads new_dash2.html"""
    
    # Read the new_dash2.html file
    try:
        with open('new_dash2.html', 'r') as f:
            html_content = f.read()
        print("✅ Loaded new_dash2.html successfully")
    except FileNotFoundError:
        print("❌ new_dash2.html not found!")
        return None
    
    # Apply the same replacements as the real dashboard
    html_content = html_content.replace(
        '// Simulate API call with mock data\n                await new Promise(resolve => setTimeout(resolve, 3000));\n                \n                // Use mock networks for demonstration\n                const networks = mockNetworks;',
        '''// Real API call
                const response = await fetch('/api/scan');
                const data = await response.json();
                const networks = data.networks || [];'''
    )
    
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
    
    html_content = html_content.replace(
        '// Simulate API call\n                await new Promise(resolve => setTimeout(resolve, 1000));',
        '''// Real API call
                await fetch('/api/attack/stop', { method: 'POST' });'''
    )
    
    return html_content

def main():
    """Main function"""
    print("🚀 NET.KRAK Test Server")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('new_dash2.html'):
        print("❌ new_dash2.html not found!")
        print("   Make sure you're in the project root directory")
        sys.exit(1)
    
    print("✅ new_dash2.html found")
    
    # Create the dashboard content
    dashboard_content = create_test_dashboard()
    if not dashboard_content:
        sys.exit(1)
    
    print("✅ Dashboard content created")
    print(f"📊 Content length: {len(dashboard_content):,} characters")
    
    # Check for key elements
    if 'NET.KRAK' in dashboard_content:
        print("✅ NET.KRAK branding found")
    else:
        print("❌ NET.KRAK branding missing")
    
    if 'interface-selector' in dashboard_content:
        print("✅ Interface selector found")
    else:
        print("❌ Interface selector missing")
    
    if 'monitor-controls' in dashboard_content:
        print("✅ Monitor controls found")
    else:
        print("❌ Monitor controls missing")
    
    if 'holographic-panel' in dashboard_content:
        print("✅ Holographic panels found")
    else:
        print("❌ Holographic panels missing")
    
    # Save the test dashboard
    with open('test_dashboard.html', 'w') as f:
        f.write(dashboard_content)
    
    print("\n✅ Test dashboard saved as test_dashboard.html")
    print("🌐 Open test_dashboard.html in your browser to see the new UI")
    print("📱 The dashboard should show:")
    print("   - NET.KRAK branding")
    print("   - Holographic panels with neon effects")
    print("   - Interface selector dropdown")
    print("   - Monitor mode controls")
    print("   - Quantum grid background")
    print("   - Cyber buttons")

if __name__ == "__main__":
    main()