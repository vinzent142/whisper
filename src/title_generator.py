import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional
import re

logger = logging.getLogger(__name__)

class GermanTitleGenerator:
    """
    Generates German titles from transcribed text using aiautomationlab/german-news-title-gen-mt5.
    """
    
    def __init__(self, model_name: str = "aiautomationlab/german-news-title-gen-mt5"):
        """
        Initialize the German title generator.
        
        Args:
            model_name: HuggingFace model name for German title generation
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        
    def load_model(self) -> bool:
        """
        Load the title generation model and tokenizer.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading German title generation model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            logger.info("German title generation model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading title generation model: {e}")
            return False
    
    def generate_title(self, text: str, max_length: int = 50) -> Optional[str]:
        """
        Generate a German title from the transcribed text.
        
        Args:
            text: Transcribed German text
            max_length: Maximum title length (default 50 characters)
            
        Returns:
            str: Generated title, or None if generation failed
        """
        if self.model is None or self.tokenizer is None:
            logger.error("Model not loaded. Call load_model() first.")
            return None
            
        try:
            logger.info("Generating German title from transcription")
            
            # Prepare text for title generation
            prepared_text = self._prepare_text_for_title_generation(text)
            
            # Tokenize input
            inputs = self.tokenizer(
                prepared_text,
                max_length=512,
                truncation=True,
                padding=True,
                return_tensors="pt"
            )
            
            # Generate title
            with self.tokenizer.as_target_tokenizer():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=20,  # Token limit for title generation
                    min_length=3,
                    num_beams=4,
                    length_penalty=1.0,
                    early_stopping=True,
                    do_sample=False,
                    temperature=1.0,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode generated title
            generated_title = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean and validate title
            title = self._clean_and_validate_title(generated_title, max_length)
            
            if title:
                logger.info(f"Generated title: {title}")
                return title
            else:
                logger.warning("Title generation produced empty result, using fallback")
                return self._generate_fallback_title(text, max_length)
                
        except Exception as e:
            logger.error(f"Error during title generation: {e}")
            return self._generate_fallback_title(text, max_length)
    
    def _prepare_text_for_title_generation(self, text: str) -> str:
        """
        Prepare transcribed text for title generation.
        
        Args:
            text: Raw transcribed text
            
        Returns:
            str: Prepared text for title generation
        """
        # Take first part of transcription (most relevant for title)
        # Limit to first 300 characters to focus on main topic
        if len(text) > 300:
            text = text[:300]
            # Try to end at a sentence boundary
            last_period = text.rfind('.')
            if last_period > 100:  # Ensure we have enough content
                text = text[:last_period + 1]
        
        return text.strip()
    
    def _clean_and_validate_title(self, title: str, max_length: int) -> Optional[str]:
        """
        Clean and validate the generated title.
        
        Args:
            title: Raw generated title
            max_length: Maximum allowed length
            
        Returns:
            str: Cleaned title, or None if invalid
        """
        if not title:
            return None
            
        # Remove extra whitespace
        title = " ".join(title.split())
        
        # Remove common prefixes that might be generated
        prefixes_to_remove = [
            "Titel:", "Title:", "Betreff:", "Subject:",
            "Zusammenfassung:", "Summary:"
        ]
        
        for prefix in prefixes_to_remove:
            if title.lower().startswith(prefix.lower()):
                title = title[len(prefix):].strip()
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        # Ensure title doesn't end with punctuation (except question marks)
        if title.endswith(('.', '!', ':')):
            title = title[:-1]
        
        # Truncate if too long
        if len(title) > max_length:
            title = title[:max_length - 3] + "..."
        
        # Validate minimum length
        if len(title.strip()) < 5:
            return None
            
        return title
    
    def _generate_fallback_title(self, text: str, max_length: int) -> str:
        """
        Generate a simple fallback title when model generation fails.
        
        Args:
            text: Original transcribed text
            max_length: Maximum title length
            
        Returns:
            str: Fallback title
        """
        # Extract key words from the beginning of the text
        words = text.split()[:10]  # First 10 words
        
        # Common German service desk terms to prioritize
        service_terms = [
            "problem", "fehler", "störung", "hilfe", "support",
            "ticket", "anfrage", "issue", "bug", "defekt"
        ]
        
        # Look for service-related terms
        key_words = []
        for word in words:
            word_clean = re.sub(r'[^\w\s]', '', word.lower())
            if word_clean in service_terms or len(word_clean) > 4:
                key_words.append(word)
                if len(key_words) >= 5:
                    break
        
        if key_words:
            fallback_title = " ".join(key_words)
        else:
            fallback_title = "Service Desk Anfrage"
        
        # Ensure it fits within max_length
        if len(fallback_title) > max_length:
            fallback_title = fallback_title[:max_length - 3] + "..."
            
        logger.info(f"Using fallback title: {fallback_title}")
        return fallback_title
