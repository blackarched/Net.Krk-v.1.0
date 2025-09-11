from flask import Flask, jsonify
import sys
import time
import subprocess
import re

app = Flask(__name__)

def scan_networks():
    networks = []
    
    print("Starting network scan...")
    
    try:
        result = subprocess.run(['iwlist', 'scan'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            networks = parse_iwlist(result.stdout)
            print(f"Found {len(networks)} networks")
    except Exception as e:
        print(f"Scan error: {e}")
    
    return networks

def parse_iwlist(output):
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
    
    if current:
        networks.append(current)
    
    return networks

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Net.Krk Scanner</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                background: #000; 
                color: #0ff; 
                font-family: monospace; 
                padding: 20px; 
            }
            .title { color: #f08; font-size: 2em; text-align: center; margin-bottom: 20px; }
            .button { 
                background: linear-gradient(45deg, #f08, #0ff); 
                border: none; 
                color: white; 
                padding: 15px 30px; 
                border-radius: 25px; 
                margin: 10px; 
                font-size: 16px; 
                cursor: pointer;
            }
            .log { 
                background: #111; 
                border: 1px solid #333; 
                padding: 15px; 
                margin: 20px 0; 
                height: 200px; 
                overflow-y: auto; 
            }
            .network { 
                background: rgba(255, 0, 136, 0.1); 
                border: 1px solid #f08; 
                padding: 10px; 
                margin: 5px 0; 
            }
        </style>
    </head>
    <body>
        <h1 class="title">net.krak</h1>
        <div style="text-align: center;">
            <button class="button" onclick="scan()">Scan Networks</button>
            <button class="button" onclick="test()">Test</button>
        </div>
        <div id="networks"></div>
        <div id="log" class="log">
            <div>Ready to scan...</div>
        </div>
        
        <script>
            function addLog(msg) {
                document.getElementById('log').innerHTML += '<div>' + new Date().toLocaleTimeString() + ' - ' + msg + '</div>';
            }
            
            function scan() {
                addLog('Scanning...');
                fetch('/api/scan')
                    .then(r => r.json())
                    .then(d => {
                        addLog('Found ' + d.count + ' networks');
                        showNetworks(d.networks);
                    });
            }
            
            function test() {
                addLog('Testing...');
                fetch('/api/test')
                    .then(r => r.json())
                    .then(d => addLog(d.message));
            }
            
            function showNetworks(nets) {
                const div = document.getElementById('networks');
                div.innerHTML = '';
                nets.forEach(net => {
                    div.innerHTML += '<div class="network">' + (net.ssid || 'Hidden') + ' - ' + net.bssid + ' - ' + net.signal + 'dBm</div>';
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/test')
def test():
    return jsonify({'message': 'Connection OK'})

@app.route('/api/scan')
def scan():
    networks = scan_networks()
    return jsonify({
        'networks': networks,
        'count': len(networks)
    })

if __name__ == '__main__':
    print("Starting Net.Krk...")
    print("Open: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)