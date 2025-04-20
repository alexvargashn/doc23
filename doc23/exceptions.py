"""
Custom exceptions for the doc23 library.
"""

class Doc23Error(Exception):
    """Base exception for all doc23 errors."""
    pass

class FileTypeError(Doc23Error):
    """Raised when an unsupported file type is provided."""
    pass
    
class ExtractionError(Doc23Error):
    """Raised when text extraction fails."""
    pass
    
class ConfigurationError(Doc23Error):
    """Raised when there's an issue with configuration."""
    pass

class OCRError(Doc23Error):
    """Raised when OCR processing fails."""
    pass

class ParsingError(Doc23Error):
    """Raised when document parsing fails."""
    pass 