"""
dashboard_api.py - Enhanced Flask API and web server for net.krak
Improved with better validation, error handling, and new endpoints
"""
import json
import os
import re
import time
import threading
from pathlib import Path
from flask import Flask, request, jsonify, abort, render_template, Response
from flask_cors import CORS

from scanner import scan_networks, list_wifi_interfaces, get_network_info, get_client_info, get_scan_status
from attacks import (deauth_attack, capture_handshake, perform_evil_twin, capture_credentials,
                    perform_wps_attack, perform_fragmentation_attack, stop_attack, stop_all_attacks,
                    get_attack_status)
from utils.logger_config import setup_logging, log_event

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)  # Enable CORS for all routes

# Setup logging
logger = setup_logging()

# Regex patterns for validation
MAC_REGEX = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
IFACE_REGEX = re.compile(r'^[a-zA-Z0-9_.-]+$')
SSID_REGEX = re.compile(r'^[\x20-\x7E]{0,32}$')  # Printable ASCII, max 32 chars

# Global state
scan_status = {"active": False, "networks": [], "clients": []}
attack_status = {"active": False, "processes": {}}

def validate_request_data(data, required_fields):
    """Validate request data and return error if invalid"""
    if not data:
        return "Request data is required", 400
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}", 400
    
    return None, None

def validate_interface(interface):
    """Validate interface name"""
    if not interface or not IFACE_REGEX.match(interface):
        return "Invalid interface name format"
    return None

def validate_mac_address(mac):
    """Validate MAC address format"""
    if not mac or not MAC_REGEX.match(mac):
        return "Invalid MAC address format"
    return None

def validate_ssid(ssid):
    """Validate SSID format"""
    if not ssid or not SSID_REGEX.match(ssid):
        return "Invalid SSID format"
    return None

def validate_channel(channel):
    """Validate WiFi channel"""
    try:
        channel_int = int(channel)
        if not (1 <= channel_int <= 165):
            return "Channel must be between 1 and 165"
    except (ValueError, TypeError):
        return "Channel must be a valid integer"
    return None

# --- Frontend Route ---
@app.route("/")
def index():
    """Serves the main dashboard page."""
    return render_template("index.html")

# --- System Information Routes ---
@app.route("/system/info", methods=["GET"])
def system_info():
    """Get system information and status"""
    try:
        info = {
            "timestamp": time.time(),
            "interfaces": list_wifi_interfaces(logger=logger),
            "scan_status": get_scan_status(),
            "attack_status": get_attack_status(),
            "version": "2.0.0",
            "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0
        }
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({"error": "Failed to get system information"}), 500

@app.route("/system/interfaces", methods=["GET"])
def get_interfaces():
    """Get list of available WiFi interfaces"""
    try:
        interfaces = list_wifi_interfaces(logger=logger)
        return jsonify({"interfaces": interfaces})
    except Exception as e:
        logger.error(f"Error getting interfaces: {e}")
        return jsonify({"error": "Failed to get interfaces"}), 500

# --- Network Scanning Routes ---
@app.route("/scan", methods=["GET"])
def api_scan():
    """Enhanced network scanning endpoint"""
    try:
        interface = request.args.get("interface")
        scan_time = request.args.get("scan_time", 15, type=int)
        method = request.args.get("method", "scapy")
        
        # Validate inputs
        if not interface:
            return jsonify({"error": "Interface parameter is required"}), 400
        
        iface_error = validate_interface(interface)
        if iface_error:
            return jsonify({"error": iface_error}), 400
        
        if not (1 <= scan_time <= 300):
            return jsonify({"error": "Scan time must be between 1 and 300 seconds"}), 400
        
        if method not in ["scapy", "airodump"]:
            return jsonify({"error": "Method must be 'scapy' or 'airodump'"}), 400
        
        log_event(logger, "api_scan_start", interface=interface, scan_time=scan_time, method=method)
        
        # Perform scan
        networks = scan_networks(interface, scan_time=scan_time, method=method, logger=logger)
        
        # Update global state
        scan_status["networks"] = networks
        scan_status["active"] = False
        
        log_event(logger, "api_scan_complete", network_count=len(networks))
        return jsonify(networks)
        
    except Exception as e:
        logger.error(f"Scan error: {e}")
        return jsonify({"error": f"Scan failed: {str(e)}"}), 500

@app.route("/scan/status", methods=["GET"])
def scan_status_endpoint():
    """Get current scan status"""
    try:
        status = get_scan_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        return jsonify({"error": "Failed to get scan status"}), 500

@app.route("/network/<bssid>", methods=["GET"])
def get_network_details(bssid):
    """Get detailed information about a specific network"""
    try:
        mac_error = validate_mac_address(bssid)
        if mac_error:
            return jsonify({"error": mac_error}), 400
        
        network_info = get_network_info(bssid)
        if not network_info:
            return jsonify({"error": "Network not found"}), 404
        
        return jsonify(network_info)
    except Exception as e:
        logger.error(f"Error getting network details: {e}")
        return jsonify({"error": "Failed to get network details"}), 500

# --- Attack Routes ---
@app.route("/attack", methods=["POST"])
def api_attack():
    """Enhanced attack endpoint with better validation"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        # Validate required fields
        required_fields = ["interface", "bssid", "ssid", "attack_type"]
        error, status_code = validate_request_data(data, required_fields)
        if error:
            return jsonify({"error": error}), status_code
        
        # Extract and validate parameters
        interface = data.get("interface")
        bssid = data.get("bssid")
        ssid = data.get("ssid")
        attack_type = data.get("attack_type")
        channel = data.get("channel")
        duration = data.get("duration", 300)
        
        # Validate individual fields
        iface_error = validate_interface(interface)
        if iface_error:
            return jsonify({"error": iface_error}), 400
        
        mac_error = validate_mac_address(bssid)
        if mac_error:
            return jsonify({"error": mac_error}), 400
        
        ssid_error = validate_ssid(ssid)
        if ssid_error:
            return jsonify({"error": ssid_error}), 400
        
        if channel:
            channel_error = validate_channel(channel)
            if channel_error:
                return jsonify({"error": channel_error}), 400
        
        # Validate attack type
        valid_attacks = ["deauth", "handshake", "evil_twin", "credential", "wps", "fragmentation"]
        if attack_type not in valid_attacks:
            return jsonify({"error": f"Invalid attack type. Must be one of: {', '.join(valid_attacks)}"}), 400
        
        log_event(logger, "api_attack_received", 
                 attack_type=attack_type, bssid=bssid, ssid=ssid, channel=channel)
        
        # Execute attack based on type
        result = None
        if attack_type == "deauth":
            packet_count = data.get("packet_count", 10)
            result = deauth_attack(interface, bssid, packet_count=packet_count, logger=logger)
            status_msg = f"Deauthentication attack {'started' if result else 'failed'} on {bssid}"
            
        elif attack_type == "handshake":
            if not channel:
                return jsonify({"error": "Channel is required for handshake capture"}), 400
            result = capture_handshake(interface, bssid, channel=channel, 
                                     duration=duration, logger=logger)
            status_msg = f"Handshake capture {'started' if result else 'failed'} on {bssid}"
            
        elif attack_type == "evil_twin":
            hidden = data.get("hidden", False)
            result = perform_evil_twin(interface, bssid, ssid, channel=channel, 
                                     hidden=hidden, logger=logger)
            status_msg = f"Evil Twin {'started' if result else 'failed'} for {ssid}"
            
        elif attack_type == "credential":
            if not channel:
                return jsonify({"error": "Channel is required for credential capture"}), 400
            result = capture_credentials(interface, bssid, channel=channel, 
                                      duration=duration, logger=logger)
            status_msg = f"Credential capture {'started' if result else 'failed'} on {bssid}"
            
        elif attack_type == "wps":
            result = perform_wps_attack(interface, bssid, timeout=duration, logger=logger)
            status_msg = f"WPS attack {'started' if result else 'failed'} on {bssid}"
            
        elif attack_type == "fragmentation":
            result = perform_fragmentation_attack(interface, bssid, timeout=duration, logger=logger)
            status_msg = f"Fragmentation attack {'started' if result else 'failed'} on {bssid}"
        
        # Update attack status
        attack_status["active"] = True
        if result and hasattr(result, 'pid'):
            attack_status["processes"][str(result.pid)] = {
                "attack_type": attack_type,
                "bssid": bssid,
                "ssid": ssid,
                "start_time": time.time()
            }
        
        return jsonify({
            "status": status_msg,
            "success": bool(result),
            "attack_type": attack_type,
            "process_id": str(result.pid) if result and hasattr(result, 'pid') else None
        })
        
    except Exception as e:
        logger.error(f"Attack error: {e}")
        return jsonify({"error": f"Attack failed: {str(e)}"}), 500

@app.route("/attack/stop", methods=["POST"])
def stop_attacks():
    """Stop all active attacks"""
    try:
        data = request.json or {}
        process_id = data.get("process_id")
        
        if process_id:
            # Stop specific process
            success = stop_attack(process_id, logger=logger)
            if success:
                attack_status["processes"].pop(process_id, None)
                return jsonify({"status": f"Stopped attack process {process_id}"})
            else:
                return jsonify({"error": f"Failed to stop process {process_id}"}), 500
        else:
            # Stop all attacks
            success = stop_all_attacks(logger=logger)
            attack_status["active"] = False
            attack_status["processes"].clear()
            return jsonify({"status": "Stopped all attacks" if success else "Failed to stop attacks"})
            
    except Exception as e:
        logger.error(f"Error stopping attacks: {e}")
        return jsonify({"error": f"Failed to stop attacks: {str(e)}"}), 500

@app.route("/attack/status", methods=["GET"])
def attack_status_endpoint():
    """Get current attack status"""
    try:
        status = get_attack_status()
        return jsonify({
            "active": bool(status),
            "processes": status,
            "global_status": attack_status
        })
    except Exception as e:
        logger.error(f"Error getting attack status: {e}")
        return jsonify({"error": "Failed to get attack status"}), 500

# --- Monitoring Routes ---
@app.route("/monitor/stream", methods=["GET"])
def monitor_stream():
    """Stream real-time monitoring data"""
    def generate():
        while True:
            try:
                data = {
                    "timestamp": time.time(),
                    "scan_status": get_scan_status(),
                    "attack_status": get_attack_status(),
                    "networks": scan_status["networks"][-10:],  # Last 10 networks
                }
                yield f"data: {json.dumps(data)}\n\n"
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in monitor stream: {e}")
                break
    
    return Response(generate(), mimetype='text/event-stream')

# --- Utility Routes ---
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0"
    })

@app.route("/logs", methods=["GET"])
def get_logs():
    """Get recent log entries"""
    try:
        log_file = Path("logs/netkrak.jsonlog")
        if not log_file.exists():
            return jsonify({"logs": []})
        
        # Read last 100 lines
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        recent_logs = lines[-100:] if len(lines) > 100 else lines
        logs = []
        
        for line in recent_logs:
            try:
                log_entry = json.loads(line.strip())
                logs.append(log_entry)
            except json.JSONDecodeError:
                continue
        
        return jsonify({"logs": logs})
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({"error": "Failed to get logs"}), 500

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

# --- Application Setup ---
def initialize_app():
    """Initialize application on first request"""
    app.start_time = time.time()
    log_event(logger, "app_start", version="2.0.0")

# Initialize app
initialize_app()

if __name__ == "__main__":
    # This block is for development only
    app.run(host='0.0.0.0', port=5000, debug=True)