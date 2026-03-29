"""Logging utilities for mental health monitoring system."""

import logging
from pathlib import Path


def get_llm_response_logger():
    """Get a dedicated logger for LLM responses.
    
    Returns:
        Logger configured to write LLM responses to llm_responses.log
    """
    logger = logging.getLogger('llm_responses')
    
    # Only add handler if not already configured
    if not logger.handlers:
        log_file = Path('llm_responses.log')
        
        # Create file handler
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
    
    return logger
