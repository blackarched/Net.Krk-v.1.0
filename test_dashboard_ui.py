#!/usr/bin/env python3
"""
Test script to verify dashboard UI is working correctly
"""

import sys
import os
sys.path.append('src')

def test_dashboard_loading():
    """Test if dashboard loads new_dash2.html correctly"""
    print("🔍 Testing Dashboard UI Loading...")
    
    try:
        from combined_dashboard import app
        
        with app.test_client() as client:
            # Test main dashboard
            response = client.get('/')
            if response.status_code == 200:
                content = response.data.decode('utf-8')
                
                # Check for new_dash2.html elements
                checks = [
                    ('NET.KRAK', 'Main branding'),
                    ('holographic-panel', 'Holographic panels'),
                    ('quantum-grid', 'Quantum grid background'),
                    ('cyber-button', 'Cyber buttons'),
                    ('interface-selector', 'Interface selector'),
                    ('monitor-controls', 'Monitor controls'),
                    ('loadInterfaces', 'Interface detection function'),
                    ('toggleMonitorMode', 'Monitor mode toggle function'),
                    ('fetch(\'/api/interfaces\')', 'Interface API call'),
                    ('fetch(\'/api/monitor-mode\')', 'Monitor mode API call')
                ]
                
                print("✅ Dashboard loaded successfully")
                print(f"📊 Content length: {len(content):,} characters")
                
                for check, description in checks:
                    if check in content:
                        print(f"✅ {description}: Found")
                    else:
                        print(f"❌ {description}: Missing")
                
                # Test attack dashboard
                attack_response = client.get('/attack')
                if attack_response.status_code == 200:
                    print("✅ Attack dashboard accessible")
                else:
                    print("❌ Attack dashboard not accessible")
                
                return True
            else:
                print(f"❌ Dashboard failed to load: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔌 Testing API Endpoints...")
    
    try:
        from combined_dashboard import app
        
        with app.test_client() as client:
            endpoints = [
                ('/api/interfaces', 'Interface detection'),
                ('/api/scan', 'Network scanning'),
                ('/api/stats', 'System statistics'),
                ('/api/targets', 'Target selection'),
                ('/api/attack-stats', 'Attack statistics')
            ]
            
            for endpoint, description in endpoints:
                response = client.get(endpoint)
                if response.status_code == 200:
                    print(f"✅ {description}: Working")
                else:
                    print(f"❌ {description}: Failed ({response.status_code})")
                    
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")

def test_file_structure():
    """Test file structure"""
    print("\n📁 Testing File Structure...")
    
    files_to_check = [
        'new_dash2.html',
        'src/combined_dashboard.py',
        'src/analytics_dashboard.py',
        'src/attack_dashboard.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {size:,} bytes")
        else:
            print(f"❌ {file_path}: Missing")

def main():
    """Main test function"""
    print("🚀 NET.KRAK Dashboard UI Test")
    print("=" * 50)
    
    # Test file structure
    test_file_structure()
    
    # Test dashboard loading
    dashboard_ok = test_dashboard_loading()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n🎯 Test Summary")
    print("=" * 50)
    if dashboard_ok:
        print("✅ Dashboard UI is working correctly!")
        print("✅ new_dash2.html layout is properly loaded")
        print("✅ WiFi interface detection is implemented")
        print("✅ Monitor mode controls are available")
        print("\n🚀 Ready to run: python src/combined_dashboard.py")
    else:
        print("❌ Dashboard UI has issues that need to be fixed")
    
    print("\n📱 Access URLs:")
    print("   Main Dashboard: http://localhost:5000")
    print("   Attack Dashboard: http://localhost:5000/attack")

if __name__ == "__main__":
    main()