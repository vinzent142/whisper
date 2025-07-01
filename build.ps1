# Whisper Transcription Service - Docker Build Script (PowerShell)
# This script builds the Docker image with optional proxy support

param(
    [string]$Name = "whisper-transcription",
    [string]$Tag = "latest",
    [string]$Proxy = "",
    [string]$HttpsProxy = "",
    [switch]$NoCache,
    [switch]$Help
)

# Function to write colored output
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\build.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Name NAME             Docker image name (default: whisper-transcription)"
    Write-Host "  -Tag TAG               Docker image tag (default: latest)"
    Write-Host "  -Proxy PROXY           HTTP proxy URL (e.g., http://proxy.company.com:8080)"
    Write-Host "  -HttpsProxy PROXY      HTTPS proxy URL"
    Write-Host "  -NoCache               Build without using Docker cache"
    Write-Host "  -Help                  Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\build.ps1                                      # Basic build"
    Write-Host "  .\build.ps1 -Name my-whisper -Tag v1.0          # Custom name and tag"
    Write-Host "  .\build.ps1 -Proxy http://proxy:8080            # With HTTP proxy"
    Write-Host "  .\build.ps1 -Proxy http://proxy:8080 -NoCache   # With proxy and no cache"
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Validate Docker is installed and running
try {
    $dockerVersion = docker --version 2>$null
    if (-not $dockerVersion) {
        Write-Error "Docker is not installed or not in PATH"
        exit 1
    }
} catch {
    Write-Error "Docker is not installed or not in PATH"
    exit 1
}

try {
    docker info 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker daemon is not running"
        exit 1
    }
} catch {
    Write-Error "Docker daemon is not running"
    exit 1
}

# Check if Dockerfile exists
if (-not (Test-Path "Dockerfile")) {
    Write-Error "Dockerfile not found in current directory"
    exit 1
}

# Build Docker arguments
$dockerBuildArgs = @()

if ($Proxy) {
    $dockerBuildArgs += "--build-arg", "http_proxy=$Proxy"
    $dockerBuildArgs += "--build-arg", "HTTP_PROXY=$Proxy"
}

if ($HttpsProxy) {
    $dockerBuildArgs += "--build-arg", "https_proxy=$HttpsProxy"
    $dockerBuildArgs += "--build-arg", "HTTPS_PROXY=$HttpsProxy"
}

if ($NoCache) {
    $dockerBuildArgs += "--no-cache"
}

# Build the Docker image
$fullImageName = "${Name}:${Tag}"

Write-Info "Starting Docker build..."
Write-Info "Image name: $fullImageName"
Write-Info "Dockerfile path: ."

if ($Proxy) {
    Write-Info "HTTP Proxy: $Proxy"
}

if ($HttpsProxy) {
    Write-Info "HTTPS Proxy: $HttpsProxy"
}

if ($NoCache) {
    Write-Info "Building without cache"
}

# Prepare the build command
$buildCmd = @("docker", "build") + $dockerBuildArgs + @("-t", $fullImageName, ".")

Write-Info "Executing: $($buildCmd -join ' ')"
Write-Host ""

# Execute the build command
try {
    & $buildCmd[0] $buildCmd[1..($buildCmd.Length-1)]
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully: $fullImageName"
        
        # Show image information
        Write-Host ""
        Write-Info "Image details:"
        docker images $Name --format "table {{.Repository}}`t{{.Tag}}`t{{.ID}}`t{{.CreatedAt}}`t{{.Size}}"
        
        Write-Host ""
        Write-Success "Build completed successfully!"
        Write-Info "You can now run the container with:"
        Write-Host "  docker run --rm -v `$(pwd)/input:/input -v `$(pwd)/output:/output $fullImageName"
    } else {
        Write-Error "Docker build failed"
        exit 1
    }
} catch {
    Write-Error "Docker build failed: $($_.Exception.Message)"
    exit 1
}
