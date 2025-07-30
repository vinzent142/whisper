import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
from model_manager import ModelManager
from utils import validate_input_file, ensure_output_directory

logger = logging.getLogger(__name__)

class FileProcessor:
    """
    Handles processing of individual audio files using persistent models.
    """
    
    def __init__(self):
        self.model_manager = ModelManager()
    
    def process_file(self, input_file_path: str) -> bool:
        """
        Process a single audio file: transcribe, generate title, and move files.
        
        Args:
            input_file_path: Path to the input WAV file
            
        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        logger.info(f"Starting processing of: {input_file_path}")
        
        try:
            # Step 1: Validate input file
            if not validate_input_file(input_file_path):
                logger.error(f"Input file validation failed: {input_file_path}")
                return False
            
            # Step 2: Generate output paths
            output_wav_path, output_txt_path = self._get_output_paths(input_file_path)
            
            # Step 3: Ensure output directory exists
            if not ensure_output_directory(output_txt_path):
                logger.error("Output directory preparation failed")
                return False
            
            # Step 4: Get models (load if necessary)
            transcriber = self.model_manager.get_whisper_transcriber()
            if not transcriber:
                logger.error("Failed to get Whisper transcriber")
                return False
            
            title_generator = self.model_manager.get_title_generator()
            if not title_generator:
                logger.error("Failed to get title generator")
                return False
            
            # Step 5: Transcribe audio
            logger.info("Starting audio transcription")
            transcription = transcriber.transcribe_audio(input_file_path)
            
            if not transcription:
                logger.error("Audio transcription failed")
                return False
            
            logger.info(f"Transcription completed: {len(transcription)} characters")
            
            # Step 6: Generate title
            logger.info("Generating title from transcription")
            title = title_generator.generate_title(transcription, max_length=50)
            
            if not title:
                logger.error("Title generation failed")
                return False
            
            logger.info(f"Title generated: {title}")
            
            # Step 7: Write transcription output
            if not self._write_transcription_output(output_txt_path, title, transcription):
                logger.error("Failed to write transcription output")
                return False
            
            # Step 8: Move original audio file to output
            if not self._move_audio_file(input_file_path, output_wav_path):
                logger.error("Failed to move audio file to output")
                return False
            
            logger.info("File processing completed successfully")
            logger.info(f"Audio file moved to: {output_wav_path}")
            logger.info(f"Transcription written to: {output_txt_path}")
            
            # Log processing summary
            self._log_processing_summary(input_file_path, output_wav_path, output_txt_path, title, transcription)
            
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error processing file {input_file_path}: {e}", exc_info=True)
            return False
    
    def _get_output_paths(self, input_file_path: str) -> Tuple[str, str]:
        """
        Generate output file paths based on input file name.
        
        Args:
            input_file_path: Path to input WAV file
            
        Returns:
            Tuple[str, str]: (output_wav_path, output_txt_path)
        """
        input_path = Path(input_file_path)
        filename_without_ext = input_path.stem
        
        output_wav_path = f"/output/{filename_without_ext}.wav"
        output_txt_path = f"/output/{filename_without_ext}.txt"
        
        return output_wav_path, output_txt_path
    
    def _write_transcription_output(self, output_path: str, title: str, transcription: str) -> bool:
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
    
    def _move_audio_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move the audio file from input to output directory.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure destination directory exists
            dest_dir = Path(destination_path).parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(source_path, destination_path)
            logger.info(f"Audio file moved: {source_path} -> {destination_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving audio file: {e}")
            return False
    
    def _log_processing_summary(self, input_path: str, output_wav_path: str, output_txt_path: str, title: str, transcription: str):
        """
        Log a summary of the processing results.
        """
        logger.info("=== FILE PROCESSING SUMMARY ===")
        logger.info(f"Input file: {input_path}")
        logger.info(f"Output audio: {output_wav_path}")
        logger.info(f"Output transcription: {output_txt_path}")
        logger.info(f"Title: {title}")
        logger.info(f"Transcription length: {len(transcription)} characters")
        logger.info("===============================")
