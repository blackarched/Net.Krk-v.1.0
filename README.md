# NetKrak - WiFi Pentest Suite

NetKrak is a comprehensive Python suite for network analysis, penetration testing, and security auditing. It combines a powerful command-line interface (CLI) with a modern, feature-rich web dashboard for managing and executing various network attacks.

## ⚠️ WARNING

**This tool is for educational and authorized testing purposes only.**
- Only use on networks you own or have explicit written permission to test.
- Unauthorized use may violate laws and terms of service.
- The authors are not responsible for any misuse of this tool.

## Features

- **Advanced Network Discovery**: Scan networks using Scapy or Airodump-ng to find active devices, access points, and clients.
- **Modern Web Dashboard**: A full-featured web UI to visualize network data, manage scans, and launch attacks from your browser.
- **Powerful CLI**: A comprehensive command-line interface (`orchestrator.py`) for scripting, automation, and headless operation.
- **Multiple Attack Vectors**:
    - Deauthentication Attacks
    - WPA/WPA2 Handshake Capture
    - Evil Twin AP Creation
    - Credential Harvesting
    - WPS Attacks
    - Packet Fragmentation Attacks
- **Docker Support**: Comes with pre-configured `Dockerfile` and `docker-compose.yml` for easy, containerized deployment.
- **Comprehensive Logging**: All actions are logged to a JSON-formatted log file for easy analysis.

## Project Structure

The project has been reorganized into a clean, modular structure:

```
.
├── src/                  # All Python source code
│   ├── attacks.py
│   ├── dashboard_api.py  # Backend for the web UI
│   ├── orchestrator.py   # Main CLI application
│   ├── scanner.py
│   └── utils/
├── web/                  # Web frontend files
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, and other static assets (if any)
├── scripts/              # Helper scripts
├── tests/                # (Currently a work in progress)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Installation

### Prerequisites
- Linux operating system (recommended)
- Python 3.7 or higher
- Root/administrator privileges for raw network access.
- System dependencies like `aircrack-ng`, `net-tools`, etc. The `Dockerfile` provides a complete list.

### Manual Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd netkrak
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

NetKrak can be run as a command-line tool or as a web service.

### 1. Web Dashboard

The web dashboard provides an intuitive interface for all of NetKrak's features.

**To start the web server:**
```bash
sudo python -m src.dashboard_api
```
Then, open your browser to `http://127.0.0.1:5000`.

### 2. Command-Line Interface (CLI)

The CLI is ideal for automation and scripting. It is managed via `orchestrator.py`.

**To see all available commands:**
```bash
sudo python -m src.orchestrator --help
```

**Example: Scanning for networks**
```bash
sudo python -m src.orchestrator scan wlan0mon
```

**Example: Running a deauthentication attack**
```bash
sudo python -m src.orchestrator attack wlan0mon --bssid AA:BB:CC:DD:EE:FF --ssid "MyNetwork" --attack-type deauth --authorized
```
**Note:** The `--authorized` flag is required for all attacks to ensure you have permission to test the target network.

## Docker Deployment

The easiest way to run NetKrak is with Docker, which handles all dependencies and setup for you.

### Docker Compose (Recommended)

Docker Compose provides two services: `netkrak-full` (with all tools) and `netkrak-demo` (a safe, web-only version).

**To build and run the full version:**
```bash
docker-compose up --build netkrak-full
```

**To run in detached mode:**
```bash
docker-compose up -d netkrak-full
```
The web dashboard will be available on the host machine at `http://<your-docker-host-ip>:5000`.

### Manual Docker Build

You can also build the Docker images manually.

**Build the full image:**
```bash
docker build -t netkrak:full --target full .
```

**Run the full image:**
```bash
docker run -it --rm --network host --cap-add NET_ADMIN --cap-add NET_RAW netkrak:full
```

## Contributing

1.  Fork the repository.
2.  Create a feature branch.
3.  Make your changes.
4.  Add or update tests if applicable.
5.  Submit a pull request.

## License

This project is for educational purposes only. Use at your own risk and ensure compliance with applicable laws and regulations.
