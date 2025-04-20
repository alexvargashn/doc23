"""
Core functionality of the doc23 library.

This module contains the main Doc23 class, which is the primary interface
for working with documents.
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Dict, Optional, Union, Any

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
    MarkdownExtractor
)
from doc23.gardener import Gardener


logger = logging.getLogger(__name__)


class Doc23:
    """
    Main class for extracting and structuring document content.
    
    This class provides methods to extract text from various document types
    and structure it according to a provided configuration.
    """
    
    ALLOWED_TYPES = AllowedTypes

    def __init__(
        self, 
        file: Union[str, Path, BytesIO, BinaryIO], 
        config: Config,
        ocr_language: str = 'eng'
    ):
        """
        Initialize Doc23 instance.
        
        Args:
            file: The document file to process, which can be a path string,
                  Path object, or a file-like object.
            config: Configuration defining how to structure the document content.
            ocr_language: Language to use for OCR, default is English ('eng').
            
        Raises:
            FileTypeError: If the file type is not supported.
            Doc23Error: If initialization fails.
        """
        self._file = file
        self._config = config
        self._ocr_language = ocr_language
        self._doc_type = None
        self._text = None
        
        # Initialize extractors
        self._extractors = {
            AllowedTypes.PDF: PDFExtractor(ocr_language=ocr_language),
            AllowedTypes.DOCX: DocxExtractor(ocr_language=ocr_language),
            AllowedTypes.TXT: TextExtractor(),
            AllowedTypes.RTF: RTFExtractor(ocr_language=ocr_language),
            AllowedTypes.ODT: ODTExtractor(ocr_language=ocr_language),
            AllowedTypes.MD: MarkdownExtractor(),
            AllowedTypes.PNG: ImageExtractor(ocr_language=ocr_language),
            AllowedTypes.JPEG: ImageExtractor(ocr_language=ocr_language),
            AllowedTypes.TIFF: ImageExtractor(ocr_language=ocr_language),
            AllowedTypes.BMP: ImageExtractor(ocr_language=ocr_language),
        }
    
    def extract_text(self, scan_or_image: Union[bool, str] = False) -> str:
        """
        Extract text from the document.
        
        Args:
            scan_or_image: How to handle potential scanned content:
                          - False: Only extract text (no OCR)
                          - True: Use OCR on all pages
                          - 'auto': Detect and use OCR only when needed
                           
        Returns:
            Extracted text as a string.
            
        Raises:
            FileTypeError: If the document type is not supported.
            ExtractionError: If text extraction fails.
        """
        if self._text is not None:
            return self._text
            
        try:
            doc_type = self.get_doc_type()
            extractor = self._extractors.get(doc_type)
            
            if not extractor:
                raise FileTypeError(f"Unsupported document type: {doc_type}")
                
            self._text = extractor.extract_text(self._file, scan_or_image)
            return self._text
            
        except Exception as e:
            if isinstance(e, (FileTypeError, ExtractionError)):
                raise
            logger.error(f"Error extracting text: {e}")
            raise ExtractionError(f"Failed to extract text: {e}") from e
    
    def prune(self, config: Optional[Config] = None, text: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse and structure the document content.
        
        Args:
            config: Configuration to use for parsing. If None, uses the
                   configuration provided at initialization.
            text: Text to parse. If None, extracts text from the document.
            
        Returns:
            Structured document content as a dictionary.
            
        Raises:
            ExtractionError: If text extraction fails.
        """
        config = config or self._config
        text = text or self.extract_text()
        
        gardener = Gardener(config)
        return gardener.prune(text)
    
    def get_doc_type(self) -> AllowedTypes:
        """
        Determine the document type.
        
        Returns:
            Document type as an AllowedTypes enum value.
            
        Raises:
            FileTypeError: If the document type is not supported.
        """
        if self._doc_type is not None:
            return self._doc_type
            
        try:
            # Get MIME type
            if isinstance(self._file, (str, Path)):
                mime_type = python_magic.from_file(str(self._file), mime=True)
            else:
                # Read the first 2048 bytes for MIME detection
                position = self._file.tell()
                content = self._file.read(2048)
                self._file.seek(position)  # Reset position
                mime_type = python_magic.from_buffer(content, mime=True)
            
            # Convert to AllowedTypes enum
            for doc_type in AllowedTypes:
                if doc_type.value == mime_type:
                    self._doc_type = doc_type
                    return doc_type
                    
            raise FileTypeError(f"Unsupported document type: {mime_type}")
            
        except Exception as e:
            if isinstance(e, FileTypeError):
                raise
            logger.error(f"Error determining document type: {e}")
            raise FileTypeError(f"Failed to determine document type: {e}") from e 