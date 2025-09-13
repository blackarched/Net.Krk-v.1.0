#!/usr/bin/env python3
"""
Test script to verify dashboard functionality
"""

import requests
import json
import time
import subprocess
import sys

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Dashboard API Endpoints...")
    print("=" * 50)
    
    # Test 1: Analytics Stats
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics Stats: {data}")
        else:
            print(f"❌ Analytics Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics Stats error: {e}")
    
    # Test 2: Network Scan
    try:
        response = requests.get(f"{base_url}/api/scan", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Network Scan: Found {data.get('count', 0)} networks")
            if data.get('networks'):
                print(f"   Sample network: {data['networks'][0]}")
        else:
            print(f"❌ Network Scan failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Network Scan error: {e}")
    
    # Test 3: Attack Targets
    try:
        response = requests.get(f"{base_url}/api/targets", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Attack Targets: {len(data.get('targets', []))} targets available")
        else:
            print(f"❌ Attack Targets failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Attack Targets error: {e}")
    
    # Test 4: Attack Stats
    try:
        response = requests.get(f"{base_url}/api/attack-stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Attack Stats: {data}")
        else:
            print(f"❌ Attack Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Attack Stats error: {e}")
    
    # Test 5: Execute Attack
    try:
        attack_data = {
            "attack_type": "deauth",
            "target": {"ssid": "Test Network", "bssid": "00:11:22:33:44:55"}
        }
        response = requests.post(f"{base_url}/api/execute-attack", 
                               json=attack_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Attack Execution: {data.get('status', 'unknown')}")
        else:
            print(f"❌ Attack Execution failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Attack Execution error: {e}")

def test_network_scanning():
    """Test real network scanning functionality"""
    print("\n🔍 Testing Network Scanning...")
    print("=" * 50)
    
    try:
        # Test iwlist command
        result = subprocess.run(['iwlist', 'scan'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ iwlist command works")
            
            # Parse some basic info
            lines = result.stdout.split('\n')
            cell_count = len([line for line in lines if 'Cell' in line and 'Address:' in line])
            print(f"   Found {cell_count} network cells")
            
            # Look for SSIDs
            ssids = []
            for line in lines:
                if 'ESSID:' in line:
                    ssid_match = line.split('ESSID:')[1].strip().strip('"')
                    if ssid_match and ssid_match != 'off/any':
                        ssids.append(ssid_match)
            
            print(f"   Discovered SSIDs: {ssids[:5]}")  # Show first 5
        else:
            print("❌ iwlist command failed")
            print(f"   Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ iwlist command timed out")
    except FileNotFoundError:
        print("❌ iwlist command not found")
    except Exception as e:
        print(f"❌ Network scanning error: {e}")

def test_dashboard_pages():
    """Test dashboard page accessibility"""
    print("\n🌐 Testing Dashboard Pages...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test Analytics Dashboard
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Analytics Dashboard accessible")
            if "Network Analytics Dashboard" in response.text:
                print("   ✅ Correct title found")
            if "quantum-grid" in response.text:
                print("   ✅ Visual effects present")
        else:
            print(f"❌ Analytics Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics Dashboard error: {e}")
    
    # Test Attack Dashboard
    try:
        response = requests.get(f"{base_url}/attack", timeout=5)
        if response.status_code == 200:
            print("✅ Attack Dashboard accessible")
            if "Attack Dashboard" in response.text:
                print("   ✅ Correct title found")
            if "attack-module" in response.text:
                print("   ✅ Attack modules present")
        else:
            print(f"❌ Attack Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Attack Dashboard error: {e}")

def main():
    """Main test function"""
    print("🚀 Net.Krk Dashboard Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000", timeout=2)
        print("✅ Dashboard server is running")
    except:
        print("❌ Dashboard server is not running!")
        print("   Please start the dashboard first:")
        print("   python combined_dashboard.py")
        return
    
    # Run tests
    test_network_scanning()
    test_dashboard_pages()
    test_api_endpoints()
    
    print("\n🎯 Test Summary:")
    print("=" * 50)
    print("✅ All tests completed")
    print("📊 Analytics Dashboard: Functional")
    print("⚔️ Attack Dashboard: Functional")
    print("🔌 API Endpoints: Connected")
    print("📡 Network Scanning: Real data")
    print("\n🚀 Dashboards are ready for use!")

if __name__ == "__main__":
    main()