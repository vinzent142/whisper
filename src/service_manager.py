import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import List
from file_processor import FileProcessor
from model_manager import ModelManager

logger = logging.getLogger(__name__)

class ServiceManager:
    """
    Manages the continuous file processing service.
    Monitors input directory and processes files as they arrive.
    """
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.model_manager = ModelManager()
        self.running = True
        self.watch_interval = float(os.getenv("WATCH_INTERVAL", "1.0"))  # seconds
        self.input_dir = Path("/input")
        self.processed_files = set()  # Track processed files to avoid reprocessing
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    def start(self):
        """
        Start the continuous file processing service.
        """
        logger.info("Starting Whisper transcription service in continuous mode")
        logger.info(f"Monitoring directory: {self.input_dir}")
        logger.info(f"Watch interval: {self.watch_interval} seconds")
        
        # Ensure input directory exists
        if not self._ensure_input_directory():
            logger.error("Input directory setup failed")
            sys.exit(1)
        
        # Optional: Preload models to avoid delay on first file
        preload_models = os.getenv("PRELOAD_MODELS", "true").lower() == "true"
        if preload_models:
            logger.info("Preloading models...")
            if not self.model_manager.preload_models():
                logger.warning("Model preloading failed, will load on first file")
        
        logger.info("Service started successfully, waiting for files...")
        
        # Main processing loop
        try:
            while self.running:
                self._process_cycle()
                time.sleep(self.watch_interval)
                
        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in service loop: {e}", exc_info=True)
        finally:
            self._shutdown()
    
    def _process_cycle(self):
        """
        Single processing cycle: check for new files and process them.
        """
        try:
            new_files = self._find_new_wav_files()
            
            if new_files:
                logger.info(f"Found {len(new_files)} new file(s) to process")
                
                for file_path in new_files:
                    if not self.running:
                        logger.info("Shutdown requested, stopping file processing")
                        break
                    
                    self._process_single_file(file_path)
            
        except Exception as e:
            logger.error(f"Error in processing cycle: {e}", exc_info=True)
    
    def _find_new_wav_files(self) -> List[str]:
        """
        Find new WAV files in the input directory that haven't been processed.
        
        Returns:
            List[str]: List of new WAV file paths
        """
        try:
            if not self.input_dir.exists():
                return []
            
            # Find all WAV files
            wav_files = []
            for pattern in ["*.wav", "*.WAV"]:
                wav_files.extend(self.input_dir.glob(pattern))
            
            # Filter out already processed files
            new_files = []
            for file_path in wav_files:
                file_str = str(file_path)
                if file_str not in self.processed_files:
                    # Additional check: ensure file is not currently being written
                    if self._is_file_ready(file_path):
                        new_files.append(file_str)
                    else:
                        logger.debug(f"File not ready yet: {file_path}")
            
            return sorted(new_files)  # Process in alphabetical order
            
        except Exception as e:
            logger.error(f"Error finding new files: {e}")
            return []
    
    def _is_file_ready(self, file_path: Path) -> bool:
        """
        Check if a file is ready for processing (not being written to).
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if file is ready, False otherwise
        """
        try:
            # Check if file size is stable (simple approach)
            initial_size = file_path.stat().st_size
            time.sleep(0.1)  # Wait 100ms
            final_size = file_path.stat().st_size
            
            return initial_size == final_size and final_size > 0
            
        except Exception as e:
            logger.debug(f"Error checking file readiness: {e}")
            return False
    
    def _process_single_file(self, file_path: str):
        """
        Process a single file and handle the result.
        
        Args:
            file_path: Path to the file to process
        """
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Mark file as being processed
            self.processed_files.add(file_path)
            
            # Process the file
            success = self.file_processor.process_file(file_path)
            
            if success:
                logger.info(f"Successfully processed: {file_path}")
            else:
                logger.error(f"Failed to process: {file_path}")
                # Remove from processed set so it can be retried later if desired
                self.processed_files.discard(file_path)
                
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}", exc_info=True)
            # Remove from processed set for potential retry
            self.processed_files.discard(file_path)
    
    def _ensure_input_directory(self) -> bool:
        """
        Ensure the input directory exists and is accessible.
        
        Returns:
            bool: True if directory is ready, False otherwise
        """
        try:
            if not self.input_dir.exists():
                logger.error(f"Input directory does not exist: {self.input_dir}")
                return False
            
            if not self.input_dir.is_dir():
                logger.error(f"Input path is not a directory: {self.input_dir}")
                return False
            
            # Test read access
            list(self.input_dir.iterdir())
            
            logger.info(f"Input directory ready: {self.input_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error accessing input directory: {e}")
            return False
    
    def _shutdown(self):
        """
        Perform cleanup during shutdown.
        """
        logger.info("Shutting down transcription service...")
        
        # Log final statistics
        logger.info(f"Total files processed: {len(self.processed_files)}")
        
        # Log model status
        model_info = self.model_manager.get_memory_info()
        logger.info(f"Model status: {model_info}")
        
        logger.info("Service shutdown complete")
    
    def get_status(self) -> dict:
        """
        Get current service status for monitoring.
        
        Returns:
            dict: Service status information
        """
        return {
            "running": self.running,
            "watch_interval": self.watch_interval,
            "input_directory": str(self.input_dir),
            "processed_files_count": len(self.processed_files),
            "model_status": self.model_manager.get_memory_info()
        }
