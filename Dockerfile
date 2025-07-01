# Multi-stage Docker build for Whisper transcription service
# Stage 1: Model download and preparation
FROM python:3.11-slim AS model-downloader

# Accept build arguments
ARG http_proxy
ARG https_proxy
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG WHISPER_MODEL=large-v3

# Set proxy environment variables if provided
ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV WHISPER_MODEL=${WHISPER_MODEL}

# Install system dependencies for model downloading
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for model downloading
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create directories for models
RUN mkdir -p /models/whisper /models/title-generator

# Download Whisper model
RUN echo "Downloading Whisper model: $WHISPER_MODEL" && \
    python -c "import whisper; import os; model_name=os.getenv('WHISPER_MODEL', 'large-v3'); print(f'Loading model: {model_name}'); whisper.load_model(model_name, download_root='/models/whisper'); print(f'Model {model_name} downloaded successfully')"

# Download German title generation model
RUN python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
    AutoTokenizer.from_pretrained('aiautomationlab/german-news-title-gen-mt5', cache_dir='/models/title-generator'); \
    AutoModelForSeq2SeqLM.from_pretrained('aiautomationlab/german-news-title-gen-mt5', cache_dir='/models/title-generator')"

# Stage 2: Production image
FROM python:3.11-slim

# Accept proxy arguments
ARG http_proxy
ARG https_proxy
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG WHISPER_MODEL=large-v3

# Set proxy environment variables if provided
ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pre-downloaded models from stage 1
COPY --from=model-downloader /models /root/.cache

# Copy application source code
COPY src/ ./src/

# Create input and output directories
RUN mkdir -p /input /output

# Set environment variables
ENV PYTHONPATH=/app/src
ENV HF_HOME=/root/.cache/title-generator
ENV WHISPER_CACHE=/root/.cache/whisper
ENV WHISPER_MODEL=${WHISPER_MODEL}

# Make main script executable
RUN chmod +x src/main.py

# Set the entrypoint
ENTRYPOINT ["python", "src/main.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Labels
LABEL maintainer="Service Desk Team"
LABEL description="Whisper transcription service for German audio files"
LABEL version="1.0.0"
LABEL whisper.model="${WHISPER_MODEL}"
