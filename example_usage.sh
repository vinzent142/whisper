#!/bin/bash
# Example usage script for Whisper Transcription Service

set -e

echo "🎙️  Whisper Transcription Service - Example Usage"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
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

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

print_step "Building Docker image..."
if docker build -t whisper-transcriber .; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Check if input directory has WAV files
if [ ! -d "input" ]; then
    mkdir -p input
    print_warning "Created input directory"
fi

wav_files=$(find input -name "*.wav" -o -name "*.WAV" 2>/dev/null | wc -l)
if [ "$wav_files" -eq 0 ]; then
    print_warning "No WAV files found in input/ directory"
    echo "Please place your German audio files (*.wav) in the input/ directory"
    echo "Example: cp your-recording.wav input/"
    echo ""
    echo "For testing, you can create a sample WAV file or download one:"
    echo "wget -O input/sample.wav 'https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav'"
    echo ""
    echo "Then run this script again."
    exit 0
fi

print_step "Found $wav_files WAV file(s) in input directory"

# Ensure output directory exists
mkdir -p output

# Process each WAV file
for wav_file in input/*.wav input/*.WAV 2>/dev/null; do
    # Skip if no files match the pattern
    [ -e "$wav_file" ] || continue
    
    filename=$(basename "$wav_file")
    print_step "Processing: $filename"
    
    # Run the transcription
    if docker run --rm \
        -v "$(pwd)/input:/input:ro" \
        -v "$(pwd)/output:/output" \
        whisper-transcriber; then
        
        print_success "Transcription completed for $filename"
        
        # Show the result
        if [ -f "output/transcription.txt" ]; then
            echo ""
            echo "📄 Transcription Result:"
            echo "========================"
            cat output/transcription.txt
            echo ""
            echo "========================"
            echo ""
        fi
    else
        print_error "Transcription failed for $filename"
    fi
    
    # Only process the first file in this example
    break
done

print_success "Example usage completed!"
echo ""
echo "💡 Tips:"
echo "- Place multiple WAV files in input/ for batch processing"
echo "- Check output/transcription.txt for results"
echo "- Use 'docker-compose up' for easier development"
echo "- Set WHISPER_MODEL_SIZE=base for faster testing"
echo ""
echo "🚀 Production usage:"
echo "docker run --rm -v /path/to/audio.wav:/input/audio.wav:ro -v /path/to/output:/output whisper-transcriber"
