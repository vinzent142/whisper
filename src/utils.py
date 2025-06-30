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
