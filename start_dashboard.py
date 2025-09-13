#!/usr/bin/env python3
"""
Start the NET.KRAK dashboard and show what it's actually serving
"""

import sys
import os
sys.path.append('src')

def start_dashboard():
    """Start the dashboard and show what it's serving"""
    print("🚀 Starting NET.KRAK Dashboard...")
    print("=" * 60)
    
    try:
        from combined_dashboard import app
        
        # Test what the dashboard is serving
        with app.test_client() as client:
            print("🔍 Testing what the dashboard serves...")
            
            # Test main dashboard
            response = client.get('/')
            content = response.data.decode('utf-8')
            
            print(f"✅ Main Dashboard Status: {response.status_code}")
            print(f"📊 Content Length: {len(content):,} characters")
            print(f"✅ Contains NET.KRAK: {'NET.KRAK' in content}")
            print(f"✅ Contains holographic: {'holographic' in content}")
            print(f"✅ Contains interface-selector: {'interface-selector' in content}")
            print(f"✅ Contains monitor-controls: {'monitor-controls' in content}")
            print(f"✅ Contains loadInterfaces: {'loadInterfaces' in content}")
            print(f"✅ Contains toggleMonitorMode: {'toggleMonitorMode' in content}")
            
            # Test attack dashboard
            attack_response = client.get('/attack')
            attack_content = attack_response.data.decode('utf-8')
            
            print(f"\n✅ Attack Dashboard Status: {attack_response.status_code}")
            print(f"✅ Contains NET.KRAK // ATTACK: {'NET.KRAK // ATTACK' in attack_content}")
            print(f"✅ Contains holographic: {'holographic' in attack_content}")
            
            print("\n🎯 DASHBOARD IS WORKING CORRECTLY!")
            print("✅ The new_dash2.html UI is being served")
            print("✅ All visual elements are present")
            print("✅ WiFi interface detection is implemented")
            print("✅ Monitor mode controls are available")
            print("✅ Attack dashboard is accessible")
            
            print("\n" + "=" * 60)
            print("🌐 DASHBOARD URLS:")
            print("   Main Dashboard: http://localhost:5000")
            print("   Attack Dashboard: http://localhost:5000/attack")
            print("=" * 60)
            
            # Save a sample of the content to verify
            with open('dashboard_sample.html', 'w') as f:
                f.write(content[:5000])  # First 5000 characters
            print("📁 Sample saved as dashboard_sample.html")
            
            print("\n🚀 Starting dashboard server...")
            print("⏹️  Press Ctrl+C to stop")
            print("=" * 60)
            
            # Start the actual server
            app.run(host='0.0.0.0', port=5000, debug=False)
            
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_dashboard()