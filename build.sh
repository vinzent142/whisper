#!/bin/bash

# Whisper Transcription Service - Docker Build Script
# This script builds the Docker image with optional proxy support

set -e  # Exit on any error

# Default values
IMAGE_NAME="whisper-transcription"
IMAGE_TAG="latest"
DOCKERFILE_PATH="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --name NAME        Docker image name (default: whisper-transcription)"
    echo "  -t, --tag TAG          Docker image tag (default: latest)"
    echo "  -p, --proxy PROXY      HTTP proxy URL (e.g., http://proxy.company.com:8080)"
    echo "  -s, --https-proxy PROXY HTTPS proxy URL"
    echo "  --no-cache             Build without using Docker cache"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Basic build"
    echo "  $0 -n my-whisper -t v1.0             # Custom name and tag"
    echo "  $0 -p http://proxy:8080              # With HTTP proxy"
    echo "  $0 -p http://proxy:8080 --no-cache   # With proxy and no cache"
}

# Parse command line arguments
DOCKER_BUILD_ARGS=""
NO_CACHE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -p|--proxy)
            HTTP_PROXY="$2"
            DOCKER_BUILD_ARGS="$DOCKER_BUILD_ARGS --build-arg http_proxy=$2 --build-arg HTTP_PROXY=$2"
            shift 2
            ;;
        -s|--https-proxy)
            HTTPS_PROXY="$2"
            DOCKER_BUILD_ARGS="$DOCKER_BUILD_ARGS --build-arg https_proxy=$2 --build-arg HTTPS_PROXY=$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate Docker is installed and running
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    exit 1
fi

# Check if Dockerfile exists
if [[ ! -f "$DOCKERFILE_PATH/Dockerfile" ]]; then
    print_error "Dockerfile not found in $DOCKERFILE_PATH"
    exit 1
fi

# Build the Docker image
FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_TAG"

print_info "Starting Docker build..."
print_info "Image name: $FULL_IMAGE_NAME"
print_info "Dockerfile path: $DOCKERFILE_PATH"

if [[ -n "$HTTP_PROXY" ]]; then
    print_info "HTTP Proxy: $HTTP_PROXY"
fi

if [[ -n "$HTTPS_PROXY" ]]; then
    print_info "HTTPS Proxy: $HTTPS_PROXY"
fi

if [[ -n "$NO_CACHE" ]]; then
    print_info "Building without cache"
fi

# Execute the build command
BUILD_CMD="docker build $NO_CACHE $DOCKER_BUILD_ARGS -t $FULL_IMAGE_NAME $DOCKERFILE_PATH"

print_info "Executing: $BUILD_CMD"
echo ""

if eval $BUILD_CMD; then
    print_success "Docker image built successfully: $FULL_IMAGE_NAME"
    
    # Show image information
    echo ""
    print_info "Image details:"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"
    
    echo ""
    print_success "Build completed successfully!"
    print_info "You can now run the container with:"
    echo "  docker run --rm -v \$(pwd)/input:/input -v \$(pwd)/output:/output $FULL_IMAGE_NAME"
    
else
    print_error "Docker build failed"
    exit 1
fi
