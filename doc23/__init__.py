"""
doc23 - A Python library for extracting text from documents and converting it into a structured JSON tree.

This library provides tools to extract text from various document formats and
structure it according to a hierarchical configuration.

Basic usage:
    >>> from doc23 import Doc23, Config, LevelConfig
    >>> config = Config(...)
    >>> doc = Doc23('document.pdf', config)
    >>> structured_content = doc.prune()
"""

import logging

from doc23.allowed_types import AllowedTypes
from doc23.config_tree import Config, LevelConfig
from doc23.core import Doc23
from doc23.exceptions import (
    Doc23Error, 
    FileTypeError, 
    ExtractionError, 
    ConfigurationError, 
    OCRError, 
    ParsingError
)
from doc23.gardener import Gardener
from doc23.logging import configure_logging, get_logger

__all__ = [
    # Core classes
    "Doc23",
    "Gardener",
    
    # Configuration
    "Config",
    "LevelConfig",
    "AllowedTypes",
    
    # Exceptions
    "Doc23Error",
    "FileTypeError",
    "ExtractionError",
    "ConfigurationError",
    "OCRError",
    "ParsingError",
    
    # Utilities
    "configure_logging",
]

__version__ = "0.2.0"

# Configure basic logging
configure_logging()
