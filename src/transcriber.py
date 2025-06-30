import whisper
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """
    Handles audio transcription using OpenAI Whisper with German language optimization.
    """
    
    def __init__(self, model_size: str = "large-v3"):
        """
        Initialize the Whisper transcriber.
        
        Args:
            model_size: Whisper model size to use (base, small, medium, large, large-v3)
        """
        self.model_size = model_size
        self.model = None
        
    def load_model(self) -> bool:
        """
        Load the Whisper model.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            return False
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file to German text.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            str: Transcribed text, or None if transcription failed
        """
        if self.model is None:
            logger.error("Model not loaded. Call load_model() first.")
            return None
            
        try:
            logger.info(f"Starting transcription of: {audio_path}")
            
            # Transcribe with German language specification
            result = self.model.transcribe(
                audio_path,
                language="de",  # German language
                task="transcribe",
                verbose=False,
                temperature=0.0,  # More deterministic output
                best_of=1,
                beam_size=5,
                patience=1.0,
                length_penalty=1.0,
                suppress_tokens=[-1],  # Suppress special tokens
                initial_prompt="Dies ist eine deutsche Audioaufnahme eines Service Desk Anrufs."  # German context
            )
            
            transcribed_text = result["text"].strip()
            
            if not transcribed_text:
                logger.error("Transcription resulted in empty text")
                return None
                
            logger.info(f"Transcription completed successfully. Length: {len(transcribed_text)} characters")
            return self._clean_transcription(transcribed_text)
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None
    
    def _clean_transcription(self, text: str) -> str:
        """
        Clean and normalize the transcribed text.
        
        Args:
            text: Raw transcribed text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
