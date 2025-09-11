# Installation Matrix - net.krak v2.0

This document provides a comprehensive installation matrix for different environments and use cases.

## 🐳 Docker Installation

### Full Functionality (Recommended for Pentesting)

```bash
# Using Docker Compose (Recommended)
git clone https://github.com/netkrak/netkrak.git
cd netkrak
sudo docker-compose up netkrak-full

# Using Docker Run
docker run -it --rm \
  --cap-add=NET_ADMIN --cap-add=NET_RAW \
  --device /dev/net/tun \
  --network host \
  -v /path/to/captures:/app/captures \
  -v /var/run/dbus:/var/run/dbus \
  --name netkrak netkrak:latest

# Access dashboard at http://localhost:5000
```

### Demo Mode (Safe for Testing/Demo)

```bash
# Using Docker Compose
sudo docker-compose up netkrak-demo

# Using Docker Run
docker run -it --rm \
  -p 5000:5000 \
  -v /path/to/logs:/app/logs \
  --name netkrak-demo netkrak-demo:latest

# Access dashboard at http://localhost:5000
```

### Docker Image Variants

| Image | Size | Capabilities | Use Case |
|-------|------|-------------|----------|
| `netkrak-full` | ~800MB | Full pentest tools | Production pentesting |
| `netkrak-demo` | ~200MB | Web UI only | Demo, testing, safe environments |

## 🐍 Python Installation

### From PyPI (Recommended)

```bash
# Install from PyPI
pip install netkrak

# Run diagnostics
netkrak-diagnostics

# Run orchestrator
sudo netkrak list-interfaces
```

### From Source

```bash
# Clone repository
git clone https://github.com/netkrak/netkrak.git
cd netkrak

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Run tests
python -m pytest
```

### Python Wheel Distribution

```bash
# Download wheel from releases
wget https://github.com/netkrak/netkrak/releases/download/v2.0.0/netkrak-2.0.0-py3-none-any.whl

# Install wheel
pip install netkrak-2.0.0-py3-none-any.whl
```

## 🖥️ System Requirements

### Operating Systems

| OS | Status | Notes |
|----|--------|-------|
| Ubuntu 20.04+ | ✅ Supported | Recommended |
| Ubuntu 18.04 | ⚠️ Limited | Some tools may not work |
| Debian 10+ | ✅ Supported | Full support |
| Kali Linux | ✅ Supported | Native environment |
| Parrot OS | ✅ Supported | Security-focused distro |
| CentOS 8+ | ⚠️ Limited | Requires additional setup |
| RHEL 8+ | ⚠️ Limited | Requires additional setup |
| Arch Linux | ✅ Supported | Community maintained |
| Fedora 33+ | ✅ Supported | Full support |

### Hardware Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| RAM | 2GB | 4GB+ | More RAM for large scans |
| CPU | 2 cores | 4+ cores | Multi-threading support |
| Storage | 1GB | 5GB+ | For captures and logs |
| WiFi | Monitor mode capable | External adapter recommended | Built-in may have limitations |

### WiFi Adapter Compatibility

| Chipset | Status | Notes |
|---------|--------|-------|
| Atheros AR9271 | ✅ Excellent | Highly recommended |
| Ralink RT3070 | ✅ Good | Good performance |
| Realtek RTL8187L | ✅ Good | USB adapter |
| Intel 7260 | ⚠️ Limited | May require additional drivers |
| Broadcom | ❌ Not supported | No monitor mode support |

## 🔧 Installation Methods by Environment

### Development Environment

```bash
# Clone and setup development environment
git clone https://github.com/netkrak/netkrak.git
cd netkrak

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Run tests
python -m pytest

# Run linting
black *.py
flake8 *.py
```

### Production Environment

```bash
# Using Docker (Recommended)
sudo docker-compose up -d netkrak-full

# Using system installation
sudo apt-get update
sudo apt-get install -y aircrack-ng reaver bully iw net-tools
pip install netkrak
sudo netkrak diagnostics
```

### CI/CD Environment

```yaml
# GitHub Actions example
- name: Install netkrak
  run: |
    pip install netkrak
    netkrak-diagnostics --json > diagnostics.json
```

### Container Orchestration

#### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: netkrak
spec:
  replicas: 1
  selector:
    matchLabels:
      app: netkrak
  template:
    metadata:
      labels:
        app: netkrak
    spec:
      containers:
      - name: netkrak
        image: ghcr.io/netkrak/netkrak-full:latest
        securityContext:
          capabilities:
            add:
            - NET_ADMIN
            - NET_RAW
        volumeMounts:
        - name: captures
          mountPath: /app/captures
      volumes:
      - name: captures
        hostPath:
          path: /var/lib/netkrak/captures
```

#### Docker Swarm

```yaml
version: '3.8'
services:
  netkrak:
    image: netkrak-full:latest
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    cap_add:
      - NET_ADMIN
      - NET_RAW
    network_mode: host
    volumes:
      - /var/lib/netkrak/captures:/app/captures
```

## 🛠️ Dependency Installation

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
  aircrack-ng \
  reaver \
  bully \
  wireless-tools \
  net-tools \
  iw \
  python3-pip \
  python3-venv

# Install Python dependencies
pip3 install netkrak
```

### CentOS/RHEL

```bash
# Install EPEL repository
sudo yum install -y epel-release

# Install dependencies
sudo yum install -y \
  aircrack-ng \
  reaver \
  wireless-tools \
  net-tools \
  python3-pip

# Install Python dependencies
pip3 install netkrak
```

### Arch Linux

```bash
# Install from AUR
yay -S netkrak

# Or install manually
sudo pacman -S aircrack-ng reaver wireless_tools net-tools python-pip
pip install netkrak
```

### Kali Linux

```bash
# Most tools already installed
sudo apt-get update
sudo apt-get install -y python3-pip
pip3 install netkrak
```

## 🔍 Verification and Testing

### System Diagnostics

```bash
# Run comprehensive diagnostics
sudo netkrak diagnostics

# Generate Docker command
sudo netkrak diagnostics --docker-command

# Export diagnostics to JSON
sudo netkrak diagnostics --json > diagnostics.json
```

### Functionality Tests

```bash
# Test interface listing
sudo netkrak list-interfaces

# Test scanning (requires monitor mode interface)
sudo netkrak scan wlan0mon --scan-time 5

# Test system status
sudo netkrak status
```

### Docker Testing

```bash
# Test full image
docker run --rm netkrak-full:latest netkrak diagnostics

# Test demo image
docker run --rm -p 5000:5000 netkrak-demo:latest

# Test with capabilities
docker run --rm --cap-add=NET_ADMIN --cap-add=NET_RAW netkrak-full:latest netkrak list-interfaces
```

## 🚨 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Solution: Run with proper capabilities
sudo netkrak diagnostics
# Or for Docker:
docker run --rm --cap-add=NET_ADMIN --cap-add=NET_RAW netkrak-full:latest
```

#### No Wireless Interfaces Found
```bash
# Check available interfaces
iw dev
ip link show

# Set interface to monitor mode
sudo airmon-ng start wlan0
```

#### Docker Network Issues
```bash
# Use host networking for wireless operations
docker run --rm --network host --cap-add=NET_ADMIN --cap-add=NET_RAW netkrak-full:latest
```

#### Missing Dependencies
```bash
# Run diagnostics to identify missing tools
sudo netkrak diagnostics

# Install missing packages based on recommendations
sudo apt-get install aircrack-ng reaver bully wireless-tools net-tools
```

## 📊 Performance Considerations

### Resource Usage

| Component | CPU Usage | Memory Usage | Disk Usage |
|-----------|-----------|--------------|------------|
| Web Dashboard | 5-10% | 50-100MB | 10MB |
| Network Scanning | 20-50% | 100-200MB | 50MB |
| Attack Execution | 30-80% | 200-500MB | 100MB+ |
| Full Suite | 50-90% | 300-800MB | 200MB+ |

### Optimization Tips

1. **Use SSD storage** for better I/O performance
2. **Allocate sufficient RAM** for large network scans
3. **Use external WiFi adapters** for better performance
4. **Close unnecessary applications** during intensive operations
5. **Use Docker resource limits** in production environments

## 🔒 Security Considerations

### Docker Security

- Use specific image tags instead of `latest`
- Run containers as non-root user when possible
- Limit container capabilities to minimum required
- Use read-only filesystems where possible
- Regularly update base images

### System Security

- Run with minimal required privileges
- Use dedicated user accounts for netkrak
- Regularly update system packages
- Monitor system logs for suspicious activity
- Use secure communication channels

## 📈 Monitoring and Maintenance

### Health Checks

```bash
# Check system health
sudo netkrak status

# Monitor resource usage
htop
iotop

# Check Docker container health
docker ps
docker logs netkrak
```

### Updates

```bash
# Update Python package
pip install --upgrade netkrak

# Update Docker images
docker pull netkrak-full:latest
docker pull netkrak-demo:latest

# Update system packages
sudo apt-get update && sudo apt-get upgrade
```

---

For more information, see the [README.md](README.md) and [ADVANCED_README.md](ADVANCED_README.md) files.