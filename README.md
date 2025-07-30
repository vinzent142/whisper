# Whisper Transcription Service

A containerized German audio transcription service using OpenAI Whisper and German title generation for Service Desk ticket creation.

## Features

- **Continuous Processing**: Monitors input directory and processes files automatically as they arrive
- **Model Persistence**: Models stay loaded in memory for faster processing of subsequent files
- **German Language Optimized**: Whisper configured specifically for German audio transcription
- **Automatic Title Generation**: Uses `aiautomationlab/german-news-title-gen-mt5` for intelligent German titles (max 50 characters)
- **Fully Offline**: All models pre-downloaded in Docker image, no internet connection required after build
- **Service Desk Ready**: Output format designed for CA Service Desk API integration
- **Robust Error Handling**: Graceful shutdown and comprehensive error handling
- **File Management**: Automatically moves processed files to output directory with matching names
- **Scalable**: CPU optimized for laptop testing, GPU ready for production server

## Quick Start

### 1. Build the Container

```bash
# Build the Docker image (this will download all models)
docker build -t whisper-transcriber .
```

### 2. Prepare Directories

```bash
# Create input and output directories
mkdir -p input output
```

### 3. Start Continuous Service

```bash
# Run the continuous transcription service
docker-compose up whisper-transcriber
```

### 4. Add Files for Processing

```bash
# Copy WAV files to input directory while service is running
cp your-recording.wav input/
cp another-recording.wav input/
```

### 5. Get Results

For each input file, you'll get both the original audio and transcription in the output directory:

**Input:** `input/meeting-recording.wav`
**Output:** 
- `output/meeting-recording.wav` (original audio file)
- `output/meeting-recording.txt` (transcription with title)

**Example output file content:**
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
│   ├── main.py              # Main entry point (continuous service)
│   ├── main_single_file.py  # Legacy single-file processing mode
│   ├── service_manager.py   # Continuous file monitoring service
│   ├── model_manager.py     # Model persistence and management
│   ├── file_processor.py    # Individual file processing logic
│   ├── transcriber.py       # Whisper transcription logic
│   ├── title_generator.py   # German title generation
│   └── utils.py             # File handling utilities
├── input/                   # Mount point for WAV files
├── output/                  # Mount point for processed files
└── README.md               # This file
```

## Configuration

### Environment Variables

**Core Configuration:**
- `WHISPER_MODEL_SIZE`: Whisper model size (default: `large-v3`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `PYTHONUNBUFFERED`: Python output buffering (default: `1`)

**Continuous Service Configuration:**
- `WATCH_INTERVAL`: File monitoring interval in seconds (default: `1.0`)
- `PRELOAD_MODELS`: Preload models on startup (default: `true`)

### Model Selection

**For Laptop Testing:**
- `base`: Fastest, lower accuracy (~39 MB)
- `small`: Good balance (~244 MB)
- `medium`: Better accuracy (~769 MB)

**For Production Server (A16 GPU):**
- `large-v3`: Best accuracy (~1550 MB) - Recommended

## Continuous Processing Workflow

The service operates in a continuous loop:

1. **Startup**: Container starts and loads models into memory
2. **Monitoring**: Watches `/input` directory for new `.wav` files
3. **Detection**: When a new file is detected, it's added to the processing queue
4. **Processing**: File is transcribed and title is generated using cached models
5. **Output**: Creates `.txt` file with transcription and moves original `.wav` to `/output`
6. **Repeat**: Continues monitoring for new files

### File Processing Flow

```
input/recording.wav  →  [Processing]  →  output/recording.wav
                                     →  output/recording.txt
```

### Performance Benefits

- **First file**: ~2-5 minutes (includes model loading time)
- **Subsequent files**: ~30 seconds - 2 minutes (models already loaded)
- **Memory usage**: Models stay loaded, reducing processing time by 80-90%

## Usage Patterns

### Continuous Service (Recommended)

```bash
# Start the continuous service
docker-compose up whisper-transcriber

# Add files while service is running
cp recording1.wav input/
cp recording2.wav input/
# Files are processed automatically
```

### Manual Container Run

```bash
# Run continuous service manually
docker run --rm \
  -v $(pwd)/input:/input:ro \
  -v $(pwd)/output:/output \
  whisper-transcriber
```

### Legacy Single File Mode

```bash
# Use the legacy single-file processor
docker run --rm \
  -v /path/to/recording.wav:/input/audio.wav:ro \
  -v /path/to/output:/output \
  --entrypoint python \
  whisper-transcriber src/main_single_file.py
```

### Custom Configuration

```bash
# Run with custom settings
docker run --rm \
  -e WHISPER_MODEL_SIZE=base \
  -e WATCH_INTERVAL=0.5 \
  -e LOG_LEVEL=DEBUG \
  -v $(pwd)/input:/input:ro \
  -v $(pwd)/output:/output \
  whisper-transcriber
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
