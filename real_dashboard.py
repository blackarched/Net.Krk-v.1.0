#!/usr/bin/env python3
"""
Real Net.Krk Dashboard for Pydroid with ACTUAL network scanning
"""

from flask import Flask, jsonify
import sys
import time
import subprocess
import re
import json
import os

app = Flask(__name__)

def get_real_wifi_networks():
    """Get REAL WiFi networks using Android system commands"""
    networks = []
    
    try:
        # Method 1: Try using iwlist (if available)
        try:
            result = subprocess.run(['iwlist', 'scan'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                networks = parse_iwlist_output(result.stdout)
                if networks:
                    return networks
        except:
            pass
        
        # Method 2: Try using nmcli (NetworkManager)
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,BSSID,SIGNAL,FREQ', 'dev', 'wifi', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                networks = parse_nmcli_output(result.stdout)
                if networks:
                    return networks
        except:
            pass
        
        # Method 3: Try using wpa_supplicant scan
        try:
            # Trigger scan
            subprocess.run(['wpa_cli', 'scan'], capture_output=True, timeout=5)
            time.sleep(2)  # Wait for scan to complete
            
            # Get results
            result = subprocess.run(['wpa_cli', 'scan_results'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                networks = parse_wpa_cli_output(result.stdout)
                if networks:
                    return networks
        except:
            pass
        
        # Method 4: Try reading from /proc/net/wireless (if available)
        try:
            with open('/proc/net/wireless', 'r') as f:
                content = f.read()
                networks = parse_proc_wireless(content)
                if networks:
                    return networks
        except:
            pass
        
        # Method 5: Try using Android's dumpsys wifi (if we have root)
        try:
            result = subprocess.run(['su', '-c', 'dumpsys wifi'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                networks = parse_dumpsys_wifi(result.stdout)
                if networks:
                    return networks
        except:
            pass
            
    except Exception as e:
        print(f"Error scanning networks: {e}")
    
    # If all methods fail, return empty list
    return []

def parse_iwlist_output(output):
    """Parse iwlist scan output"""
    networks = []
    current_net = {}
    
    for line in output.split('\n'):
        line = line.strip()
        
        if 'Cell' in line and 'Address:' in line:
            if current_net:
                networks.append(current_net)
            current_net = {}
            # Extract BSSID
            bssid_match = re.search(r'Address: ([0-9A-Fa-f:]{17})', line)
            if bssid_match:
                current_net['bssid'] = bssid_match.group(1)
        
        elif 'ESSID:' in line:
            ssid_match = re.search(r'ESSID:"([^"]*)"', line)
            if ssid_match:
                current_net['ssid'] = ssid_match.group(1) or 'Hidden'
        
        elif 'Signal level=' in line:
            signal_match = re.search(r'Signal level=(-?\d+)', line)
            if signal_match:
                current_net['signal'] = int(signal_match.group(1))
        
        elif 'Frequency:' in line:
            freq_match = re.search(r'Frequency:(\d+\.\d+)', line)
            if freq_match:
                freq = float(freq_match.group(1))
                current_net['channel'] = freq_to_channel(freq)
    
    if current_net:
        networks.append(current_net)
    
    return networks

def parse_nmcli_output(output):
    """Parse nmcli output"""
    networks = []
    
    for line in output.split('\n'):
        if line.strip():
            parts = line.split(':')
            if len(parts) >= 4:
                ssid = parts[0] if parts[0] != '--' else 'Hidden'
                bssid = parts[1] if parts[1] != '--' else 'Unknown'
                signal = parts[2] if parts[2] != '--' else '-100'
                freq = parts[3] if parts[3] != '--' else '0'
                
                try:
                    signal_int = int(signal)
                    freq_float = float(freq)
                    channel = freq_to_channel(freq_float)
                except:
                    signal_int = -100
                    channel = 0
                
                networks.append({
                    'ssid': ssid,
                    'bssid': bssid,
                    'signal': signal_int,
                    'channel': channel
                })
    
    return networks

def parse_wpa_cli_output(output):
    """Parse wpa_cli scan results"""
    networks = []
    
    for line in output.split('\n'):
        if line.strip() and not line.startswith('bssid'):
            parts = line.split('\t')
            if len(parts) >= 4:
                bssid = parts[0]
                freq = parts[1]
                signal = parts[2]
                ssid = parts[3] if len(parts) > 3 else 'Hidden'
                
                try:
                    signal_int = int(signal)
                    freq_float = float(freq)
                    channel = freq_to_channel(freq_float)
                except:
                    signal_int = -100
                    channel = 0
                
                networks.append({
                    'ssid': ssid,
                    'bssid': bssid,
                    'signal': signal_int,
                    'channel': channel
                })
    
    return networks

def parse_proc_wireless(content):
    """Parse /proc/net/wireless output"""
    networks = []
    lines = content.split('\n')
    
    for line in lines[2:]:  # Skip header lines
        if line.strip():
            parts = line.split()
            if len(parts) >= 3:
                interface = parts[0].rstrip(':')
                status = parts[1]
                link = parts[2]
                
                if status == '1':  # Interface is up
                    networks.append({
                        'ssid': f'Interface_{interface}',
                        'bssid': 'Unknown',
                        'signal': int(link) if link.isdigit() else -100,
                        'channel': 0
                    })
    
    return networks

def parse_dumpsys_wifi(output):
    """Parse Android dumpsys wifi output"""
    networks = []
    
    # Look for scan results in dumpsys output
    in_scan_results = False
    for line in output.split('\n'):
        if 'Scan Results:' in line:
            in_scan_results = True
            continue
        
        if in_scan_results and line.strip():
            if 'BSSID:' in line:
                # Extract BSSID
                bssid_match = re.search(r'BSSID: ([0-9A-Fa-f:]{17})', line)
                if bssid_match:
                    current_net = {'bssid': bssid_match.group(1)}
            elif 'SSID:' in line:
                ssid_match = re.search(r'SSID: ([^,]+)', line)
                if ssid_match:
                    current_net['ssid'] = ssid_match.group(1).strip()
            elif 'RSSI:' in line:
                rssi_match = re.search(r'RSSI: (-?\d+)', line)
                if rssi_match:
                    current_net['signal'] = int(rssi_match.group(1))
                    if 'ssid' in current_net:
                        networks.append(current_net)
    
    return networks

def freq_to_channel(freq):
    """Convert frequency to channel number"""
    if 2412 <= freq <= 2484:
        return int((freq - 2412) / 5) + 1
    elif 5170 <= freq <= 5825:
        return int((freq - 5000) / 5)
    else:
        return 0

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Net.Krk Mobile Dashboard - REAL DATA</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                color: #00ffff; 
                font-family: 'Courier New', monospace; 
                padding: 20px; 
                margin: 0;
                min-height: 100vh;
            }
            .container { max-width: 800px; margin: 0 auto; }
            .title { 
                color: #ff0088; 
                font-size: 2.5em; 
                text-align: center; 
                text-shadow: 0 0 20px #ff0088;
                margin-bottom: 20px; 
            }
            .subtitle { 
                color: #00ffff; 
                text-align: center; 
                margin-bottom: 30px; 
            }
            .status { 
                background: rgba(0, 255, 255, 0.1); 
                border: 1px solid #00ffff; 
                border-radius: 10px; 
                padding: 20px; 
                margin: 20px 0; 
                text-align: center; 
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
                transition: transform 0.3s;
            }
            .button:hover { transform: scale(1.05); }
            .log { 
                background: #000; 
                border: 1px solid #333; 
                border-radius: 5px; 
                padding: 15px; 
                margin: 20px 0; 
                height: 200px; 
                overflow-y: auto; 
                font-size: 12px; 
            }
            .log-entry { margin: 5px 0; padding: 5px; border-radius: 3px; }
            .log-info { color: #00ffff; }
            .log-success { color: #00ff00; }
            .log-warning { color: #ffff00; }
            .log-error { color: #ff0000; }
            .network-item {
                background: rgba(255, 0, 136, 0.1);
                border: 1px solid #ff0088;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
            }
            .network-ssid { color: #ff0088; font-weight: bold; }
            .network-details { color: #00ffff; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="title">net.krak</h1>
            <p class="subtitle">WiFi Penetration Suite v2.0 - REAL DATA</p>
            
            <div class="status">
                <h3>🚀 System Status: ONLINE</h3>
                <p>Real Network Scanning Active</p>
            </div>
            
            <div style="text-align: center;">
                <button class="button" onclick="scanRealNetworks()">🔍 Scan REAL Networks</button>
                <button class="button" onclick="testConnection()">Test Connection</button>
                <button class="button" onclick="showSystemInfo()">System Info</button>
            </div>
            
            <div>
                <h3>📡 Discovered Networks</h3>
                <div id="networks" style="margin: 20px 0;">
                    <div class="log-entry log-info">Click "Scan REAL Networks" to discover actual WiFi networks</div>
                </div>
            </div>
            
            <div>
                <h3>📊 Activity Log</h3>
                <div id="log" class="log">
                    <div class="log-entry log-info">[INFO] Real data dashboard initialized</div>
                    <div class="log-entry log-success">[SUCCESS] Flask server running on port 5000</div>
                    <div class="log-entry log-info">[INFO] Ready for REAL network scanning</div>
                </div>
            </div>
        </div>
        
        <script>
            function addLog(type, message) {
                const log = document.getElementById('log');
                const entry = document.createElement('div');
                entry.className = `log-entry log-${type}`;
                entry.textContent = `[${type.toUpperCase()}] ${message}`;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
            }
            
            function displayNetworks(networks) {
                const container = document.getElementById('networks');
                container.innerHTML = '';
                
                if (networks.length === 0) {
                    container.innerHTML = '<div class="log-entry log-warning">No networks found. Try running scan again.</div>';
                    return;
                }
                
                networks.forEach(net => {
                    const div = document.createElement('div');
                    div.className = 'network-item';
                    div.innerHTML = `
                        <div class="network-ssid">${net.ssid || 'Hidden Network'}</div>
                        <div class="network-details">
                            BSSID: ${net.bssid} | Signal: ${net.signal}dBm | Channel: ${net.channel || 'Unknown'}
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
            
            function scanRealNetworks() {
                addLog('info', 'Starting REAL network scan...');
                fetch('/api/real-scan')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            addLog('success', `Found ${data.networks.length} REAL networks`);
                            displayNetworks(data.networks);
                        } else {
                            addLog('error', `Scan failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addLog('error', `Scan failed: ${error.message}`);
                    });
            }
            
            function testConnection() {
                addLog('info', 'Testing connection...');
                fetch('/api/test')
                    .then(response => response.json())
                    .then(data => {
                        addLog('success', `Connection test: ${data.message}`);
                    })
                    .catch(error => {
                        addLog('error', `Connection failed: ${error.message}`);
                    });
            }
            
            function showSystemInfo() {
                addLog('info', 'Getting system information...');
                fetch('/api/system')
                    .then(response => response.json())
                    .then(data => {
                        addLog('success', `Platform: ${data.platform}`);
                        addLog('info', `Python: ${data.python_version}`);
                        addLog('info', `Status: ${data.status}`);
                    })
                    .catch(error => {
                        addLog('error', `System info failed: ${error.message}`);
                    });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'success',
        'message': 'Connection successful!',
        'timestamp': time.time()
    })

@app.route('/api/real-scan')
def api_real_scan():
    """Scan for REAL WiFi networks"""
    try:
        addLog('info', 'Starting real network scan...')
        networks = get_real_wifi_networks()
        
        if networks:
            return jsonify({
                'status': 'success',
                'networks': networks,
                'count': len(networks),
                'message': f'Found {len(networks)} real networks'
            })
        else:
            return jsonify({
                'status': 'error',
                'networks': [],
                'count': 0,
                'error': 'No networks found. Check permissions or try different scanning method.'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'networks': [],
            'count': 0,
            'error': f'Scan failed: {str(e)}'
        })

@app.route('/api/system')
def api_system():
    return jsonify({
        'platform': sys.platform,
        'python_version': sys.version,
        'status': 'online',
        'mobile': True
    })

def addLog(level, message):
    """Add log entry (for server-side logging)"""
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] [{level.upper()}] {message}")

if __name__ == '__main__':
    print("🚀 Starting Net.Krk REAL DATA Dashboard...")
    print("📱 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure port 5000 is not in use")