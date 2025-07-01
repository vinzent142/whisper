# Whisper Transcription Service

A containerized German audio transcription service using OpenAI Whisper and German title generation for Service Desk ticket creation.

## Features

- **German Language Optimized**: Whisper configured specifically for German audio transcription
- **Automatic Title Generation**: Uses `aiautomationlab/german-news-title-gen-mt5` for intelligent German titles (max 50 characters)
- **Multiple Model Support**: Choose from small, medium, large-v3, or turbo models during build
- **Device Detection**: Automatic logging of CPU/GPU information and hardware specifications
- **Fully Offline**: All models pre-downloaded in Docker image, no internet connection required after build
- **Service Desk Ready**: Output format designed for CA Service Desk API integration
- **Robust Error Handling**: Clear exit codes for automation and monitoring
- **Scalable**: CPU optimized for laptop testing, GPU ready for production server

## Quick Start

### 1. Build the Container

```bash
# Build the Docker image with default large-v3 model
./build.sh

# Or build with a specific model
./build.sh -m small -t v1.0
./build.sh -m turbo -t production

# On Windows
.\build.ps1 -Model small -Tag v1.0
```

### 2. Prepare Directories

```bash
# Create input and output directories
mkdir -p input output

# Place your WAV file in the input directory
cp your-recording.wav input/
```

### 3. Run Transcription

```bash
# Run the transcription service (using default large-v3 model)
docker run --rm \
  -v $(pwd)/input:/input:ro \
  -v $(pwd)/output:/output \
  whisper-transcription:large-v3_latest

# Or use a specific model build
docker run --rm \
  -v $(pwd)/input:/input:ro \
  -v $(pwd)/output:/output \
  whisper-transcription:small_v1.0
```

### 4. Get Results

The transcribed text with title will be available in `output/transcription.txt`:

```
Service Desk Problem mit Drucker

Guten Tag, ich habe ein Problem mit meinem Drucker. Der Drucker druckt nicht mehr und zeigt eine Fehlermeldung an. Können Sie mir bitte helfen?
```

## Development Setup

### Using Docker Compose

```bash
# For production testing
docker-compose up whisper-transcriber

# For development with smaller models
docker-compose --profile dev up whisper-transcriber-dev
```

## Project Structure

```
whisper-transcription/
├── Dockerfile                 # Multi-stage build with model downloads
├── docker-compose.yml         # Development and testing setup
├── requirements.txt          # Python dependencies
├── src/
│   ├── main.py              # Main entry point
│   ├── transcriber.py       # Whisper transcription logic
│   ├── title_generator.py   # German title generation
│   └── utils.py             # File handling utilities
├── input/                   # Mount point for WAV files
├── output/                  # Mount point for TXT output
└── README.md               # This file
```

## Configuration

### Environment Variables

- `WHISPER_MODEL_SIZE`: Whisper model size (default: `large-v3`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `PYTHONUNBUFFERED`: Python output buffering (default: `1`)

### Model Selection

Available Whisper models (specified during build):

**For Laptop Testing:**
- `small`: Good balance (~244 MB)
- `medium`: Better accuracy (~769 MB)

**For Production Server (A16 GPU):**
- `large-v3`: Best accuracy (~1550 MB) - **Default**
- `turbo`: Fast and accurate (~798 MB)

### Build Options

The build scripts support the following options:

**Linux/macOS (build.sh):**
```bash
./build.sh [OPTIONS]
  -n, --name NAME        Docker image name (default: whisper-transcription)
  -t, --tag TAG          Docker image tag (default: latest)
  -m, --model MODEL      Whisper model: small, medium, large-v3, turbo (default: large-v3)
  -p, --proxy PROXY      HTTP proxy URL
  -s, --https-proxy PROXY HTTPS proxy URL
  --no-cache             Build without using Docker cache
  -h, --help             Show help message
```

**Windows (build.ps1):**
```powershell
.\build.ps1 [OPTIONS]
  -Name NAME             Docker image name (default: whisper-transcription)
  -Tag TAG               Docker image tag (default: latest)
  -Model MODEL           Whisper model: small, medium, large-v3, turbo (default: large-v3)
  -Proxy PROXY           HTTP proxy URL
  -HttpsProxy PROXY      HTTPS proxy URL
  -NoCache               Build without using Docker cache
  -Help                  Show help message
```

**Image Tagging:**
Images are automatically tagged with the model name: `imagename:model_tag`
- Example: `whisper-transcription:large-v3_latest`
- Example: `whisper-transcription:small_v1.0`

## Usage Patterns

### Single File Processing

```bash
# Standard usage
docker run --rm \
  -v /path/to/recording.wav:/input/audio.wav:ro \
  -v /path/to/output:/output \
  whisper-transcriber
```

### Batch Processing Script

```bash
#!/bin/bash
for wav_file in recordings/*.wav; do
    filename=$(basename "$wav_file" .wav)
    mkdir -p "output/$filename"
    
    docker run --rm \
      -v "$wav_file:/input/audio.wav:ro" \
      -v "$(pwd)/output/$filename:/output" \
      whisper-transcriber
      
    if [ $? -eq 0 ]; then
        echo "✓ Processed: $filename"
    else
        echo "✗ Failed: $filename"
    fi
done
```

## Exit Codes

- **0**: Success - transcription completed
- **1**: Input file error (missing, invalid format)
- **2**: Processing error (transcription or title generation failed)
- **3**: Output error (cannot write result)

## Hardware Requirements

### Development (Laptop)
- **CPU**: Intel i7 or equivalent
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 4GB for Docker image
- **Processing Time**: ~2-5 minutes per minute of audio

### Production (Server)
- **GPU**: NVIDIA A16 (16GB VRAM)
- **RAM**: 16GB minimum
- **Storage**: 4GB for Docker image
- **Processing Time**: ~30 seconds per minute of audio

## Audio Requirements

- **Format**: WAV files
- **Language**: German
- **Quality**: Phone recording quality supported
- **Length**: No specific limits (tested up to 60 minutes)

## Integration with CA Service Desk

The output format is designed for easy API integration:

```python
# Example Python integration
import requests

def create_service_desk_ticket(transcription_file):
    with open(transcription_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    title = lines[0]
    description = '\n'.join(lines[2:])  # Skip blank line
    
    ticket_data = {
        'summary': title,
        'description': description,
        'category': 'Phone Support',
        'priority': 'Medium'
    }
    
    # Your CA Service Desk API call here
    response = requests.post('your-api-endpoint', json=ticket_data)
    return response
```

## Troubleshooting

### Common Issues

1. **Out of Memory Error**
   ```bash
   # Reduce model size for testing
   docker run -e WHISPER_MODEL_SIZE=base ...
   ```

2. **No Audio File Found**
   ```bash
   # Check file permissions and format
   ls -la input/
   file input/*.wav
   ```

3. **Permission Denied on Output**
   ```bash
   # Fix output directory permissions
   chmod 755 output/
   ```

### Debug Mode

```bash
# Run with debug logging
docker run -e LOG_LEVEL=DEBUG --rm \
  -v $(pwd)/input:/input:ro \
  -v $(pwd)/output:/output \
  whisper-transcriber
```

## Production Deployment

### Server Setup

1. **Build for Production**
   ```bash
   docker build -t whisper-transcriber:prod .
   ```

2. **GPU Support** (for A16 server)
   ```bash
   # Install NVIDIA Container Toolkit
   # Run with GPU support
   docker run --gpus all --rm \
     -v /path/to/input:/input:ro \
     -v /path/to/output:/output \
     whisper-transcriber:prod
   ```

3. **Automated Processing**
   ```bash
   # Example systemd service or cron job
   # Monitor input directory and process new files
   ```

## License

This project is designed for internal Service Desk use. Model licenses:
- OpenAI Whisper: MIT License
- aiautomationlab/german-news-title-gen-mt5: Apache 2.0 License

## Support

For issues and questions, contact the Service Desk development team.
