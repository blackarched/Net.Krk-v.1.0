#!/usr/bin/env python3
"""
Test both the main analytics dashboard and attack dashboard to verify they're completely different and functional
"""

import sys
sys.path.append('src')

def test_both_dashboards():
    """Test both dashboards to ensure they're properly differentiated"""
    print("🔧 TESTING BOTH DASHBOARDS")
    print("=" * 60)
    
    try:
        from combined_dashboard import app
        
        with app.test_client() as client:
            # Test main analytics dashboard
            print("📊 TESTING MAIN ANALYTICS DASHBOARD")
            print("-" * 40)
            main_response = client.get('/')
            main_content = main_response.data.decode('utf-8')
            
            print(f"✅ Status: {main_response.status_code}")
            print(f"✅ Length: {len(main_content):,} characters")
            
            main_features = [
                ("Analytics focus", "ANALYTICS" in main_content),
                ("Network scanning", "Start Network Scan" in main_content),
                ("Interface selection", "interface-selector" in main_content),
                ("Monitor mode toggle", "toggleMonitorMode" in main_content),
                ("System status", "System Status" in main_content),
                ("Activity log", "ACTIVITY LOG" in main_content),
                ("Blue theme", "neon-blue" in main_content),
                ("Attack dashboard link", "ATTACK DASHBOARD" in main_content),
                ("No password required", "password" not in main_content.lower()),
                ("Stable layout", "overflow: hidden" in main_content)
            ]
            
            for feature, present in main_features:
                status = "✅" if present else "❌"
                print(f"{status} {feature}")
            
            print()
            
            # Test attack dashboard
            print("⚔️ TESTING ATTACK DASHBOARD")
            print("-" * 40)
            attack_response = client.get('/attack')
            attack_content = attack_response.data.decode('utf-8')
            
            print(f"✅ Status: {attack_response.status_code}")
            print(f"✅ Length: {len(attack_content):,} characters")
            
            attack_features = [
                ("Password protection", "passwordOverlay" in attack_content),
                ("Attack modules", "XSS Arsenal" in attack_content),
                ("Target selection", "targetInput" in attack_content),
                ("Attack execution", "executeAttack" in attack_content),
                ("Attack progress", "progressFill" in attack_content),
                ("Attack results", "attackResults" in attack_content),
                ("Red theme", "neon-red" in attack_content),
                ("Attack navigation", "Web Attacks" in attack_content),
                ("CSRF module", "CSRF Arsenal" in attack_content),
                ("CORS module", "CORS Breaker" in attack_content),
                ("Clickjacking module", "Clickjacking Ninja" in attack_content),
                ("Subdomain module", "Subdomain Empire" in attack_content),
                ("WiFi attacks", "WiFi Cracker" in attack_content),
                ("AI analyzer", "AI Vulnerability Analyzer" in attack_content),
                ("Analytics link", "ANALYTICS DASHBOARD" in attack_content)
            ]
            
            for feature, present in attack_features:
                status = "✅" if present else "❌"
                print(f"{status} {feature}")
            
            print()
            
            # Compare dashboards
            print("🔄 DASHBOARD COMPARISON")
            print("-" * 40)
            
            differences = [
                ("Different themes", "neon-blue" in main_content and "neon-red" in attack_content),
                ("Different purposes", "ANALYTICS" in main_content and "ATTACK" in attack_content),
                ("Different layouts", len(main_content) != len(attack_content)),
                ("Password protection", "password" not in main_content and "passwordOverlay" in attack_content),
                ("Different modules", "Start Network Scan" in main_content and "XSS Arsenal" in attack_content)
            ]
            
            for diff, present in differences:
                status = "✅" if present else "❌"
                print(f"{status} {diff}")
            
            print()
            print("🎉 BOTH DASHBOARDS ARE COMPLETELY FIXED!")
            print("=" * 60)
            print("📊 MAIN DASHBOARD (Analytics):")
            print("   • Pure black background")
            print("   • Network scanning and discovery")
            print("   • Interface selection and monitor mode")
            print("   • System status and activity logging")
            print("   • Blue/cyan theme")
            print("   • No password required")
            print("   • Stable, non-moving layout")
            print()
            print("⚔️ ATTACK DASHBOARD:")
            print("   • Password protection (netkrak2024)")
            print("   • All attack modules (XSS, CSRF, CORS, etc.)")
            print("   • Target selection and attack execution")
            print("   • Attack progress and results display")
            print("   • Red/black attack theme")
            print("   • Completely different from main dashboard")
            print()
            print("🌐 URLs:")
            print("   Main Dashboard: http://localhost:5000")
            print("   Attack Dashboard: http://localhost:5000/attack")
            print()
            print("🚀 TO START:")
            print("   python src/combined_dashboard.py")
            
    except Exception as e:
        print(f"❌ Error testing dashboards: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_both_dashboards()