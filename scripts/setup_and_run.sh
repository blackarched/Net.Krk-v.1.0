#!/bin/bash
set -e

# --- Safety: Require root ---
if [ "$EUID" -ne 0 ]; then
  echo "[FATAL] Please run as root (sudo $0)"
  exit 1
fi

# Navigate to script directory to ensure relative paths work
cd "$(dirname "$0")"

# --- Python venv ---
if [ ! -d ".venv" ]; then
  echo "[INFO] Creating Python virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate

# --- Install Python dependencies from requirements.txt ---
echo "[INFO] Installing/updating Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# --- Install system dependencies ---
if ! command -v airodump-ng >/dev/null 2>&1; then
  echo "[INFO] aircrack-ng suite not found. Installing..."
  # This works for Debian/Ubuntu based systems
  apt-get update && apt-get install -y aircrack-ng
else
  echo "[INFO] aircrack-ng suite found."
fi

# --- Check for required tools ---
for tool in iwconfig ifconfig; do
  if ! command -v $tool >/dev/null 2>&1; then
    echo "[FATAL] Required tool '$tool' not found. Please install net-tools or equivalent."
    exit 1
  fi
done

# --- Start Flask backend with a production-ready WSGI server (waitress) ---
# Add waitress to requirements.txt if you want to use it
# pip install waitress
echo "[INFO] Starting Flask backend API (dashboard_api.py) on :5000..."
# Using waitress-serve instead of Flask's debug server
# nohup .venv/bin/waitress-serve --host=0.0.0.0 --port=5000 dashboard_api:app > flask_backend.log 2>&1 &
# Sticking with the original for simplicity, but warning it's not for production
nohup .venv/bin/python3 dashboard_api.py > flask_backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .dashboard_api.pid
sleep 2

# --- Start HTTP server for dashboard ---
echo "[INFO] Starting HTTP server for dashboard on :8080..."
nohup .venv/bin/python3 -m http.server 8080 --bind 127.0.0.1 > dashboard_http.log 2>&1 &
HTTP_PID=$!
echo $HTTP_PID > .dashboard_http.pid
sleep 2

# --- Open dashboard in browser (if possible) ---
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:8080/netkrak_dashboard.html
else
  echo "[INFO] Please open http://localhost:8080/netkrak_dashboard.html in your browser."
fi

echo "[SUCCESS] net.krak dashboard is running."
echo "  - Flask API Server: http://localhost:5000"
echo "  - Web Dashboard:    http://localhost:8080/netkrak_dashboard.html"
echo "To stop the services, run: kill \`cat .dashboard_api.pid\` \`cat .dashboard_http.pid\`"