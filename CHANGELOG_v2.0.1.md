# Changelog v2.0.1 - Enhanced Docker Support & Diagnostics

## 🚀 New Features

### 1. Comprehensive Docker Documentation
- **Enhanced README.md**: Added detailed Docker run commands with all required flags
- **Updated ADVANCED_README.md**: Included Docker installation instructions for advanced tools
- **Docker Flag Documentation**: Clear explanation of `--cap-add`, `--device`, `--network host` requirements
- **Hardware Mapping Guide**: Documentation for avoiding `--network host` when necessary

### 2. Runtime Diagnostics System
- **New Module**: `utils/runtime_diagnostics.py` - Comprehensive system diagnostics
- **Tool Availability Checks**: Enhanced error messages with specific installation instructions
- **Privilege Verification**: Checks for required capabilities (CAP_NET_RAW, CAP_NET_ADMIN)
- **Docker Environment Detection**: Identifies Docker capabilities and network mode
- **Actionable Recommendations**: Provides specific commands to fix issues
- **CLI Integration**: New `diagnostics` command in orchestrator

### 3. Multi-Stage Docker Build
- **Builder Stage**: Optimized Python dependency installation
- **Full Image**: Complete functionality with all pentest tools (~800MB)
- **Demo Image**: Safe mode with web UI only (~200MB)
- **Security Improvements**: Non-root user, minimal attack surface
- **Reproducible Builds**: Build arguments for consistent builds

### 4. Enhanced Docker Compose
- **Multiple Services**: `netkrak-full` and `netkrak-demo` services
- **Capability Management**: Proper `cap_add` configuration
- **Volume Mapping**: Persistent storage for captures and logs
- **Health Checks**: Comprehensive container health monitoring

### 5. Release Artifacts & Packaging
- **Python Wheel**: `setup.py` for PyPI distribution
- **Build Script**: `build.sh` for automated Docker image building
- **GitHub Actions**: Automated CI/CD pipeline with security scanning
- **Installation Matrix**: Comprehensive installation guide for all environments
- **Version Tagging**: Semantic versioning with Git commit tags

## 🔧 Technical Improvements

### Code Quality
- **TODO Resolution**: Implemented robust signature verification in `orchestrator.py`
- **Enhanced Error Messages**: Specific installation instructions for missing tools
- **Better Logging**: Improved diagnostic information in error messages
- **Type Safety**: Added proper imports for cryptographic functions

### Security Enhancements
- **Signature Verification**: HMAC-SHA256 based authorization file verification
- **Non-root Containers**: Docker images run as non-root user
- **Capability Management**: Minimal required capabilities instead of privileged mode
- **Input Validation**: Enhanced parameter validation and error handling

### Performance Optimizations
- **Multi-stage Builds**: Reduced image sizes through build optimization
- **Layer Caching**: Improved Docker build performance
- **Resource Management**: Better memory and CPU usage patterns
- **Parallel Processing**: Optimized build processes

## 📋 New Commands & Usage

### Diagnostics Commands
```bash
# Run comprehensive diagnostics
sudo python3 orchestrator.py diagnostics

# Export diagnostics to JSON
sudo python3 orchestrator.py diagnostics --json

# Generate optimal Docker command
sudo python3 orchestrator.py diagnostics --docker-command

# Standalone diagnostics
python3 -m utils.runtime_diagnostics
```

### Docker Commands
```bash
# Full functionality
docker run -it --rm \
  --cap-add=NET_ADMIN --cap-add=NET_RAW \
  --device /dev/net/tun \
  --network host \
  -v /path/to/captures:/app/captures \
  -v /var/run/dbus:/var/run/dbus \
  --name netkrak netkrak:latest

# Demo mode (safe)
docker run -it --rm \
  -p 5000:5000 \
  -v /path/to/logs:/app/logs \
  --name netkrak-demo netkrak-demo:latest

# Docker Compose
docker-compose up netkrak-full    # Full functionality
docker-compose up netkrak-demo    # Demo mode
```

### Build Commands
```bash
# Build all artifacts
./build.sh

# Build only Docker images
./build.sh --docker-only

# Build with custom registry
DOCKER_REGISTRY=myregistry.com ./build.sh
```

## 🐛 Bug Fixes

- **Signature Verification**: Resolved TODO for robust authorization file verification
- **Error Messages**: Improved clarity of missing tool error messages
- **Docker Networking**: Fixed host networking requirements documentation
- **Capability Checks**: Enhanced privilege verification in containers

## 📚 Documentation Updates

### New Files
- `INSTALLATION_MATRIX.md`: Comprehensive installation guide
- `utils/runtime_diagnostics.py`: Runtime diagnostics module
- `setup.py`: Python package configuration
- `build.sh`: Automated build script
- `.github/workflows/build.yml`: CI/CD pipeline

### Updated Files
- `README.md`: Enhanced Docker documentation
- `ADVANCED_README.md`: Added Docker support
- `Dockerfile`: Multi-stage build implementation
- `docker-compose.yml`: Multiple service configuration
- `orchestrator.py`: Added diagnostics command and signature verification

## 🔄 Migration Guide

### From v2.0.0 to v2.0.1

1. **Update Docker Images**:
   ```bash
   docker pull netkrak-full:latest
   docker pull netkrak-demo:latest
   ```

2. **Run Diagnostics**:
   ```bash
   sudo python3 orchestrator.py diagnostics
   ```

3. **Update Docker Compose**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **Verify Installation**:
   ```bash
   sudo python3 orchestrator.py status
   ```

## 🎯 Next Steps

### Planned Features
- **Kubernetes Support**: Helm charts and K8s manifests
- **Advanced Monitoring**: Prometheus metrics and Grafana dashboards
- **Plugin System**: Extensible architecture for custom tools
- **API Documentation**: OpenAPI/Swagger documentation
- **Performance Profiling**: Built-in performance analysis tools

### Known Limitations
- **Windows Support**: Currently Linux-only (WSL2 support planned)
- **macOS Support**: Limited due to wireless interface restrictions
- **ARM Architecture**: Docker images not yet optimized for ARM

## 🤝 Contributing

### Development Setup
```bash
git clone https://github.com/netkrak/netkrak.git
cd netkrak
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

### Testing
```bash
# Run tests
python -m pytest

# Run diagnostics
python -m utils.runtime_diagnostics

# Test Docker builds
./build.sh --docker-only
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Full Changelog**: https://github.com/netkrak/netkrak/compare/v2.0.0...v2.0.1