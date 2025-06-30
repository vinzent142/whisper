#!/usr/bin/env python3
"""
Whisper Transcription Service
Transcribes German audio files and generates titles for Service Desk tickets.
"""

import sys
import logging
import os
from transcriber import WhisperTranscriber
from title_generator import GermanTitleGenerator
from utils import (
    validate_input_file,
    ensure_output_directory,
    write_transcription_output,
    get_input_file_path,
    get_output_file_path
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Exit codes
EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 1
EXIT_PROCESSING_ERROR = 2
EXIT_OUTPUT_ERROR = 3

def main():
    """
    Main transcription pipeline.
    """
    logger.info("Starting Whisper transcription service")
    
    try:
        # Step 1: Get input file path
        input_file = get_input_file_path()
        if not input_file:
            logger.error("No input file found")
            sys.exit(EXIT_INPUT_ERROR)
        
        # Step 2: Validate input file
        if not validate_input_file(input_file):
            logger.error("Input file validation failed")
            sys.exit(EXIT_INPUT_ERROR)
        
        # Step 3: Prepare output
        output_file = get_output_file_path()
        if not ensure_output_directory(output_file):
            logger.error("Output directory preparation failed")
            sys.exit(EXIT_OUTPUT_ERROR)
        
        # Step 4: Initialize and load Whisper model
        logger.info("Initializing Whisper transcriber")
        model_size = os.getenv("WHISPER_MODEL_SIZE", "large-v3")
        logger.info(f"Using Whisper model size: {model_size}")
        transcriber = WhisperTranscriber(model_size=model_size)
        
        if not transcriber.load_model():
            logger.error("Failed to load Whisper model")
            sys.exit(EXIT_PROCESSING_ERROR)
        
        # Step 5: Transcribe audio
        logger.info("Starting audio transcription")
        transcription = transcriber.transcribe_audio(input_file)
        
        if not transcription:
            logger.error("Audio transcription failed")
            sys.exit(EXIT_PROCESSING_ERROR)
        
        logger.info(f"Transcription completed: {len(transcription)} characters")
        
        # Step 6: Initialize and load title generation model
        logger.info("Initializing German title generator")
        title_generator = GermanTitleGenerator()
        
        if not title_generator.load_model():
            logger.error("Failed to load title generation model")
            sys.exit(EXIT_PROCESSING_ERROR)
        
        # Step 7: Generate title
        logger.info("Generating title from transcription")
        title = title_generator.generate_title(transcription, max_length=50)
        
        if not title:
            logger.error("Title generation failed")
            sys.exit(EXIT_PROCESSING_ERROR)
        
        logger.info(f"Title generated: {title}")
        
        # Step 8: Write output
        logger.info("Writing transcription output")
        if not write_transcription_output(output_file, title, transcription):
            logger.error("Failed to write output file")
            sys.exit(EXIT_OUTPUT_ERROR)
        
        logger.info("Transcription service completed successfully")
        logger.info(f"Output written to: {output_file}")
        
        # Log summary
        logger.info("=== TRANSCRIPTION SUMMARY ===")
        logger.info(f"Input file: {input_file}")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Title: {title}")
        logger.info(f"Transcription length: {len(transcription)} characters")
        logger.info("=============================")
        
        sys.exit(EXIT_SUCCESS)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(EXIT_PROCESSING_ERROR)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(EXIT_PROCESSING_ERROR)

if __name__ == "__main__":
    main()
