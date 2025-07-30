#!/usr/bin/env python3
"""
Whisper Transcription Service
Continuous service that transcribes German audio files and generates titles for Service Desk tickets.
"""

import sys
import logging
import os
from service_manager import ServiceManager

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Exit codes
EXIT_SUCCESS = 0
EXIT_SERVICE_ERROR = 1

def main():
    """
    Main entry point for the continuous transcription service.
    """
    logger.info("Starting Whisper transcription service in continuous mode")
    
    try:
        # Create and start the service manager
        service = ServiceManager()
        service.start()
        
        logger.info("Service stopped normally")
        sys.exit(EXIT_SUCCESS)
        
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(EXIT_SUCCESS)
        
    except Exception as e:
        logger.error(f"Unexpected error in service: {e}", exc_info=True)
        sys.exit(EXIT_SERVICE_ERROR)

if __name__ == "__main__":
    main()
