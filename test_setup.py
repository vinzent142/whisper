#!/usr/bin/env python3
"""
Test script to verify the Whisper transcription setup.
This script tests the individual components without requiring a full Docker build.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

from utils import validate_input_file, ensure_output_directory, write_transcription_output
from transcriber import WhisperTranscriber
from title_generator import GermanTitleGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dependencies():
    """Test if all required dependencies are available."""
    logger.info("Testing dependencies...")
    
    try:
        import torch
        logger.info(f"✓ PyTorch version: {torch.__version__}")
        
        import whisper
        logger.info("✓ OpenAI Whisper available")
        
        import transformers
        logger.info(f"✓ Transformers version: {transformers.__version__}")
        
        import soundfile
        logger.info("✓ SoundFile available")
        
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        return False

def test_whisper_model():
    """Test Whisper model loading with a small model."""
    logger.info("Testing Whisper model loading...")
    
    try:
        # Use base model for testing (smaller download)
        transcriber = WhisperTranscriber(model_size="base")
        if transcriber.load_model():
            logger.info("✓ Whisper model loaded successfully")
            return True
        else:
            logger.error("✗ Failed to load Whisper model")
            return False
    except Exception as e:
        logger.error(f"✗ Whisper model test failed: {e}")
        return False

def test_title_generator():
    """Test German title generation model loading."""
    logger.info("Testing German title generator...")
    
    try:
        title_generator = GermanTitleGenerator("aiautomationlab/german-news-title-gen-mt5")
        if title_generator.load_model():
            logger.info("✓ German title generator loaded successfully")
            
            # Test title generation with sample text
            sample_text = "Guten Tag, ich habe ein Problem mit meinem Computer. Der Bildschirm zeigt nichts an."
            title = title_generator.generate_title(sample_text, max_length=50)
            
            if title:
                logger.info(f"✓ Sample title generated: {title}")
                return True
            else:
                logger.error("✗ Title generation returned empty result")
                return False
        else:
            logger.error("✗ Failed to load German title generator")
            return False
    except Exception as e:
        logger.error(f"✗ Title generator test failed: {e}")
        return False

def test_file_operations():
    """Test file operations."""
    logger.info("Testing file operations...")
    
    try:
        # Test output directory creation
        test_output = "test_output/transcription.txt"
        if ensure_output_directory(test_output):
            logger.info("✓ Output directory creation works")
        else:
            logger.error("✗ Output directory creation failed")
            return False
        
        # Test file writing
        test_title = "Test Service Desk Anfrage"
        test_transcription = "Dies ist ein Test der Transkription."
        
        if write_transcription_output(test_output, test_title, test_transcription):
            logger.info("✓ File writing works")
            
            # Verify content
            with open(test_output, 'r', encoding='utf-8') as f:
                content = f.read()
                if test_title in content and test_transcription in content:
                    logger.info("✓ File content verification passed")
                else:
                    logger.error("✗ File content verification failed")
                    return False
        else:
            logger.error("✗ File writing failed")
            return False
        
        # Cleanup
        os.remove(test_output)
        os.rmdir("test_output")
        
        return True
    except Exception as e:
        logger.error(f"✗ File operations test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting Whisper transcription setup tests...")
    logger.info("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("File Operations", test_file_operations),
        ("Whisper Model", test_whisper_model),
        ("Title Generator", test_title_generator),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Your setup is ready.")
        logger.info("\nNext steps:")
        logger.info("1. Build the Docker image: docker build -t whisper-transcriber .")
        logger.info("2. Place a WAV file in the input/ directory")
        logger.info("3. Run: docker run --rm -v $(pwd)/input:/input:ro -v $(pwd)/output:/output whisper-transcriber")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        logger.info("\nTo install missing dependencies:")
        logger.info("pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
