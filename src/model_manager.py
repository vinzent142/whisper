import logging
import os
from typing import Optional
from transcriber import WhisperTranscriber
from title_generator import GermanTitleGenerator

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Singleton class to manage model loading and persistence.
    Keeps models loaded in memory for faster processing of multiple files.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.whisper_transcriber = None
            self.title_generator = None
            self._whisper_loaded = False
            self._title_generator_loaded = False
            ModelManager._initialized = True
    
    def get_whisper_transcriber(self) -> Optional[WhisperTranscriber]:
        """
        Get the Whisper transcriber, loading it if necessary.
        
        Returns:
            WhisperTranscriber: Loaded transcriber instance, or None if loading failed
        """
        if not self._whisper_loaded:
            logger.info("Loading Whisper model (first time)")
            model_size = os.getenv("WHISPER_MODEL_SIZE", "large-v3")
            logger.info(f"Using Whisper model size: {model_size}")
            
            self.whisper_transcriber = WhisperTranscriber(model_size=model_size)
            
            if not self.whisper_transcriber.load_model():
                logger.error("Failed to load Whisper model")
                return None
            
            self._whisper_loaded = True
            logger.info("Whisper model loaded and cached")
        else:
            logger.debug("Using cached Whisper model")
        
        return self.whisper_transcriber
    
    def get_title_generator(self) -> Optional[GermanTitleGenerator]:
        """
        Get the title generator, loading it if necessary.
        
        Returns:
            GermanTitleGenerator: Loaded title generator instance, or None if loading failed
        """
        if not self._title_generator_loaded:
            logger.info("Loading German title generation model (first time)")
            
            self.title_generator = GermanTitleGenerator()
            
            if not self.title_generator.load_model():
                logger.error("Failed to load title generation model")
                return None
            
            self._title_generator_loaded = True
            logger.info("Title generation model loaded and cached")
        else:
            logger.debug("Using cached title generation model")
        
        return self.title_generator
    
    def is_ready(self) -> bool:
        """
        Check if both models are loaded and ready.
        
        Returns:
            bool: True if both models are loaded, False otherwise
        """
        return self._whisper_loaded and self._title_generator_loaded
    
    def preload_models(self) -> bool:
        """
        Preload both models to avoid delays during first file processing.
        
        Returns:
            bool: True if both models loaded successfully, False otherwise
        """
        logger.info("Preloading all models...")
        
        whisper_ok = self.get_whisper_transcriber() is not None
        title_ok = self.get_title_generator() is not None
        
        if whisper_ok and title_ok:
            logger.info("All models preloaded successfully")
            return True
        else:
            logger.error("Failed to preload models")
            return False
    
    def get_memory_info(self) -> dict:
        """
        Get information about loaded models for monitoring.
        
        Returns:
            dict: Model loading status information
        """
        return {
            "whisper_loaded": self._whisper_loaded,
            "title_generator_loaded": self._title_generator_loaded,
            "models_ready": self.is_ready()
        }
