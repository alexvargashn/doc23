"""
DOCX text extraction module.
"""

import logging
from io import BytesIO
import os
import tempfile
from pathlib import Path
from typing import BinaryIO, Optional, Union

import docx2txt

from doc23.exceptions import ExtractionError
from doc23.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class DocxExtractor(BaseExtractor):
    """
    Extractor for DOCX files that handles text extraction and OCR when needed.
    """
    
    def __init__(self, ocr_language: str = 'eng'):
        """
        Initialize DOCX extractor.
        
        Args:
            ocr_language: The language to use for OCR, default is English ('eng').
        """
        self.ocr_language = ocr_language
        
    def extract_text(
        self, 
        file_obj: Union[str, Path, BytesIO, BinaryIO], 
        scan_or_image: Union[bool, str] = False
    ) -> str:
        """
        Extract text from a DOCX file.
        
        Args:
            file_obj: The DOCX file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: How to handle potential images in the document:
                          - False: Only extract text (no OCR)
                          - True: Extract text and use OCR on images
                          - 'auto': Extract text and detect if OCR is needed for images
                           
        Returns:
            Extracted text as a string.
            
        Raises:
            ExtractionError: If text extraction fails.
        """
        try:
            validated_file = self._validate_file_object(file_obj)
            
            # For now, ignore the scan_or_image parameter for DOCX
            # Future enhancement: Extract images from DOCX and apply OCR if requested
            
            if isinstance(validated_file, str):
                # Direct path to file
                return docx2txt.process(validated_file).strip()
            else:
                # File-like object, save to temp file first
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                    temp_path = temp_file.name
                    validated_file.seek(0)
                    temp_file.write(validated_file.read())
                
                try:
                    result = docx2txt.process(temp_path).strip()
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                
                return result
                
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            logger.error(f"Error extracting text from DOCX: {e}")
            raise ExtractionError(f"Failed to extract text from DOCX: {e}") from e 