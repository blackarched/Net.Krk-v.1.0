#!/bin/bash
# Build script for net.krak Docker images with tags and reproducible builds

set -e

# Configuration
REGISTRY="netkrak"
IMAGE_NAME="netkrak"
VERSION="2.0.0"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Build arguments for reproducible builds
BUILD_ARGS="--build-arg BUILD_DATE=${BUILD_DATE} --build-arg VCS_REF=${GIT_COMMIT}"

# Function to build and tag images
build_image() {
    local target=$1
    local tag_suffix=$2
    local description=$3
    
    log_info "Building ${description}..."
    
    # Build the image
    docker build \
        --target ${target} \
        ${BUILD_ARGS} \
        -t ${REGISTRY}/${IMAGE_NAME}${tag_suffix}:${VERSION} \
        -t ${REGISTRY}/${IMAGE_NAME}${tag_suffix}:latest \
        -t ${REGISTRY}/${IMAGE_NAME}${tag_suffix}:${GIT_COMMIT} \
        .
    
    log_success "Built ${description} with tags:"
    echo "  - ${REGISTRY}/${IMAGE_NAME}${tag_suffix}:${VERSION}"
    echo "  - ${REGISTRY}/${IMAGE_NAME}${tag_suffix}:latest"
    echo "  - ${REGISTRY}/${IMAGE_NAME}${tag_suffix}:${GIT_COMMIT}"
}

# Function to build Python wheel
build_wheel() {
    log_info "Building Python wheel..."
    
    # Clean previous builds
    rm -rf build/ dist/ *.egg-info/
    
    # Build wheel
    python3 setup.py sdist bdist_wheel
    
    log_success "Python wheel built successfully"
    ls -la dist/
}

# Function to test images
test_images() {
    log_info "Testing built images..."
    
    # Test full image
    log_info "Testing full image..."
    docker run --rm ${REGISTRY}/${IMAGE_NAME}-full:latest python3 -c "import orchestrator; print('Full image OK')"
    
    # Test demo image
    log_info "Testing demo image..."
    docker run --rm ${REGISTRY}/${IMAGE_NAME}-demo:latest python3 -c "import dashboard_api; print('Demo image OK')"
    
    log_success "All images tested successfully"
}

# Function to push images (if registry is provided)
push_images() {
    if [ -n "$DOCKER_REGISTRY" ]; then
        log_info "Pushing images to registry: $DOCKER_REGISTRY"
        
        # Push full image
        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}-full:${VERSION}
        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}-full:latest
        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}-full:${GIT_COMMIT}
        
        # Push demo image
        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}-demo:${VERSION}
        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}-demo:latest
        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}-demo:${GIT_COMMIT}
        
        log_success "Images pushed to registry"
    else
        log_warning "DOCKER_REGISTRY not set, skipping push"
    fi
}

# Function to generate build report
generate_report() {
    local report_file="build-report-${VERSION}-${GIT_COMMIT}.json"
    
    log_info "Generating build report: $report_file"
    
    cat > "$report_file" << EOF
{
  "build_info": {
    "version": "${VERSION}",
    "git_commit": "${GIT_COMMIT}",
    "build_date": "${BUILD_DATE}",
    "builder": "$(whoami)@$(hostname)"
  },
  "images": {
    "full": {
      "tags": [
        "${REGISTRY}/${IMAGE_NAME}-full:${VERSION}",
        "${REGISTRY}/${IMAGE_NAME}-full:latest",
        "${REGISTRY}/${IMAGE_NAME}-full:${GIT_COMMIT}"
      ],
      "size": "$(docker images --format "table {{.Size}}" ${REGISTRY}/${IMAGE_NAME}-full:latest | tail -n 1)"
    },
    "demo": {
      "tags": [
        "${REGISTRY}/${IMAGE_NAME}-demo:${VERSION}",
        "${REGISTRY}/${IMAGE_NAME}-demo:latest",
        "${REGISTRY}/${IMAGE_NAME}-demo:${GIT_COMMIT}"
      ],
      "size": "$(docker images --format "table {{.Size}}" ${REGISTRY}/${IMAGE_NAME}-demo:latest | tail -n 1)"
    }
  },
  "artifacts": {
    "python_wheel": "dist/netkrak-${VERSION}-py3-none-any.whl",
    "source_distribution": "dist/netkrak-${VERSION}.tar.gz"
  }
}
EOF
    
    log_success "Build report generated: $report_file"
}

# Main execution
main() {
    log_info "Starting net.krak build process..."
    log_info "Version: $VERSION"
    log_info "Git commit: $GIT_COMMIT"
    log_info "Build date: $BUILD_DATE"
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if git is available
    if ! command -v git >/dev/null 2>&1; then
        log_warning "Git not found, using 'unknown' for commit hash"
    fi
    
    # Build Python wheel
    if [ "$1" != "--docker-only" ]; then
        build_wheel
    fi
    
    # Build Docker images
    build_image "full" "-full" "Full functionality image with all pentest tools"
    build_image "demo" "-demo" "Demo image with web UI only (safe mode)"
    
    # Test images
    test_images
    
    # Push images if registry is provided
    push_images
    
    # Generate build report
    generate_report
    
    log_success "Build process completed successfully!"
    
    echo ""
    echo "Available images:"
    docker images | grep "${REGISTRY}/${IMAGE_NAME}"
    
    echo ""
    echo "Usage examples:"
    echo "  Full functionality: docker run --rm --cap-add=NET_ADMIN --cap-add=NET_RAW --network host ${REGISTRY}/${IMAGE_NAME}-full:latest"
    echo "  Demo mode:         docker run --rm -p 5000:5000 ${REGISTRY}/${IMAGE_NAME}-demo:latest"
    echo "  Docker Compose:    docker-compose up netkrak-full"
    echo "  Demo Compose:      docker-compose up netkrak-demo"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--docker-only] [--help]"
        echo ""
        echo "Options:"
        echo "  --docker-only    Build only Docker images, skip Python wheel"
        echo "  --help, -h       Show this help message"
        echo ""
        echo "Environment variables:"
        echo "  DOCKER_REGISTRY  Registry to push images to (optional)"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac