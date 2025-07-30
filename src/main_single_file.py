#!/usr/bin/env python3
"""
Whisper Transcription Service - Single File Mode
Legacy single-file processing mode for backwards compatibility.
Transcribes German audio files and generates titles for Service Desk tickets.
"""

import sys
import logging
import os
from transcriber import WhisperTranscriber
from title_generator import GermanTitleGenerator
from utils import validate_input_file, ensure_output_directory
from pathlib import Path

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

def get_input_file_path() -> str:
    """
    Get the path to the input WAV file from the /input directory.
    
    Returns:
        str: Path to the input file, or None if not found
    """
    input_dir = Path("/input")
    
    if not input_dir.exists():
        logger.error("Input directory /input does not exist")
        return None
    
    # Look for WAV files in the input directory
    wav_files = list(input_dir.glob("*.wav")) + list(input_dir.glob("*.WAV"))
    
    if not wav_files:
        logger.error("No WAV files found in /input directory")
        return None
    
    if len(wav_files) > 1:
        logger.warning(f"Multiple WAV files found, using first: {wav_files[0]}")
    
    return str(wav_files[0])

def get_output_file_path() -> str:
    """
    Get the path for the output TXT file.
    
    Returns:
        str: Path to the output file
    """
    return "/output/transcription.txt"

def write_transcription_output(output_path: str, title: str, transcription: str) -> bool:
    """
    Write the formatted transcription output to file.
    
    Args:
        output_path: Path to the output file
        title: Generated title (max 50 chars)
        transcription: Full transcription text
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure title is within 50 character limit
        if len(title) > 50:
            title = title[:47] + "..."
            logger.warning(f"Title truncated to 50 characters: {title}")
        
        # Format output: Title + blank line + transcription
        output_content = f"{title}\n\n{transcription}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
            
        logger.info(f"Transcription output written to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        return False

def main():
    """
    Main transcription pipeline for single file processing.
    """
    logger.info("Starting Whisper transcription service (single file mode)")
    
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
