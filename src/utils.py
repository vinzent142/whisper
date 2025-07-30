import os
import logging
import soundfile as sf
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_input_file(input_path: str) -> bool:
    """
    Validate that the input WAV file exists and is readable.
    
    Args:
        input_path: Path to the input WAV file
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    try:
        if not os.path.exists(input_path):
            logger.error(f"Input file does not exist: {input_path}")
            return False
            
        # Try to read the audio file to validate format
        data, samplerate = sf.read(input_path)
        logger.info(f"Audio file validated: {len(data)} samples at {samplerate}Hz")
        return True
        
    except Exception as e:
        logger.error(f"Error validating input file: {e}")
        return False

def ensure_output_directory(output_path: str) -> bool:
    """
    Ensure the output directory exists and is writable.
    
    Args:
        output_path: Path to the output directory
        
    Returns:
        bool: True if directory is ready, False otherwise
    """
    try:
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = output_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        
        logger.info(f"Output directory ready: {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error preparing output directory: {e}")
        return False

# Note: write_transcription_output, get_input_file_path, and get_output_file_path
# functions have been moved to file_processor.py for the continuous service architecture
