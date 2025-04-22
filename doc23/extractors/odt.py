"""
ODT (OpenDocument Text) extraction module.
"""

import logging
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union, Optional

from odf.opendocument import load
from odf.text import P

from doc23.exceptions import ExtractionError
from doc23.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class ODTExtractor(BaseExtractor):
    """
    Extractor for ODT (OpenDocument Text) files.
    """
    
    def __init__(
        self, 
        file_obj: Union[str, Path, BytesIO, BinaryIO],
        scan_or_image: Union[bool, str] = False,
        ocr_language: str = 'eng'
    ):
        """
        Initialize ODT extractor.
        
        Args:
            file_obj: The ODT file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: How to handle potential images in the document (not fully implemented).
            ocr_language: The language to use for OCR if needed, default is English ('eng').
        """
        super().__init__(file_obj)
        self.scan_or_image = scan_or_image
        self.ocr_language = ocr_language
        
    def extract_text(
        self, 
        file_obj: Optional[Union[str, Path, BytesIO, BinaryIO]] = None,
        scan_or_image: Optional[Union[bool, str]] = None
    ) -> str:
        """
        Extract text from an ODT file.
        
        Args:
            file_obj: Optional file object to override the one provided at initialization.
            scan_or_image: Optional scan_or_image setting to override the one provided at initialization.
            
        Returns:
            Extracted text as a string.
            
        Raises:
            ExtractionError: If text extraction fails.
        """
        try:
            # Use instance values if parameters are not provided
            file_to_use = file_obj if file_obj is not None else self.file_obj
            scan_to_use = scan_or_image if scan_or_image is not None else self.scan_or_image
            
            # Handle file paths
            if isinstance(file_to_use, str):
                return self._extract_from_odt(file_to_use)
            
            # Handle file-like objects by saving to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.odt', delete=False) as temp_file:
                temp_path = temp_file.name
                file_to_use.seek(0)
                temp_file.write(file_to_use.read())
            
            try:
                return self._extract_from_odt(temp_path)
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            logger.error(f"Error extracting text from ODT: {e}")
            raise ExtractionError(f"Failed to extract text from ODT: {e}") from e
    
    def _extract_from_odt(self, file_path: str) -> str:
        """Extract text from an ODT file."""
        try:
            doc = load(file_path)
            paragraphs = doc.getElementsByType(P)
            
            # Extract text from each paragraph
            text_parts = []
            for paragraph in paragraphs:
                text_parts.append(paragraph.plainText())
            
            return "\n".join(text_parts).strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from ODT file: {e}")
            raise ExtractionError(f"Failed to extract text from ODT: {e}") from e 