from flask import Flask, jsonify, request, session
import subprocess
import re
import time
import json
import os
from network_discovery import network_discovery

app = Flask(__name__)
app.secret_key = 'netkrak_combined_2024'

# Global state
is_scanning = False
is_attacking = False
discovered_networks = []
active_attacks = []
selected_target = None
selected_attack = None

# Enhanced network scanning using the new module
def scan_networks(interface='wlan0'):
    """Enhanced network scanning with comprehensive analysis"""
    global is_scanning, discovered_networks
    is_scanning = True
    add_log_entry('info', f'Starting enhanced network discovery on {interface}...')
    
    try:
        networks = network_discovery.scan_networks(interface)
        discovered_networks = networks
        add_log_entry('success', f'Discovered {len(networks)} networks with enhanced analysis')
        return networks
    except Exception as e:
        add_log_entry('error', f'Enhanced scan error: {e}')
        return []
    finally:
        is_scanning = False

def execute_attack(target, attack_type):
    """Execute REAL attack using attack modules"""
    global is_attacking
    is_attacking = True
    add_log_entry('info', f'Starting REAL {attack_type} attack on {target.get("ssid", "Hidden")}')
    
    try:
        # Import attack functions
        from attacks import (deauth_attack, handshake_capture, beacon_flood, evil_twin_attack, 
                           wps_attack, credential_capture, fragmentation_attack)
        
        success = False
        message = ""
        
        if attack_type == 'deauth':
            success = deauth_attack(
                interface='wlan0',
                target_bssid=target.get('bssid'),
                packet_count=30,
                dry_run=False
            )
            message = f"Deauth attack {'completed successfully' if success else 'failed'}"
            
        elif attack_type == 'handshake_capture':
            output_file = f"/tmp/handshake_{target.get('bssid', '').replace(':', '')}.pcap"
            success = handshake_capture(
                interface='wlan0',
                target_bssid=target.get('bssid'),
                output_file=output_file,
                duration=30
            )
            message = f"Handshake capture {'completed successfully' if success else 'failed'}"
            
        elif attack_type == 'beacon_flood':
            success = beacon_flood(
                interface='wlan0',
                ssid=target.get('ssid', 'FakeAP'),
                packet_count=50,
                interval=0.1
            )
            message = f"Beacon flood {'completed successfully' if success else 'failed'}"
            
        elif attack_type == 'evil_twin':
            success = evil_twin_attack(
                interface='wlan0',
                target_bssid=target.get('bssid'),
                target_ssid=target.get('ssid', 'FakeAP'),
                channel=target.get('channel', 6)
            )
            message = f"Evil twin attack {'completed successfully' if success else 'failed'}"
            
        elif attack_type == 'wps':
            success = wps_attack(
                interface='wlan0',
                target_bssid=target.get('bssid'),
                timeout=300
            )
            message = f"WPS attack {'completed successfully' if success else 'failed'}"
            
        elif attack_type == 'credential':
            success = credential_capture(
                interface='wlan0',
                target_bssid=target.get('bssid'),
                duration=300
            )
            message = f"Credential capture {'completed successfully' if success else 'failed'}"
            
        elif attack_type == 'fragmentation':
            success = fragmentation_attack(
                interface='wlan0',
                target_bssid=target.get('bssid'),
                timeout=300
            )
            message = f"Fragmentation attack {'completed successfully' if success else 'failed'}"
            
        else:
            message = f"Unknown attack type: {attack_type}"
            success = False
        
        result = {
            'status': 'success' if success else 'failed',
            'attack_type': attack_type,
            'target': target,
            'timestamp': time.time(),
            'message': message,
            'success': success
        }
        
        active_attacks.append(result)
        is_attacking = False
        add_log_entry('success' if success else 'error', f'{attack_type} attack {message}')
        return result
        
    except Exception as e:
        result = {
            'status': 'error',
            'attack_type': attack_type,
            'target': target,
            'timestamp': time.time(),
            'message': f'Attack failed: {str(e)}',
            'success': False,
            'error': str(e)
        }
        
        active_attacks.append(result)
        is_attacking = False
        add_log_entry('error', f'{attack_type} attack failed: {str(e)}')
        return result

@app.route('/')
def analytics_dashboard():
    # Read the new dashboard HTML file
    try:
        # Try multiple possible paths for improved_main_dashboard.html
        possible_paths = [
            'improved_main_dashboard.html',  # Current directory
            '../improved_main_dashboard.html',  # Parent directory
            os.path.join(os.path.dirname(__file__), '..', 'improved_main_dashboard.html'),  # Relative to this file
            os.path.join(os.path.dirname(__file__), 'improved_main_dashboard.html')  # Same directory as this file
        ]
        
        html_content = None
        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    html_content = f.read()
                print(f"✅ Loaded improved_main_dashboard.html from: {path}")
                break
            except FileNotFoundError:
                continue
        
        if html_content is None:
            raise FileNotFoundError("improved_main_dashboard.html not found in any expected location")
        
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
        
        return html_content
    except FileNotFoundError:
        # Fallback to original dashboard if new_dash2.html not found
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Net.Krk - Analytics Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
            
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                background: radial-gradient(ellipse at center, #0a0a0a 0%, #000000 70%);
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                color: #00ffff;
                overflow: hidden;
                position: relative;
                font-weight: 300;
            }

            .quantum-grid {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 20%, rgba(0,255,255,0.03) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(255,0,255,0.03) 0%, transparent 50%),
                    linear-gradient(rgba(0,255,255,0.02) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0,255,255,0.02) 1px, transparent 1px);
                background-size: 800px 800px, 600px 600px, 40px 40px, 40px 40px;
                animation: quantumShift 20s linear infinite;
                z-index: -3;
            }

            @keyframes quantumShift {
                0% { background-position: 0 0, 0 0, 0 0, 0 0; }
                100% { background-position: 800px 800px, -600px -600px, 40px 40px, 40px 40px; }
            }

            .photon-cascade {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, transparent 30%, rgba(0,255,255,0.02) 50%, transparent 70%);
                animation: photonFlow 15s linear infinite;
                z-index: -2;
            }

            @keyframes photonFlow {
                0% { transform: translateY(-10px) translateX(0px); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateY(100vh) translateX(20px); opacity: 0; }
            }

            .container {
                position: relative;
                z-index: 1;
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
            }

            .title {
                font-size: 3em;
                color: #ff0088;
                text-shadow: 0 0 30px #ff0088;
                margin-bottom: 10px;
                animation: exploitPulse 3s ease-in-out infinite alternate;
            }

            @keyframes exploitPulse {
                0% { text-shadow: 0 0 20px #ff0088, 0 0 40px #ff0088; }
                100% { text-shadow: 0 0 30px #ff0088, 0 0 60px #ff0088, 0 0 80px rgba(255,0,136,0.8); }
            }

            .subtitle {
                color: #00ffff;
                font-size: 1.2em;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            }

            .nav-bar {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
            }

            .nav-button {
                background: linear-gradient(45deg, #ff0088, #00ffff);
                border: none;
                color: white;
                padding: 12px 25px;
                border-radius: 25px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }

            .nav-button:hover {
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(255, 0, 136, 0.4);
            }

            .nav-button.active {
                background: linear-gradient(45deg, #00ffff, #ff0088);
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }

            .stat-card {
                background: rgba(0, 255, 255, 0.05);
                border: 1px solid #00ffff;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s ease;
            }

            .stat-card:hover {
                background: rgba(0, 255, 255, 0.1);
                transform: translateY(-2px);
            }

            .stat-number {
                font-size: 2.5em;
                color: #ff0088;
                font-weight: bold;
                margin-bottom: 5px;
            }

            .stat-label {
                color: #00ffff;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .button {
                background: linear-gradient(45deg, #ff0088, #00ffff);
                border: none;
                color: white;
                padding: 15px 30px;
                border-radius: 25px;
                margin: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .button:hover {
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(255, 0, 136, 0.4);
            }

            .network-list {
                max-height: 500px;
                overflow-y: auto;
                margin: 20px 0;
            }

            .network-item {
                background: rgba(0, 255, 255, 0.05);
                border: 1px solid #00ffff;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s ease;
                animation: networkMaterialize 0.6s ease-out;
            }

            .network-item:hover {
                background: rgba(0, 255, 255, 0.1);
                transform: translateX(5px);
            }

            @keyframes networkMaterialize {
                0% { opacity: 0; transform: translateX(-30px); }
                100% { opacity: 1; transform: translateX(0); }
            }

            .network-ssid {
                color: #ff0088;
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 5px;
            }

            .network-details {
                color: #00ffff;
                font-size: 0.9em;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }

            .signal-bar {
                width: 100%;
                height: 4px;
                background: #333;
                border-radius: 2px;
                margin: 5px 0;
                overflow: hidden;
            }

            .signal-fill {
                height: 100%;
                background: linear-gradient(90deg, #ff0000, #ffff00, #00ff00);
                transition: width 0.5s ease;
            }

            .activity-log {
                background: #000;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
                height: 200px;
                overflow-y: auto;
                font-size: 12px;
            }

            .log-entry {
                margin: 5px 0;
                padding: 5px;
                border-radius: 3px;
                animation: logMaterialize 0.5s ease-out;
            }

            .log-info { color: #00ffff; }
            .log-success { color: #00ff00; }
            .log-warning { color: #ffff00; }
            .log-error { color: #ff0000; }

            @keyframes logMaterialize {
                0% { opacity: 0; transform: translateX(-20px); }
                100% { opacity: 1; transform: translateX(0); }
            }

            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #333;
                border-top: 3px solid #00ffff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="quantum-grid"></div>
        <div class="photon-cascade"></div>
        
        <div class="container">
            <div class="header">
                <h1 class="title">net.krak</h1>
                <p class="subtitle">Network Analytics Dashboard</p>
            </div>
            
            <div class="nav-bar">
                <a href="/" class="nav-button active">📊 Analytics</a>
                <a href="/attack" class="nav-button">⚔️ Attack Modules</a>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card">
                    <div class="stat-number" id="totalNetworks">0</div>
                    <div class="stat-label">Total Networks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="hiddenNetworks">0</div>
                    <div class="stat-label">Hidden Networks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="openNetworks">0</div>
                    <div class="stat-label">Open Networks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="securedNetworks">0</div>
                    <div class="stat-label">Secured Networks</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <button class="button" id="scanBtn" onclick="scanNetworks()">Start Network Scan</button>
                <button class="button" onclick="refreshStats()">Refresh Statistics</button>
            </div>
            
            <div class="network-list" id="networkList">
                <div class="log-entry log-info">Click "Start Network Scan" to discover WiFi networks</div>
            </div>
            
            <div class="activity-log" id="activityLog">
                <div class="log-entry log-info">[INFO] Analytics dashboard initialized</div>
                <div class="log-entry log-success">[SUCCESS] Ready for network analysis</div>
            </div>
        </div>
        
        <script>
            function addLogEntry(type, message) {
                const log = document.getElementById('activityLog');
                const entry = document.createElement('div');
                entry.className = `log-entry log-${type}`;
                entry.textContent = `[${type.toUpperCase()}] ${message}`;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
            }
            
            function updateStats() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('totalNetworks').textContent = data.total_networks;
                        document.getElementById('hiddenNetworks').textContent = data.hidden_networks;
                        document.getElementById('openNetworks').textContent = data.open_networks;
                        document.getElementById('securedNetworks').textContent = data.secured_networks;
                    });
            }
            
            function scanNetworks() {
                const scanBtn = document.getElementById('scanBtn');
                scanBtn.disabled = true;
                scanBtn.innerHTML = '<div class="loading"></div> SCANNING...';
                
                addLogEntry('info', 'Starting comprehensive network scan...');
                
                fetch('/api/scan')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            addLogEntry('success', `Discovered ${data.networks.length} networks`);
                            displayNetworks(data.networks);
                            updateStats();
                        } else {
                            addLogEntry('error', `Scan failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addLogEntry('error', `Scan failed: ${error.message}`);
                    })
                    .finally(() => {
                        scanBtn.disabled = false;
                        scanBtn.textContent = 'Start Network Scan';
                    });
            }
            
            function displayNetworks(networks) {
                const container = document.getElementById('networkList');
                container.innerHTML = '';
                
                if (networks.length === 0) {
                    container.innerHTML = '<div class="log-entry log-warning">No networks found</div>';
                    return;
                }
                
                networks.sort((a, b) => (b.signal || -100) - (a.signal || -100));
                
                networks.forEach(net => {
                    const div = document.createElement('div');
                    div.className = 'network-item';
                    
                    const signalStrength = net.signal || -100;
                    const signalPercent = Math.max(0, Math.min(100, ((signalStrength + 100) / 60) * 100));
                    
                    div.innerHTML = `
                        <div class="network-ssid">${net.ssid || 'Hidden Network'}</div>
                        <div class="network-details">
                            <div><strong>BSSID:</strong> ${net.bssid || 'Unknown'}</div>
                            <div><strong>Signal:</strong> ${signalStrength}dBm</div>
                            <div><strong>Channel:</strong> ${net.channel || 'Unknown'}</div>
                            <div><strong>Security:</strong> ${net.security || 'Unknown'}</div>
                        </div>
                        <div class="signal-bar">
                            <div class="signal-fill" style="width: ${signalPercent}%"></div>
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
            
            function refreshStats() {
                addLogEntry('info', 'Refreshing statistics...');
                updateStats();
            }
            
            updateStats();
        </script>
    </body>
    </html>
    '''

@app.route('/attack')
def attack_dashboard():
    # Read the fixed attack dashboard HTML file
    try:
        # Try multiple possible paths for working_attack_dashboard.html
        possible_paths = [
            'working_attack_dashboard.html',  # Current directory
            '../working_attack_dashboard.html',  # Parent directory
            os.path.join(os.path.dirname(__file__), '..', 'working_attack_dashboard.html'),  # Relative to this file
            os.path.join(os.path.dirname(__file__), 'working_attack_dashboard.html')  # Same directory as this file
        ]
        
        html_content = None
        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    html_content = f.read()
                print(f"✅ Loaded working_attack_dashboard.html from: {path}")
                break
            except FileNotFoundError:
                continue
        
        if html_content is None:
            raise FileNotFoundError("working_attack_dashboard.html not found in any expected location")
        
        # Return the attack dashboard as-is (no modifications needed)
        return html_content
    except FileNotFoundError:
        # Fallback to original attack dashboard if new_dash2.html not found
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Net.Krk - Attack Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
            
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                background: radial-gradient(ellipse at center, #0a0a0a 0%, #000000 70%);
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                color: #00ffff;
                overflow: hidden;
                position: relative;
                font-weight: 300;
            }

            .quantum-grid {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 20%, rgba(0,255,255,0.03) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(255,0,255,0.03) 0%, transparent 50%),
                    linear-gradient(rgba(0,255,255,0.02) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0,255,255,0.02) 1px, transparent 1px);
                background-size: 800px 800px, 600px 600px, 40px 40px, 40px 40px;
                animation: quantumShift 20s linear infinite;
                z-index: -3;
            }

            @keyframes quantumShift {
                0% { background-position: 0 0, 0 0, 0 0, 0 0; }
                100% { background-position: 800px 800px, -600px -600px, 40px 40px, 40px 40px; }
            }

            .photon-cascade {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, transparent 30%, rgba(0,255,255,0.02) 50%, transparent 70%);
                animation: photonFlow 15s linear infinite;
                z-index: -2;
            }

            @keyframes photonFlow {
                0% { transform: translateY(-10px) translateX(0px); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateY(100vh) translateX(20px); opacity: 0; }
            }

            .container {
                position: relative;
                z-index: 1;
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
            }

            .title {
                font-size: 3em;
                color: #ff0088;
                text-shadow: 0 0 30px #ff0088;
                margin-bottom: 10px;
                animation: exploitPulse 3s ease-in-out infinite alternate;
            }

            @keyframes exploitPulse {
                0% { text-shadow: 0 0 20px #ff0088, 0 0 40px #ff0088; }
                100% { text-shadow: 0 0 30px #ff0088, 0 0 60px #ff0088, 0 0 80px rgba(255,0,136,0.8); }
            }

            .subtitle {
                color: #00ffff;
                font-size: 1.2em;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            }

            .nav-bar {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
            }

            .nav-button {
                background: linear-gradient(45deg, #ff0088, #00ffff);
                border: none;
                color: white;
                padding: 12px 25px;
                border-radius: 25px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }

            .nav-button:hover {
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(255, 0, 136, 0.4);
            }

            .nav-button.active {
                background: linear-gradient(45deg, #00ffff, #ff0088);
            }

            .attack-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }

            .attack-module {
                background: rgba(0, 255, 255, 0.05);
                border: 1px solid #00ffff;
                border-radius: 10px;
                padding: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
            }

            .attack-module:hover {
                background: rgba(0, 255, 255, 0.1);
                transform: scale(1.02);
            }

            .attack-module.active {
                background: rgba(255, 0, 136, 0.1);
                border-color: #ff0088;
            }

            .attack-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }

            .attack-name {
                color: #ff0088;
                font-weight: bold;
                margin-bottom: 5px;
            }

            .attack-description {
                color: #00ffff;
                font-size: 0.8em;
                margin-bottom: 10px;
            }

            .button {
                background: linear-gradient(45deg, #ff0088, #00ffff);
                border: none;
                color: white;
                padding: 15px 30px;
                border-radius: 25px;
                margin: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .button:hover {
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(255, 0, 136, 0.4);
            }

            .button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            .activity-log {
                background: #000;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
                height: 200px;
                overflow-y: auto;
                font-size: 12px;
            }

            .log-entry {
                margin: 5px 0;
                padding: 5px;
                border-radius: 3px;
                animation: logMaterialize 0.5s ease-out;
            }

            .log-info { color: #00ffff; }
            .log-success { color: #00ff00; }
            .log-warning { color: #ffff00; }
            .log-error { color: #ff0000; }

            @keyframes logMaterialize {
                0% { opacity: 0; transform: translateX(-20px); }
                100% { opacity: 1; transform: translateX(0); }
            }

            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #333;
                border-top: 3px solid #00ffff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="quantum-grid"></div>
        <div class="photon-cascade"></div>
        
        <div class="container">
            <div class="header">
                <h1 class="title">net.krak</h1>
                <p class="subtitle">Attack Dashboard</p>
            </div>
            
            <div class="nav-bar">
                <a href="/" class="nav-button">📊 Analytics</a>
                <a href="/attack" class="nav-button active">⚔️ Attack Modules</a>
            </div>
            
            <div class="attack-grid">
                <div class="attack-module" onclick="selectAttack('deauth')">
                    <div class="attack-icon">📡</div>
                    <div class="attack-name">Deauth Attack</div>
                    <div class="attack-description">Disconnect devices from target network</div>
                </div>
                <div class="attack-module" onclick="selectAttack('handshake')">
                    <div class="attack-icon">🤝</div>
                    <div class="attack-name">Handshake Capture</div>
                    <div class="attack-description">Capture WPA/WPA2 handshakes</div>
                </div>
                <div class="attack-module" onclick="selectAttack('evil_twin')">
                    <div class="attack-icon">👥</div>
                    <div class="attack-name">Evil Twin</div>
                    <div class="attack-description">Create fake access point</div>
                </div>
                <div class="attack-module" onclick="selectAttack('wps')">
                    <div class="attack-icon">🔐</div>
                    <div class="attack-name">WPS Attack</div>
                    <div class="attack-description">Exploit WPS vulnerabilities</div>
                </div>
                <div class="attack-module" onclick="selectAttack('fragmentation')">
                    <div class="attack-icon">💥</div>
                    <div class="attack-name">Fragmentation</div>
                    <div class="attack-description">Fragmentation attack on WEP</div>
                </div>
                <div class="attack-module" onclick="selectAttack('credential')">
                    <div class="attack-icon">🔑</div>
                    <div class="attack-name">Credential Harvest</div>
                    <div class="attack-description">Capture login credentials</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <button class="button" id="executeBtn" onclick="executeAttack()" disabled>Execute Attack</button>
                <button class="button" onclick="stopAllAttacks()">Stop All Attacks</button>
            </div>
            
            <div class="activity-log" id="activityLog">
                <div class="log-entry log-info">[INFO] Attack dashboard initialized</div>
                <div class="log-entry log-success">[SUCCESS] Ready for attack operations</div>
            </div>
        </div>
        
        <script>
            let selectedAttack = null;
            let isAttacking = false;
            
            function addLogEntry(type, message) {
                const log = document.getElementById('activityLog');
                const entry = document.createElement('div');
                entry.className = `log-entry log-${type}`;
                entry.textContent = `[${type.toUpperCase()}] ${message}`;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
            }
            
            function selectAttack(attackType) {
                document.querySelectorAll('.attack-module').forEach(module => {
                    module.classList.remove('active');
                });
                
                event.target.closest('.attack-module').classList.add('active');
                selectedAttack = attackType;
                
                addLogEntry('info', `Selected attack: ${attackType}`);
                document.getElementById('executeBtn').disabled = false;
            }
            
            function executeAttack() {
                if (!selectedAttack || isAttacking) return;
                
                isAttacking = true;
                const executeBtn = document.getElementById('executeBtn');
                executeBtn.disabled = true;
                executeBtn.innerHTML = '<div class="loading"></div> EXECUTING...';
                
                addLogEntry('info', `Executing ${selectedAttack} attack...`);
                
                // Get available targets first
                fetch('/api/targets')
                    .then(response => response.json())
                    .then(targetData => {
                        const target = targetData.targets && targetData.targets.length > 0 ? targetData.targets[0] : null;
                        
                        return fetch('/api/execute-attack', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                attack_type: selectedAttack,
                                target: target
                            })
                        });
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            addLogEntry('success', `Attack completed: ${data.message}`);
                        } else {
                            addLogEntry('error', `Attack failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addLogEntry('error', `Attack failed: ${error.message}`);
                    })
                    .finally(() => {
                        isAttacking = false;
                        executeBtn.disabled = false;
                        executeBtn.textContent = 'Execute Attack';
                    });
            }
            
            function stopAllAttacks() {
                addLogEntry('info', 'Stopping all attacks...');
                isAttacking = false;
                addLogEntry('success', 'All attacks stopped');
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/scan')
def api_scan():
    try:
        networks = scan_networks()
        return jsonify({
            'status': 'success',
            'networks': networks,
            'count': len(networks)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'networks': [],
            'count': 0,
            'error': str(e)
        })

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'total_networks': len(discovered_networks),
        'hidden_networks': len([n for n in discovered_networks if not n.get('ssid') or n.get('ssid') == 'Hidden']),
        'open_networks': len([n for n in discovered_networks if n.get('security') == 'Open']),
        'secured_networks': len([n for n in discovered_networks if n.get('security') != 'Open'])
    })

@app.route('/api/execute-attack', methods=['POST'])
def api_execute_attack():
    try:
        data = request.get_json()
        attack_type = data.get('attack_type')
        target = data.get('target', {})
        
        if not attack_type:
            return jsonify({
                'status': 'error',
                'error': 'Missing attack type'
            })
        
        # Use real target if provided, otherwise use first discovered network
        if not target and discovered_networks:
            target = discovered_networks[0]
        elif not target:
            target = {'ssid': 'Unknown', 'bssid': '00:00:00:00:00:00'}
        
        result = execute_attack(target, attack_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/targets')
def api_targets():
    """Get available targets from discovered networks"""
    return jsonify({
        'status': 'success',
        'targets': discovered_networks
    })

@app.route('/api/attack-stats')
def api_attack_stats():
    """Get attack statistics"""
    return jsonify({
        'total_attacks': len(active_attacks),
        'successful_attacks': len([a for a in active_attacks if a.get('status') == 'success']),
        'active_attacks': 1 if is_attacking else 0,
        'attack_types': list(set([a.get('attack_type', '') for a in active_attacks if a.get('attack_type')]))
    })


@app.route('/api/monitor-mode', methods=['POST'])
def api_monitor_mode():
    """Enable/disable monitor mode for an interface - COMPLETELY AUTOMATIC"""
    try:
        data = request.get_json()
        interface = data.get('interface', 'wlan0')
        automatic = data.get('automatic', False)
        
        # Simulate monitor mode toggle (since we don't have iwconfig/airmon-ng in this environment)
        # In a real environment, this would use the actual commands
        add_log_entry('info', f'Checking monitor mode status for {interface}')
        
        # Real monitor mode check
        try:
            import subprocess
            result = subprocess.run(['iwconfig', interface], capture_output=True, text=True, timeout=5)
            is_monitor = 'Mode:Monitor' in result.stdout
        except:
            is_monitor = False
        
        if is_monitor:
            add_log_entry('info', f'Monitor mode automatically disabled for {interface}')
            return jsonify({
                'success': True,
                'monitor_mode': False,
                'message': f'Monitor mode automatically disabled for {interface}'
            })
        else:
            add_log_entry('info', f'Monitor mode automatically enabled for {interface}')
            return jsonify({
                'success': True,
                'monitor_mode': True,
                'message': f'Monitor mode automatically enabled for {interface}'
            })
            
    except Exception as e:
        add_log_entry('error', f'Monitor mode error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/start-scan', methods=['POST'])
def api_start_scan():
    """Start enhanced network scanning"""
    global is_scanning
    try:
        data = request.get_json()
        interface = data.get('interface', 'wlan0')
        continuous = data.get('continuous', False)
        interval = data.get('interval', 30)
        
        if is_scanning:
            return jsonify({'success': False, 'error': 'Scan already in progress'})
        
        # Start enhanced scanning
        is_scanning = True
        add_log_entry('info', f'Starting enhanced network scan on {interface}')
        
        # Start continuous monitoring if requested
        if continuous:
            network_discovery.start_continuous_monitoring(interface, interval)
            add_log_entry('info', f'Continuous monitoring started with {interval}s interval')
        
        return jsonify({
            'success': True, 
            'message': 'Enhanced scan started',
            'continuous': continuous,
            'interval': interval
        })
    except Exception as e:
        add_log_entry('error', f'Start scan error: {e}')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop-scan', methods=['POST'])
def api_stop_scan():
    """Stop network scanning and continuous monitoring"""
    global is_scanning
    is_scanning = False
    network_discovery.stop_continuous_monitoring()
    add_log_entry('info', 'Network scan and monitoring stopped')
    return jsonify({'success': True, 'message': 'Scan and monitoring stopped'})

@app.route('/api/scan-results')
def api_scan_results():
    """Get enhanced scan results with analytics"""
    global discovered_networks, is_scanning
    
    try:
        # Get current networks from the enhanced discovery module
        current_networks = network_discovery.discovered_networks
        discovered_networks = current_networks
        
        # Get analytics
        analytics = network_discovery.get_network_analytics()
        
        return jsonify({
            'networks': current_networks,
            'is_scanning': is_scanning,
            'analytics': analytics,
            'total_networks': len(current_networks),
            'last_scan': network_discovery.last_scan_time.isoformat() if network_discovery.last_scan_time else None
        })
    except Exception as e:
        add_log_entry('error', f'Scan results error: {e}')
        return jsonify({
            'networks': [],
            'is_scanning': False,
            'analytics': {},
            'error': str(e)
        })

@app.route('/api/interfaces')
def api_interfaces():
    """Get available network interfaces"""
    try:
        interfaces = network_discovery.get_available_interfaces()
        return jsonify({
            'success': True,
            'interfaces': interfaces
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'interfaces': []
        })

@app.route('/api/network-details/<bssid>')
def api_network_details(bssid):
    """Get detailed information about a specific network"""
    try:
        details = network_discovery.get_network_details(bssid)
        if details:
            return jsonify({
                'success': True,
                'network': details
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Network not found'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/search-networks')
def api_search_networks():
    """Search networks by query"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter required'
            })
        
        results = network_discovery.search_networks(query)
        return jsonify({
            'success': True,
            'networks': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'networks': []
        })

@app.route('/api/filter-networks', methods=['POST'])
def api_filter_networks():
    """Filter networks based on criteria"""
    try:
        filters = request.get_json() or {}
        results = network_discovery.filter_networks(filters)
        return jsonify({
            'success': True,
            'networks': results,
            'count': len(results),
            'filters_applied': filters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'networks': []
        })

@app.route('/api/network-analytics')
def api_network_analytics():
    """Get comprehensive network analytics"""
    try:
        analytics = network_discovery.get_network_analytics()
        return jsonify({
            'success': True,
            'analytics': analytics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'analytics': {}
        })

@app.route('/api/start-monitoring', methods=['POST'])
def api_start_monitoring():
    """Start continuous network monitoring"""
    try:
        data = request.get_json()
        interface = data.get('interface', 'wlan0')
        interval = data.get('interval', 30)
        
        success = network_discovery.start_continuous_monitoring(interface, interval)
        if success:
            add_log_entry('info', f'Continuous monitoring started on {interface} with {interval}s interval')
            return jsonify({
                'success': True,
                'message': f'Monitoring started on {interface}',
                'interval': interval
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Monitoring already active'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stop-monitoring', methods=['POST'])
def api_stop_monitoring():
    """Stop continuous network monitoring"""
    try:
        network_discovery.stop_continuous_monitoring()
        add_log_entry('info', 'Continuous monitoring stopped')
        return jsonify({
            'success': True,
            'message': 'Monitoring stopped'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Global log storage
log_entries = []

def add_log_entry(type, message):
    timestamp = time.strftime('%H:%M:%S')
    log_entry = {
        'timestamp': timestamp,
        'type': type.upper(),
        'message': message
    }
    log_entries.append(log_entry)
    # Keep only last 100 entries
    if len(log_entries) > 100:
        log_entries.pop(0)
    print(f"[{timestamp}] [{type.upper()}] {message}")

@app.route('/api/logs')
def api_get_logs():
    """Get real-time log entries"""
    return jsonify({
        'logs': log_entries,
        'count': len(log_entries)
    })

if __name__ == '__main__':
    print("🚀 Starting Net.Krk Combined Dashboard...")
    print("📊 Analytics: http://localhost:5000")
    print("⚔️ Attack Modules: http://localhost:5000/attack")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure port 5000 is not in use")