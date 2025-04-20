"""
RTF (Rich Text Format) extraction module.
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

from striprtf.striprtf import rtf_to_text

from doc23.exceptions import ExtractionError
from doc23.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class RTFExtractor(BaseExtractor):
    """
    Extractor for RTF (Rich Text Format) files.
    """
    
    def __init__(self, ocr_language: str = 'eng'):
        """
        Initialize RTF extractor.
        
        Args:
            ocr_language: The language to use for OCR if needed, default is English ('eng').
                          Not used for standard RTF extraction.
        """
        self.ocr_language = ocr_language
        
    def extract_text(
        self, 
        file_obj: Union[str, Path, BytesIO, BinaryIO], 
        scan_or_image: Union[bool, str] = False
    ) -> str:
        """
        Extract text from an RTF file.
        
        Args:
            file_obj: The RTF file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: Ignored for RTF files.
                           
        Returns:
            Extracted text as a string.
            
        Raises:
            ExtractionError: If text extraction fails.
        """
        try:
            validated_file = self._validate_file_object(file_obj)
            
            # Handle file paths
            if isinstance(validated_file, str):
                with open(validated_file, "r", encoding="utf-8", errors="ignore") as f:
                    rtf_content = f.read()
            # Handle file-like objects
            else:
                validated_file.seek(0)
                rtf_content = validated_file.read().decode("utf-8", errors="ignore")
            
            # Convert RTF to plain text
            text = rtf_to_text(rtf_content)
            return text.strip()
                
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            logger.error(f"Error extracting text from RTF: {e}")
            raise ExtractionError(f"Failed to extract text from RTF: {e}") from e 