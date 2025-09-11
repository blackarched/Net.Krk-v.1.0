from flask import Flask, jsonify, request
import sys
import time
import subprocess
import re
import json
import os

app = Flask(__name__)

# Global state
is_scanning = False
is_attacking = False
selected_target = None
active_vectors = []
system_status = {}

def add_log_entry(type, message):
    """Add log entry"""
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] [{type.upper()}] {message}")

def update_status(status, text):
    """Update status"""
    print(f"Status: {status} - {text}")

def get_system_status():
    """Get system status"""
    return {
        'platform': sys.platform,
        'python_version': sys.version,
        'status': 'online',
        'interfaces': ['wlan0', 'wlan1']  # Mock interfaces
    }

def scan_networks():
    """Scan for WiFi networks"""
    global is_scanning
    is_scanning = True
    add_log_entry('info', 'Starting network scan...')
    
    networks = []
    try:
        result = subprocess.run(['iwlist', 'scan'], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            networks = parse_iwlist(result.stdout)
            add_log_entry('success', f'Found {len(networks)} networks')
        else:
            add_log_entry('error', 'iwlist scan failed')
    except Exception as e:
        add_log_entry('error', f'Scan error: {e}')
    
    is_scanning = False
    return networks

def parse_iwlist(output):
    """Parse iwlist output"""
    networks = []
    current = {}
    
    for line in output.split('\n'):
        if 'Cell' in line and 'Address:' in line:
            if current:
                networks.append(current)
            current = {}
            bssid = re.search(r'Address: ([0-9A-Fa-f:]{17})', line)
            if bssid:
                current['bssid'] = bssid.group(1)
        elif 'ESSID:' in line:
            ssid = re.search(r'ESSID:"([^"]*)"', line)
            if ssid:
                current['ssid'] = ssid.group(1) or 'Hidden'
        elif 'Signal level=' in line:
            signal = re.search(r'Signal level=(-?\d+)', line)
            if signal:
                current['signal'] = int(signal.group(1))
        elif 'Frequency:' in line:
            freq = re.search(r'Frequency:(\d+\.\d+)', line)
            if freq:
                current['channel'] = freq_to_channel(float(freq.group(1)))
        elif 'Encryption key:' in line:
            current['security'] = 'WPA2' if 'on' in line else 'Open'
    
    if current:
        networks.append(current)
    
    return networks

def freq_to_channel(freq):
    """Convert frequency to channel"""
    if 2412 <= freq <= 2484:
        return int((freq - 2412) / 5) + 1
    elif 5170 <= freq <= 5825:
        return int((freq - 5000) / 5)
    return 0

def attack_network(target, attack_type):
    """Simulate network attack"""
    global is_attacking
    is_attacking = True
    add_log_entry('info', f'Starting {attack_type} attack on {target}')
    
    # Simulate attack progress
    time.sleep(2)
    add_log_entry('success', f'{attack_type} attack completed on {target}')
    
    is_attacking = False
    return {'status': 'success', 'message': f'{attack_type} attack completed'}

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>net.krak - WiFi Penetration Suite v2.0</title>
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
                max-width: 1200px;
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

            .status-panel {
                background: rgba(0, 255, 255, 0.05);
                border: 1px solid #00ffff;
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

            .status-beacon.scanning {
                background: #ffff00;
                animation: scanBeacon 0.6s ease-in-out infinite;
            }

            .status-beacon.attacking {
                background: #ff0000;
                animation: attackBeacon 0.3s ease-in-out infinite;
            }

            @keyframes beaconPulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.1); opacity: 0.8; }
            }

            @keyframes scanBeacon {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.3); }
            }

            @keyframes attackBeacon {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.5); }
            }

            .control-panel {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 20px 0;
            }

            .scan-section, .attack-section {
                background: rgba(255, 0, 136, 0.05);
                border: 1px solid #ff0088;
                border-radius: 10px;
                padding: 20px;
            }

            .section-title {
                color: #ff0088;
                font-size: 1.2em;
                margin-bottom: 15px;
                text-align: center;
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

            .network-list {
                max-height: 400px;
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

            .network-item.selected {
                background: rgba(255, 0, 136, 0.1);
                border-color: #ff0088;
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

            .attack-vectors {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin: 20px 0;
            }

            .attack-vector {
                background: rgba(255, 0, 136, 0.05);
                border: 1px solid #ff0088;
                border-radius: 5px;
                padding: 10px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
            }

            .attack-vector:hover {
                background: rgba(255, 0, 136, 0.1);
                transform: scale(1.02);
            }

            .attack-vector.active {
                background: rgba(255, 0, 136, 0.2);
                border-color: #ff0088;
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

            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }

            .stat-card {
                background: rgba(0, 255, 255, 0.05);
                border: 1px solid #00ffff;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
            }

            .stat-number {
                font-size: 2em;
                color: #ff0088;
                font-weight: bold;
            }

            .stat-label {
                color: #00ffff;
                font-size: 0.9em;
                margin-top: 5px;
            }

            @media (max-width: 768px) {
                .control-panel {
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
                <p class="subtitle">WiFi Penetration Suite v2.0 - Mobile Edition</p>
            </div>
            
            <div class="status-panel">
                <span class="status-beacon" id="statusBeacon"></span>
                <span id="statusText">System Ready</span>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-number" id="networkCount">0</div>
                    <div class="stat-label">Networks Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="attackCount">0</div>
                    <div class="stat-label">Active Attacks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="successCount">0</div>
                    <div class="stat-label">Successful</div>
                </div>
            </div>
            
            <div class="control-panel">
                <div class="scan-section">
                    <h3 class="section-title">🔍 Network Discovery</h3>
                    <div style="text-align: center;">
                        <button class="button" id="scanBtn" onclick="scanNetworks()">Scan Networks</button>
                        <button class="button" onclick="refreshNetworks()">Refresh</button>
                    </div>
                    <div class="network-list" id="networkList">
                        <div class="log-entry log-info">Click "Scan Networks" to discover WiFi networks</div>
                    </div>
                </div>
                
                <div class="attack-section">
                    <h3 class="section-title">⚔️ Attack Vectors</h3>
                    <div class="attack-vectors">
                        <div class="attack-vector" onclick="selectAttack('deauth')">
                            <div>Deauth Attack</div>
                        </div>
                        <div class="attack-vector" onclick="selectAttack('handshake')">
                            <div>Handshake Capture</div>
                        </div>
                        <div class="attack-vector" onclick="selectAttack('evil_twin')">
                            <div>Evil Twin</div>
                        </div>
                        <div class="attack-vector" onclick="selectAttack('wps')">
                            <div>WPS Attack</div>
                        </div>
                        <div class="attack-vector" onclick="selectAttack('fragmentation')">
                            <div>Fragmentation</div>
                        </div>
                        <div class="attack-vector" onclick="selectAttack('credential')">
                            <div>Credential Harvest</div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 15px;">
                        <button class="button" id="attackBtn" onclick="startAttack()" disabled>Start Attack</button>
                        <button class="button" onclick="stopAttack()">Stop Attack</button>
                    </div>
                </div>
            </div>
            
            <div class="activity-log" id="activityLog">
                <div class="log-entry log-info">[INFO] System initialized</div>
                <div class="log-entry log-success">[SUCCESS] Ready for operations</div>
            </div>
        </div>
        
        <script>
            let selectedNetwork = null;
            let selectedAttack = null;
            let isScanning = false;
            let isAttacking = false;
            
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
                const networks = document.querySelectorAll('.network-item').length;
                document.getElementById('networkCount').textContent = networks;
                document.getElementById('attackCount').textContent = isAttacking ? 1 : 0;
            }
            
            function scanNetworks() {
                if (isScanning) return;
                
                isScanning = true;
                updateStatus('scanning', 'SCANNING...');
                
                const scanBtn = document.getElementById('scanBtn');
                scanBtn.disabled = true;
                scanBtn.innerHTML = '<div class="loading"></div> SCANNING...';
                
                addLogEntry('info', 'Starting network scan...');
                
                fetch('/api/scan')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            addLogEntry('success', `Found ${data.networks.length} networks`);
                            displayNetworks(data.networks);
                        } else {
                            addLogEntry('error', `Scan failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addLogEntry('error', `Scan failed: ${error.message}`);
                    })
                    .finally(() => {
                        isScanning = false;
                        updateStatus('ready', 'System Ready');
                        scanBtn.disabled = false;
                        scanBtn.textContent = 'Scan Networks';
                    });
            }
            
            function displayNetworks(networks) {
                const container = document.getElementById('networkList');
                container.innerHTML = '';
                
                if (networks.length === 0) {
                    container.innerHTML = '<div class="log-entry log-warning">No networks found</div>';
                    return;
                }
                
                networks.forEach(net => {
                    const div = document.createElement('div');
                    div.className = 'network-item';
                    div.onclick = () => selectNetwork(net, div);
                    
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
                
                updateStats();
            }
            
            function selectNetwork(network, element) {
                // Remove previous selection
                document.querySelectorAll('.network-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // Select new network
                element.classList.add('selected');
                selectedNetwork = network;
                
                addLogEntry('info', `Selected network: ${network.ssid || 'Hidden'}`);
                
                // Enable attack button if attack is selected
                if (selectedAttack) {
                    document.getElementById('attackBtn').disabled = false;
                }
            }
            
            function selectAttack(attackType) {
                // Remove previous selection
                document.querySelectorAll('.attack-vector').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Select new attack
                event.target.closest('.attack-vector').classList.add('active');
                selectedAttack = attackType;
                
                addLogEntry('info', `Selected attack: ${attackType}`);
                
                // Enable attack button if network is selected
                if (selectedNetwork) {
                    document.getElementById('attackBtn').disabled = false;
                }
            }
            
            function startAttack() {
                if (!selectedNetwork || !selectedAttack || isAttacking) return;
                
                isAttacking = true;
                updateStatus('attacking', 'ATTACKING...');
                
                const attackBtn = document.getElementById('attackBtn');
                attackBtn.disabled = true;
                attackBtn.innerHTML = '<div class="loading"></div> ATTACKING...';
                
                addLogEntry('info', `Starting ${selectedAttack} attack on ${selectedNetwork.ssid || 'Hidden'}`);
                
                fetch('/api/attack', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        target: selectedNetwork,
                        attack_type: selectedAttack
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogEntry('success', `Attack completed: ${data.message}`);
                        document.getElementById('successCount').textContent = 
                            parseInt(document.getElementById('successCount').textContent) + 1;
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
                    attackBtn.disabled = false;
                    attackBtn.textContent = 'Start Attack';
                });
            }
            
            function stopAttack() {
                if (!isAttacking) return;
                
                addLogEntry('info', 'Stopping attack...');
                isAttacking = false;
                updateStatus('ready', 'System Ready');
                
                const attackBtn = document.getElementById('attackBtn');
                attackBtn.disabled = false;
                attackBtn.textContent = 'Start Attack';
            }
            
            function refreshNetworks() {
                addLogEntry('info', 'Refreshing networks...');
                scanNetworks();
            }
            
            // Auto-refresh every 30 seconds
            setInterval(() => {
                if (!isScanning && !isAttacking) {
                    addLogEntry('info', 'System heartbeat - ' + new Date().toLocaleTimeString());
                }
            }, 30000);
            
            // Initialize
            updateStats();
        </script>
    </body>
    </html>
    '''

@app.route('/api/scan')
def api_scan():
    """Scan for WiFi networks"""
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

@app.route('/api/attack', methods=['POST'])
def api_attack():
    """Execute network attack"""
    try:
        data = request.get_json()
        target = data.get('target')
        attack_type = data.get('attack_type')
        
        if not target or not attack_type:
            return jsonify({
                'status': 'error',
                'error': 'Missing target or attack type'
            })
        
        result = attack_network(target, attack_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify(get_system_status())

if __name__ == '__main__':
    print("🚀 Starting Net.Krk Full Dashboard...")
    print("📱 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure port 5000 is not in use")