from flask import Flask, jsonify, request, session
import subprocess
import re
import time
import json
import os

app = Flask(__name__)
app.secret_key = 'netkrak_attack_2024'

# Global state
is_attacking = False
active_attacks = []
attack_results = {}

def add_log_entry(type, message):
    """Add log entry"""
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] [{type.upper()}] {message}")

def execute_attack(target, attack_type):
    """Execute network attack"""
    global is_attacking
    is_attacking = True
    add_log_entry('info', f'Starting {attack_type} attack on {target.get("ssid", "Hidden")}')
    
    # Simulate attack execution
    time.sleep(2)
    
    # Mock attack results
    result = {
        'status': 'success',
        'attack_type': attack_type,
        'target': target,
        'timestamp': time.time(),
        'message': f'{attack_type} attack completed successfully'
    }
    
    active_attacks.append(result)
    attack_results[attack_type] = result
    
    is_attacking = False
    add_log_entry('success', f'{attack_type} attack completed')
    return result

def get_attack_stats():
    """Get attack statistics"""
    return {
        'total_attacks': len(active_attacks),
        'successful_attacks': len([a for a in active_attacks if a['status'] == 'success']),
        'active_attacks': len([a for a in active_attacks if a['status'] == 'running']),
        'attack_types': list(set([a['attack_type'] for a in active_attacks])),
        'last_attack': active_attacks[-1] if active_attacks else None
    }

@app.route('/')
def home():
    # Read the new dashboard HTML file and modify for attack mode
    try:
        with open('new_dash.html', 'r') as f:
            html_content = f.read()
        
        # Modify for attack dashboard
        html_content = html_content.replace(
            '<title>net.krak - WiFi Penetration Suite v2.0</title>',
            '<title>net.krak - Attack Dashboard v2.0</title>'
        )
        
        # Replace mock data with real API calls
        html_content = html_content.replace(
            '// Simulate API call with mock data\n                await new Promise(resolve => setTimeout(resolve, 3000));\n                \n                // Use mock networks for demonstration\n                const networks = mockNetworks;',
            '''// Real API call
                const response = await fetch('/api/scan');
                const data = await response.json();
                const networks = data.networks || [];'''
        )
        
        # Add attack-specific modifications
        html_content = html_content.replace(
            'net.krak v2.0',
            'net.krak ATTACK v2.0'
        )
        
        return html_content
    except FileNotFoundError:
        # Fallback to original attack dashboard if new_dash.html not found
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Net.Krk - Attack Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

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

            .status-panel {
                background: rgba(255, 0, 136, 0.05);
                border: 1px solid #ff0088;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: center;
            }

            .status-beacon {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #00ff00;
                margin-right: 10px;
                animation: beaconPulse 2s ease-in-out infinite;
            }

            .status-beacon.attacking {
                background: #ff0000;
                animation: attackBeacon 0.3s ease-in-out infinite;
            }

            @keyframes beaconPulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.1); opacity: 0.8; }
            }

            @keyframes attackBeacon {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.5); }
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }

            .stat-card {
                background: rgba(255, 0, 136, 0.05);
                border: 1px solid #ff0088;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s ease;
            }

            .stat-card:hover {
                background: rgba(255, 0, 136, 0.1);
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

            .attack-panel {
                background: rgba(255, 0, 136, 0.05);
                border: 1px solid #ff0088;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }

            .section-title {
                color: #ff0088;
                font-size: 1.3em;
                margin-bottom: 15px;
                text-align: center;
                text-transform: uppercase;
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

            .attack-status {
                color: #00ff00;
                font-size: 0.7em;
                text-transform: uppercase;
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

            .button.danger {
                background: linear-gradient(45deg, #ff0000, #ff8800);
            }

            .target-panel {
                background: rgba(0, 255, 255, 0.05);
                border: 1px solid #00ffff;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }

            .target-item {
                background: rgba(255, 0, 136, 0.05);
                border: 1px solid #ff0088;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .target-item:hover {
                background: rgba(255, 0, 136, 0.1);
                transform: translateX(5px);
            }

            .target-item.selected {
                background: rgba(255, 0, 136, 0.2);
                border-color: #ff0088;
            }

            .target-ssid {
                color: #ff0088;
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 5px;
            }

            .target-details {
                color: #00ffff;
                font-size: 0.9em;
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

            .results-panel {
                background: rgba(0, 255, 255, 0.05);
                border: 1px solid #00ffff;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }

            .result-item {
                background: rgba(0, 255, 255, 0.1);
                border: 1px solid #00ffff;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
            }

            @media (max-width: 768px) {
                .stats-grid {
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                }
                
                .attack-grid {
                    grid-template-columns: 1fr;
                }
                
                .title {
                    font-size: 2em;
                }
                
                .container {
                    padding: 10px;
                }
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
                <a href="/analytics" class="nav-button">📊 Analytics</a>
                <a href="/" class="nav-button active">⚔️ Attack Modules</a>
            </div>
            
            <div class="status-panel">
                <span class="status-beacon" id="statusBeacon"></span>
                <span id="statusText">System Ready</span>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card">
                    <div class="stat-number" id="totalAttacks">0</div>
                    <div class="stat-label">Total Attacks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="successfulAttacks">0</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="activeAttacks">0</div>
                    <div class="stat-label">Active</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="attackTypes">0</div>
                    <div class="stat-label">Attack Types</div>
                </div>
            </div>
            
            <div class="target-panel">
                <h3 class="section-title">🎯 Target Selection</h3>
                <div style="text-align: center; margin-bottom: 15px;">
                    <button class="button" onclick="loadTargets()">Load Targets</button>
                    <button class="button" onclick="clearTargets()">Clear Selection</button>
                </div>
                <div id="targetList">
                    <div class="log-entry log-info">Click "Load Targets" to get available networks</div>
                </div>
            </div>
            
            <div class="attack-panel">
                <h3 class="section-title">⚔️ Attack Modules</h3>
                <div class="attack-grid">
                    <div class="attack-module" onclick="selectAttack('deauth')">
                        <div class="attack-icon">📡</div>
                        <div class="attack-name">Deauth Attack</div>
                        <div class="attack-description">Disconnect devices from target network</div>
                        <div class="attack-status">Ready</div>
                    </div>
                    <div class="attack-module" onclick="selectAttack('handshake')">
                        <div class="attack-icon">🤝</div>
                        <div class="attack-name">Handshake Capture</div>
                        <div class="attack-description">Capture WPA/WPA2 handshakes</div>
                        <div class="attack-status">Ready</div>
                    </div>
                    <div class="attack-module" onclick="selectAttack('evil_twin')">
                        <div class="attack-icon">👥</div>
                        <div class="attack-name">Evil Twin</div>
                        <div class="attack-description">Create fake access point</div>
                        <div class="attack-status">Ready</div>
                    </div>
                    <div class="attack-module" onclick="selectAttack('wps')">
                        <div class="attack-icon">🔐</div>
                        <div class="attack-name">WPS Attack</div>
                        <div class="attack-description">Exploit WPS vulnerabilities</div>
                        <div class="attack-status">Ready</div>
                    </div>
                    <div class="attack-module" onclick="selectAttack('fragmentation')">
                        <div class="attack-icon">💥</div>
                        <div class="attack-name">Fragmentation</div>
                        <div class="attack-description">Fragmentation attack on WEP</div>
                        <div class="attack-status">Ready</div>
                    </div>
                    <div class="attack-module" onclick="selectAttack('credential')">
                        <div class="attack-icon">🔑</div>
                        <div class="attack-name">Credential Harvest</div>
                        <div class="attack-description">Capture login credentials</div>
                        <div class="attack-status">Ready</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <button class="button" id="executeBtn" onclick="executeAttack()" disabled>Execute Attack</button>
                    <button class="button danger" onclick="stopAllAttacks()">Stop All Attacks</button>
                </div>
            </div>
            
            <div class="results-panel">
                <h3 class="section-title">📊 Attack Results</h3>
                <div id="attackResults">
                    <div class="log-entry log-info">No attacks executed yet</div>
                </div>
            </div>
            
            <div class="activity-log" id="activityLog">
                <div class="log-entry log-info">[INFO] Attack dashboard initialized</div>
                <div class="log-entry log-success">[SUCCESS] Ready for attack operations</div>
            </div>
        </div>
        
        <script>
            let selectedTarget = null;
            let selectedAttack = null;
            let isAttacking = false;
            let availableTargets = [];
            
            function addLogEntry(type, message) {
                const log = document.getElementById('activityLog');
                const entry = document.createElement('div');
                entry.className = `log-entry log-${type}`;
                entry.textContent = `[${type.toUpperCase()}] ${message}`;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
            }
            
            function updateStatus(status, text) {
                const beacon = document.getElementById('statusBeacon');
                const statusText = document.getElementById('statusText');
                
                beacon.className = `status-beacon ${status}`;
                statusText.textContent = text;
            }
            
            function updateStats() {
                fetch('/api/attack-stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('totalAttacks').textContent = data.total_attacks;
                        document.getElementById('successfulAttacks').textContent = data.successful_attacks;
                        document.getElementById('activeAttacks').textContent = data.active_attacks;
                        document.getElementById('attackTypes').textContent = data.attack_types.length;
                    });
            }
            
            function loadTargets() {
                addLogEntry('info', 'Loading available targets...');
                
                fetch('/api/targets')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            availableTargets = data.targets;
                            displayTargets(data.targets);
                            addLogEntry('success', `Loaded ${data.targets.length} targets`);
                        } else {
                            addLogEntry('error', `Failed to load targets: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addLogEntry('error', `Failed to load targets: ${error.message}`);
                    });
            }
            
            function displayTargets(targets) {
                const container = document.getElementById('targetList');
                container.innerHTML = '';
                
                if (targets.length === 0) {
                    container.innerHTML = '<div class="log-entry log-warning">No targets available</div>';
                    return;
                }
                
                targets.forEach(target => {
                    const div = document.createElement('div');
                    div.className = 'target-item';
                    div.onclick = () => selectTarget(target, div);
                    
                    div.innerHTML = `
                        <div class="target-ssid">${target.ssid || 'Hidden Network'}</div>
                        <div class="target-details">
                            BSSID: ${target.bssid} | Signal: ${target.signal}dBm | Security: ${target.security || 'Unknown'}
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
            
            function selectTarget(target, element) {
                document.querySelectorAll('.target-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                element.classList.add('selected');
                selectedTarget = target;
                
                addLogEntry('info', `Selected target: ${target.ssid || 'Hidden'} (${target.bssid})`);
                
                if (selectedAttack) {
                    document.getElementById('executeBtn').disabled = false;
                }
            }
            
            function selectAttack(attackType) {
                document.querySelectorAll('.attack-module').forEach(module => {
                    module.classList.remove('active');
                });
                
                event.target.closest('.attack-module').classList.add('active');
                selectedAttack = attackType;
                
                addLogEntry('info', `Selected attack: ${attackType}`);
                
                if (selectedTarget) {
                    document.getElementById('executeBtn').disabled = false;
                }
            }
            
            function executeAttack() {
                if (!selectedTarget || !selectedAttack || isAttacking) return;
                
                isAttacking = true;
                updateStatus('attacking', 'EXECUTING ATTACK...');
                
                const executeBtn = document.getElementById('executeBtn');
                executeBtn.disabled = true;
                executeBtn.innerHTML = '<div class="loading"></div> EXECUTING...';
                
                addLogEntry('info', `Executing ${selectedAttack} attack on ${selectedTarget.ssid || 'Hidden'}`);
                
                fetch('/api/execute-attack', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        target: selectedTarget,
                        attack_type: selectedAttack
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry('success', `Attack completed: ${data.message}`);
                        displayAttackResult(data);
                        updateStats();
                    } else {
                        addLogEntry('error', `Attack failed: ${data.error}`);
                    }
                })
                .catch(error => {
                    addLogEntry('error', `Attack failed: ${error.message}`);
                })
                .finally(() => {
                    isAttacking = false;
                    updateStatus('ready', 'System Ready');
                    executeBtn.disabled = false;
                    executeBtn.textContent = 'Execute Attack';
                });
            }
            
            function displayAttackResult(result) {
                const container = document.getElementById('attackResults');
                const div = document.createElement('div');
                div.className = 'result-item';
                
                div.innerHTML = `
                    <div><strong>Attack:</strong> ${result.attack_type}</div>
                    <div><strong>Target:</strong> ${result.target.ssid || 'Hidden'} (${result.target.bssid})</div>
                    <div><strong>Status:</strong> ${result.status}</div>
                    <div><strong>Time:</strong> ${new Date(result.timestamp * 1000).toLocaleTimeString()}</div>
                    <div><strong>Message:</strong> ${result.message}</div>
                `;
                
                container.appendChild(div);
            }
            
            function stopAllAttacks() {
                addLogEntry('info', 'Stopping all attacks...');
                isAttacking = false;
                updateStatus('ready', 'System Ready');
                
                const executeBtn = document.getElementById('executeBtn');
                executeBtn.disabled = false;
                executeBtn.textContent = 'Execute Attack';
                
                addLogEntry('success', 'All attacks stopped');
            }
            
            function clearTargets() {
                selectedTarget = null;
                document.querySelectorAll('.target-item').forEach(item => {
                    item.classList.remove('selected');
                });
                document.getElementById('executeBtn').disabled = true;
                addLogEntry('info', 'Target selection cleared');
            }
            
            // Auto-refresh every 30 seconds
            setInterval(() => {
                if (!isAttacking) {
                    updateStats();
                }
            }, 30000);
            
            // Initialize
            updateStats();
        </script>
    </body>
    </html>
    '''

@app.route('/api/targets')
def api_targets():
    """Get available targets"""
    try:
        # Mock targets for demonstration
        targets = [
            {'ssid': 'HomeWiFi', 'bssid': '00:11:22:33:44:55', 'signal': -45, 'security': 'WPA2'},
            {'ssid': 'Office_Network', 'bssid': '00:11:22:33:44:66', 'signal': -60, 'security': 'WPA2'},
            {'ssid': 'Public_WiFi', 'bssid': '00:11:22:33:44:77', 'signal': -75, 'security': 'Open'},
            {'ssid': 'Hidden_Network', 'bssid': '00:11:22:33:44:88', 'signal': -80, 'security': 'WPA2'}
        ]
        
        return jsonify({
            'status': 'success',
            'targets': targets
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'targets': [],
            'error': str(e)
        })

@app.route('/api/execute-attack', methods=['POST'])
def api_execute_attack():
    """Execute attack"""
    try:
        data = request.get_json()
        target = data.get('target')
        attack_type = data.get('attack_type')
        
        if not target or not attack_type:
            return jsonify({
                'status': 'error',
                'error': 'Missing target or attack type'
            })
        
        result = execute_attack(target, attack_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/attack-stats')
def api_attack_stats():
    """Get attack statistics"""
    return jsonify(get_attack_stats())

if __name__ == '__main__':
    print("🚀 Starting Net.Krk Attack Dashboard...")
    print("⚔️ Attack Modules: http://localhost:5001")
    print("📊 Analytics: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure port 5001 is not in use")