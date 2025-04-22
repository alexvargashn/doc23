"""
RTF (Rich Text Format) extraction module.
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union, Optional

from striprtf.striprtf import rtf_to_text

from doc23.exceptions import ExtractionError
from doc23.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class RTFExtractor(BaseExtractor):
    """
    Extractor for RTF (Rich Text Format) files.
    """
    
    def __init__(
        self, 
        file_obj: Union[str, Path, BytesIO, BinaryIO],
        scan_or_image: Union[bool, str] = False,
        ocr_language: str = 'eng'
    ):
        """
        Initialize RTF extractor.
        
        Args:
            file_obj: The RTF file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: Ignored for RTF files.
            ocr_language: The language to use for OCR if needed, default is English ('eng').
                          Not used for standard RTF extraction.
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
        Extract text from an RTF file.
        
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
                with open(file_to_use, "r", encoding="utf-8", errors="ignore") as f:
                    rtf_content = f.read()
            # Handle file-like objects
            else:
                file_to_use.seek(0)
                rtf_content = file_to_use.read().decode("utf-8", errors="ignore")
            
            # Convert RTF to plain text
            text = rtf_to_text(rtf_content)
            return text.strip()
                
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            logger.error(f"Error extracting text from RTF: {e}")
            raise ExtractionError(f"Failed to extract text from RTF: {e}") from e 