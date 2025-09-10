# File: README.md
# net.krak - WiFi Pentesting Suite

## ⚠️ Legal Notice & Authorization
This tool is intended **strictly for educational purposes and authorized security testing**. You may only use this tool on networks you own or have explicit, written permission to test. Unauthorized access to or attacks on computer networks is illegal. The developers assume no liability and are not responsible for any misuse or damage.

**By using this software, you acknowledge that you are fully responsible for your actions.** The tool has safeguards (like the confirmation dialogs below) to ensure deliberate use, reinforcing your accountability.

## Getting Started

### Prerequisites
* Docker and Docker Compose
* A Linux host machine
* A WiFi adapter that supports monitor mode and packet injection.

### Deployment with Docker

1.  **Clone the repository:**
    ```bash
    git clone https://your-repo-url/net.krak.git
    cd net.krak
    ```

2.  **Configure the application:**
    Copy the example environment file. No changes are needed to run with the defaults.
    ```bash
    cp .env.example .env
    ```

3.  **Build and run with Docker Compose:**
    This command builds the container and starts the application.
    ```bash
    sudo docker-compose up --build
    ```

4.  **Access the Dashboard:**
    Open your web browser and navigate to `http://localhost:5000` (or the port defined in your `.env` file).

### **Required Docker Capabilities**

This tool requires direct, low-level access to your host's network hardware. The `docker-compose.yml` file is pre-configured with the necessary flags:

* `network_mode: "host"`: Allows the container to see and control your host's network interfaces (e.g., `wlan0`).
* `cap_add: [NET_ADMIN, NET_RAW]`: Grants the specific kernel capabilities needed to enable monitor mode, sniff packets, and perform packet injection, without granting full `privileged` access.