#!/usr/bin/env python3
"""
Simplified Net.Krk Dashboard for Pydroid
This version is designed to work better on mobile devices
"""

import os
import sys
import json
import time
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Simple HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Net.Krk - Mobile Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ffff;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .title {
            font-size: 2.5em;
            color: #ff0088;
            text-shadow: 0 0 20px #ff0088;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #00ffff;
            font-size: 1.2em;
        }
        
        .status {
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid #00ffff;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff00;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .section {
            background: rgba(255, 0, 136, 0.1);
            border: 1px solid #ff0088;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .section h3 {
            color: #ff0088;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .button {
            background: linear-gradient(45deg, #ff0088, #00ffff);
            border: none;
            color: white;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            margin: 10px;
            transition: transform 0.3s;
        }
        
        .button:hover {
            transform: scale(1.05);
        }
        
        .button:active {
            transform: scale(0.95);
        }
        
        .info {
            background: rgba(0, 255, 255, 0.05);
            border-left: 4px solid #00ffff;
            padding: 15px;
            margin: 15px 0;
        }
        
        .log {
            background: #000;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        
        .log-entry {
            margin: 5px 0;
            padding: 5px;
            border-radius: 3px;
        }
        
        .log-info { color: #00ffff; }
        .log-success { color: #00ff00; }
        .log-warning { color: #ffff00; }
        .log-error { color: #ff0000; }
        
        .links {
            text-align: center;
            margin: 30px 0;
        }
        
        .links a {
            color: #00ffff;
            text-decoration: none;
            margin: 0 15px;
            padding: 10px 20px;
            border: 1px solid #00ffff;
            border-radius: 5px;
            display: inline-block;
            margin: 10px;
        }
        
        .links a:hover {
            background: rgba(0, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">net.krak</h1>
            <p class="subtitle">WiFi Penetration Suite v2.0 - Mobile Edition</p>
        </div>
        
        <div class="status">
            <span class="status-indicator"></span>
            <strong>System Status: ONLINE</strong>
            <p>Mobile Dashboard Ready</p>
        </div>
        
        <div class="section">
            <h3>🚀 Quick Actions</h3>
            <button class="button" onclick="testConnection()">Test Connection</button>
            <button class="button" onclick="scanNetworks()">Scan Networks</button>
            <button class="button" onclick="showSystemInfo()">System Info</button>
        </div>
        
        <div class="section">
            <h3>🔧 Advanced Tools</h3>
            <div class="links">
                <a href="/advanced">Advanced Scanner</a>
                <a href="/xss">XSS Generator</a>
                <a href="/subdomain">Subdomain Empire</a>
                <a href="/csrf">CSRF Arsenal</a>
                <a href="/cors">CORS Breaker</a>
                <a href="/clickjacking">Clickjacking Ninja</a>
                <a href="/ai">AI Analyzer</a>
            </div>
        </div>
        
        <div class="section">
            <h3>📊 Activity Log</h3>
            <div id="log" class="log">
                <div class="log-entry log-info">[INFO] Mobile dashboard initialized</div>
                <div class="log-entry log-success">[SUCCESS] Flask server running on port 5000</div>
                <div class="log-entry log-info">[INFO] Ready for operations</div>
            </div>
        </div>
        
        <div class="info">
            <h4>📱 Mobile Instructions:</h4>
            <p>1. This dashboard is optimized for mobile devices</p>
            <p>2. Use the buttons above to test functionality</p>
            <p>3. Check the activity log for real-time updates</p>
            <p>4. Advanced tools are available via the links above</p>
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
        
        function scanNetworks() {
            addLog('info', 'Starting network scan...');
            fetch('/api/scan')
                .then(response => response.json())
                .then(data => {
                    addLog('success', `Found ${data.networks.length} networks`);
                })
                .catch(error => {
                    addLog('error', `Scan failed: ${error.message}`);
                });
        }
        
        function showSystemInfo() {
            addLog('info', 'Getting system information...');
            fetch('/api/system')
                .then(response => response.json())
                .then(data => {
                    addLog('success', `System: ${data.platform} ${data.python_version}`);
                })
                .catch(error => {
                    addLog('error', `System info failed: ${error.message}`);
                });
        }
        
        // Auto-refresh log every 5 seconds
        setInterval(() => {
            addLog('info', 'System heartbeat - ' + new Date().toLocaleTimeString());
        }, 5000);
    </script>
</body>
</html>
"""

# API Routes
@app.route('/')
def dashboard():
    return DASHBOARD_HTML

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'success',
        'message': 'Connection successful!',
        'timestamp': time.time()
    })

@app.route('/api/scan')
def api_scan():
    # Simulate network scan
    networks = [
        {'ssid': 'TestNetwork1', 'bssid': '00:11:22:33:44:55', 'signal': -45},
        {'ssid': 'TestNetwork2', 'bssid': '00:11:22:33:44:66', 'signal': -60},
        {'ssid': 'TestNetwork3', 'bssid': '00:11:22:33:44:77', 'signal': -75}
    ]
    return jsonify({
        'status': 'success',
        'networks': networks,
        'count': len(networks)
    })

@app.route('/api/system')
def api_system():
    return jsonify({
        'platform': sys.platform,
        'python_version': sys.version,
        'status': 'online'
    })

# Advanced tool routes
@app.route('/advanced')
def advanced_scanner():
    try:
        with open('advanced_scanner.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Advanced scanner not available", 404

@app.route('/xss')
def xss_generator():
    try:
        with open('xss_payload_generator.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "XSS generator not available", 404

@app.route('/subdomain')
def subdomain_empire():
    try:
        with open('subdomain_empire.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Subdomain empire not available", 404

@app.route('/csrf')
def csrf_arsenal():
    try:
        with open('csrf_arsenal.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "CSRF arsenal not available", 404

@app.route('/cors')
def cors_breaker():
    try:
        with open('cors_breaker.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "CORS breaker not available", 404

@app.route('/clickjacking')
def clickjacking_ninja():
    try:
        with open('clickjacking_ninja.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Clickjacking ninja not available", 404

@app.route('/ai')
def ai_analyzer():
    try:
        with open('ai_vulnerability_analyzer.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "AI analyzer not available", 404

if __name__ == '__main__':
    print("🚀 Starting Net.Krk Mobile Dashboard...")
    print("📱 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure port 5000 is not in use")