"""
Logging configuration for the doc23 library.

This module provides functions to set up logging for the library.
"""

import logging
import sys
from typing import Optional


def configure_logging(
    level: int = logging.INFO, 
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configure logging for the doc23 library.
    
    Args:
        level: The logging level to use (default: logging.INFO)
        log_file: Path to a file to log to (default: None, logs to stderr only)
        log_format: Custom log format string (default: None, uses standard format)
    """
    logger = logging.getLogger('doc23')
    logger.setLevel(level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Default format
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: The name of the module, typically __name__
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(f'doc23.{name}') 