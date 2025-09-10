"""
dashboard_api.py - Flask API and web server for net.krak.
"""
import json
import os
import re
from pathlib import Path
from flask import Flask, request, jsonify, abort, render_template

from scanner import scan_networks
from attacks import deauth_attack, capture_handshake, perform_evil_twin
from utils.logger_config import setup_logging, log_event

# Serve the dashboard from the 'static' folder
app = Flask(__name__, static_folder='static', template_folder='static')
logger = setup_logging()

# Regex for validation
MAC_REGEX = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
IFACE_REGEX = re.compile(r'^[a-zA-Z0-9_.-]+$')

# --- Frontend Route ---
@app.route("/")
def index():
    """Serves the main dashboard page."""
    return render_template("index.html")

# --- API Routes ---
@app.route("/scan", methods=["GET"])
def api_scan():
    interface = request.args.get("interface")
    if not interface or not IFACE_REGEX.match(interface):
        return jsonify({"error": "A valid interface parameter is required"}), 400

    scan_time = request.args.get("scan_time", 15, type=int)
    log_event(logger, "api_scan_start", interface=interface, scan_time=scan_time)
    nets = scan_networks(interface, scan_time=scan_time, logger=logger)
    log_event(logger, "api_scan_complete", network_count=len(nets))
    return jsonify(nets)

@app.route("/attack", methods=["POST"])
def api_attack():
    data = request.json
    if not data:
        abort(400)

    # Validate inputs
    interface = data.get("interface")
    bssid = data.get("bssid")
    ssid = data.get("ssid")
    attack_type = data.get("attack_type")

    if not all([interface, bssid, ssid, attack_type]):
        return jsonify({"error": "Missing required parameters"}), 400
    if not IFACE_REGEX.match(interface):
        return jsonify({"error": "Invalid interface name format"}), 400
    if not MAC_REGEX.match(bssid):
        return jsonify({"error": "Invalid BSSID (MAC address) format"}), 400

    log_event(logger, "api_attack_received", attack_type=attack_type, bssid=bssid, ssid=ssid)

    if attack_type == "deauth":
        deauth_attack(interface, bssid, logger=logger)
        return jsonify({"status": f"Deauthentication attack started on {bssid}"})
    elif attack_type == "handshake":
        try:
            channel = int(data.get("channel"))
            if not (1 <= channel <= 165): raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "A valid channel number is required for handshake capture"}), 400
        capture_handshake(interface, bssid, channel=channel, logger=logger)
        return jsonify({"status": f"Handshake capture started on {bssid}"})
    elif attack_type == "evil_twin":
        perform_evil_twin(interface, bssid, ssid, logger=logger)
        return jsonify({"status": f"Evil Twin started for {ssid}"})

    return jsonify({"error": f"Unknown attack type: {attack_type}"}), 400

# This block is no longer needed as Gunicorn is the entry point
# if __name__ == "__main__":
#     app.run(...)