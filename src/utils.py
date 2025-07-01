import os
import logging
import torch
import platform
import psutil
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

def log_device_info():
    """
    Log detailed information about the device being used (CPU/GPU).
    """
    logger.info("=== DEVICE INFORMATION ===")
    
    # System information
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.architecture()[0]}")
    logger.info(f"Processor: {platform.processor()}")
    
    # CPU information
    try:
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        logger.info(f"CPU Cores: {cpu_count} physical, {cpu_count_logical} logical")
        
        # CPU frequency
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            logger.info(f"CPU Frequency: {cpu_freq.current:.2f} MHz (max: {cpu_freq.max:.2f} MHz)")
    except Exception as e:
        logger.warning(f"Could not get CPU info: {e}")
    
    # Memory information
    try:
        memory = psutil.virtual_memory()
        logger.info(f"RAM: {memory.total / (1024**3):.2f} GB total, {memory.available / (1024**3):.2f} GB available")
    except Exception as e:
        logger.warning(f"Could not get memory info: {e}")
    
    # PyTorch and GPU information
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        logger.info(f"CUDA version: {torch.version.cuda}")
        gpu_count = torch.cuda.device_count()
        logger.info(f"GPU count: {gpu_count}")
        
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            logger.info(f"GPU {i}: {gpu_name} ({gpu_memory:.2f} GB)")
            
        # Current GPU memory usage
        try:
            current_device = torch.cuda.current_device()
            memory_allocated = torch.cuda.memory_allocated(current_device) / (1024**3)
            memory_reserved = torch.cuda.memory_reserved(current_device) / (1024**3)
            logger.info(f"Current GPU memory: {memory_allocated:.2f} GB allocated, {memory_reserved:.2f} GB reserved")
        except Exception as e:
            logger.warning(f"Could not get GPU memory info: {e}")
    else:
        logger.info("GPU: Not available - using CPU")
    
    # Determine device that will be used
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Whisper will use: {device.upper()}")
    
    logger.info("==========================")
