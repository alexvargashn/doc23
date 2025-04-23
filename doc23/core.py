"""
Core functionality of the doc23 library.

This module contains the main Doc23 class and utility functions for working with documents.
"""

import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
from io import BytesIO

import magic as python_magic

from doc23.allowed_types import AllowedTypes
from doc23.config_tree import Config
from doc23.exceptions import Doc23Error, FileTypeError, ExtractionError
from doc23.extractors import (
    PDFExtractor,
    DocxExtractor,
    TextExtractor,
    ImageExtractor,
    ODTExtractor,
    RTFExtractor,
    MarkdownExtractor,
)
from doc23.gardener import Gardener


logger = logging.getLogger(__name__)


def extract_text(file: Union[str, Path, bytes, BytesIO], scan_or_image: Union[bool, str] = False) -> str:
    """
    Extract raw text from a file.
    
    This function detects the file type and uses the appropriate extractor to
    extract the text content. For scanned documents or images, OCR can be used.
    
    Args:
        file: Path to the file or file-like object
        scan_or_image: Controls OCR behavior:
            - False (default): No OCR, extract text directly
            - True: Force OCR on all pages
            - 'auto': Automatically detect if OCR is needed
            
    Returns:
        str: The extracted text content
        
    Raises:
        ExtractionError: If text extraction fails for any reason
        FileTypeError: If the file type is not supported
    """
    doc = Doc23(file, Config("temp", "sections", "description", {}))
    return doc._extract_text(scan_or_image)


class Doc23:
    """
    Main class for extracting and structuring document content.

    Given a file path or buffer and a configuration, it automatically extracts
    the plain text and structures it according to the defined hierarchy.
    """

    def __init__(self, file: Union[str, Path, bytes, BytesIO], config: Config):
        """Initialize the Doc23 instance.
        
        Args:
            file: Path to the file or file-like object
            config: Configuration for document parsing
        """
        self.file = file
        self.config = config
        self.file_type = self._detect_type()
        self.gardener = Gardener(config)

    def extract_text(self, scan_or_image: Union[bool, str] = False) -> str:
        """
        Extract raw text from the file.
        
        This method detects the file type and uses the appropriate extractor to
        extract the text content. For scanned documents or images, OCR can be used.
        
        Args:
            scan_or_image: Controls OCR behavior:
                - False (default): No OCR, extract text directly
                - True: Force OCR on all pages
                - 'auto': Automatically detect if OCR is needed
                
        Returns:
            str: The extracted text content
            
        Raises:
            ExtractionError: If text extraction fails for any reason
            FileTypeError: If the file type is not supported
        """
        return self._extract_text(scan_or_image)

    def _extract_text(self, scan_or_image: Union[bool, str]) -> str:
        """Internal method for text extraction."""
        extractor = self._get_extractor(scan_or_image)
        try:
            return extractor.extract_text(scan_or_image=scan_or_image)
        except Exception as e:
            raise ExtractionError(f"Failed to extract text: {e}") from e

    def prune(self, text: Optional[str] = None) -> Dict[str, any]:
        """
        Generate a structured JSON-like dictionary from extracted or provided text.
        
        This method uses the configured hierarchy patterns to parse the text and
        structure it according to the defined levels.
        
        Args:
            text: The text to parse. If None, text will be automatically extracted
                 from the file using extract_text() with OCR if necessary.
                 
        Returns:
            Dict[str, Any]: A structured dictionary representing the document hierarchy
            
        Raises:
            ExtractionError: If text extraction fails when text=None
        """
        if text is None:
            text = self.extract_text(scan_or_image="auto")
        return self.gardener.prune(text)

    def _get_extractor(self, scan_or_image: Union[bool, str]) -> Any:
        """Get the appropriate extractor for the file type."""
        if self.file_type == "pdf":
            return PDFExtractor(self.file, scan_or_image=scan_or_image)
        elif self.file_type == "docx":
            return DocxExtractor(self.file, scan_or_image=scan_or_image)
        elif self.file_type == "odt":
            return ODTExtractor(self.file, scan_or_image=scan_or_image)
        elif self.file_type == "rtf":
            return RTFExtractor(self.file, scan_or_image=scan_or_image)
        elif self.file_type == "txt":
            return TextExtractor(self.file, scan_or_image=scan_or_image)
        elif self.file_type == "md":
            return MarkdownExtractor(self.file, scan_or_image=scan_or_image)
        elif self.file_type in ["jpg", "jpeg", "png", "tiff", "bmp"]:
            return ImageExtractor(self.file, scan_or_image=scan_or_image)
        else:
            raise FileTypeError(f"Unsupported file type: {self.file_type}")

    def _detect_type(self) -> str:
        """Detect the file type based on the file extension or MIME type."""
        if isinstance(self.file, (str, Path)):
            file_path = Path(self.file)
            extension = file_path.suffix.lower().lstrip('.')
            if extension in ['pdf', 'docx', 'odt', 'rtf', 'txt', 'md', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']:
                return extension
            # If extension not recognized, try MIME type detection
            try:
                import magic
                mime = magic.Magic(mime=True)
                mime_type = mime.from_file(str(file_path))
                return self._mime_to_extension(mime_type)
            except ImportError:
                raise FileTypeError("python-magic package is required for MIME type detection")
        elif isinstance(self.file, (bytes, BytesIO)):
            try:
                import magic
                mime = magic.Magic(mime=True)
                if isinstance(self.file, bytes):
                    mime_type = mime.from_buffer(self.file)
                else:
                    mime_type = mime.from_buffer(self.file.read(2048))
                    self.file.seek(0)  # Reset file pointer
                return self._mime_to_extension(mime_type)
            except ImportError:
                raise FileTypeError("python-magic package is required for MIME type detection")
        else:
            raise FileTypeError("Unsupported file input type")

    def _mime_to_extension(self, mime_type: str) -> str:
        """Convert MIME type to file extension."""
        mime_map = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.oasis.opendocument.text': 'odt',
            'text/rtf': 'rtf',
            'text/plain': 'txt',
            'text/markdown': 'md',
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/tiff': 'tiff',
            'image/bmp': 'bmp'
        }
        if mime_type in mime_map:
            return mime_map[mime_type]
        raise FileTypeError(f"Unsupported MIME type: {mime_type}")
