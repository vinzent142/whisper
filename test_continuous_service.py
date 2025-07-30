#!/usr/bin/env python3
"""
Test script for the continuous Whisper transcription service.
This script validates the new architecture components.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, 'src')

def test_model_manager():
    """Test the ModelManager singleton and model loading."""
    print("Testing ModelManager...")
    
    try:
        from model_manager import ModelManager
        
        # Test singleton behavior
        manager1 = ModelManager()
        manager2 = ModelManager()
        assert manager1 is manager2, "ModelManager should be a singleton"
        print("✓ Singleton pattern working")
        
        # Test model info
        info = manager1.get_memory_info()
        assert isinstance(info, dict), "get_memory_info should return dict"
        assert 'whisper_loaded' in info, "Should track whisper loading status"
        assert 'title_generator_loaded' in info, "Should track title generator loading status"
        print("✓ Model info tracking working")
        
        print("✓ ModelManager tests passed")
        return True
        
    except Exception as e:
        print(f"✗ ModelManager test failed: {e}")
        return False

def test_file_processor():
    """Test the FileProcessor class."""
    print("Testing FileProcessor...")
    
    try:
        from file_processor import FileProcessor
        
        # Test initialization
        processor = FileProcessor()
        assert processor.model_manager is not None, "Should have model manager"
        print("✓ FileProcessor initialization working")
        
        # Test output path generation
        output_wav, output_txt = processor._get_output_paths("/input/test.wav")
        assert output_wav == "/output/test.wav", f"Expected /output/test.wav, got {output_wav}"
        assert output_txt == "/output/test.txt", f"Expected /output/test.txt, got {output_txt}"
        print("✓ Output path generation working")
        
        print("✓ FileProcessor tests passed")
        return True
        
    except Exception as e:
        print(f"✗ FileProcessor test failed: {e}")
        return False

def test_service_manager():
    """Test the ServiceManager class."""
    print("Testing ServiceManager...")
    
    try:
        from service_manager import ServiceManager
        
        # Test initialization
        service = ServiceManager()
        assert service.file_processor is not None, "Should have file processor"
        assert service.model_manager is not None, "Should have model manager"
        assert service.running == True, "Should start in running state"
        print("✓ ServiceManager initialization working")
        
        # Test status
        status = service.get_status()
        assert isinstance(status, dict), "get_status should return dict"
        assert 'running' in status, "Should include running status"
        assert 'input_directory' in status, "Should include input directory"
        print("✓ ServiceManager status working")
        
        print("✓ ServiceManager tests passed")
        return True
        
    except Exception as e:
        print(f"✗ ServiceManager test failed: {e}")
        return False

def test_utils():
    """Test utility functions."""
    print("Testing utils...")
    
    try:
        from utils import validate_input_file, ensure_output_directory
        
        # Test with non-existent file
        result = validate_input_file("/nonexistent/file.wav")
        assert result == False, "Should return False for non-existent file"
        print("✓ File validation working")
        
        # Test output directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            test_output = os.path.join(temp_dir, "subdir", "test.txt")
            result = ensure_output_directory(test_output)
            assert result == True, "Should create output directory"
            assert os.path.exists(os.path.dirname(test_output)), "Directory should exist"
        print("✓ Output directory creation working")
        
        print("✓ Utils tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Utils test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    modules = [
        'main',
        'model_manager',
        'file_processor', 
        'service_manager',
        'transcriber',
        'title_generator',
        'utils'
    ]
    
    try:
        for module in modules:
            __import__(module)
            print(f"✓ {module} imported successfully")
        
        print("✓ All imports working")
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing Continuous Whisper Service Architecture")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_model_manager,
        test_file_processor,
        test_service_manager,
        test_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        if test():
            passed += 1
        else:
            print("Test failed, continuing...")
    
    print()
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The continuous service architecture is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
