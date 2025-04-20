"""
Image text extraction module using OCR.
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

from doc23.exceptions import ExtractionError, OCRError
from doc23.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class ImageExtractor(BaseExtractor):
    """
    Extractor for image files that uses OCR to extract text.
    """
    
    def __init__(self, ocr_language: str = 'eng'):
        """
        Initialize image extractor.
        
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
        Extract text from an image file using OCR.
        
        The scan_or_image parameter is ignored for image files since OCR is always used.
        
        Args:
            file_obj: The image file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: Ignored for image files.
                           
        Returns:
            Extracted text as a string.
            
        Raises:
            ExtractionError: If text extraction fails.
        """
        try:
            validated_file = self._validate_file_object(file_obj)
            
            # Import here to avoid circular imports
            from doc23.ocr.processor import OCRProcessor
            
            try:
                # Initialize OCR processor
                ocr = OCRProcessor(language=self.ocr_language)
                
                # Process image with OCR
                return ocr.process_image(validated_file)
                
            except OCRError as e:
                logger.error(f"OCR error processing image: {e}")
                raise ExtractionError(f"OCR failed on image: {e}") from e
                
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            logger.error(f"Error extracting text from image: {e}")
            raise ExtractionError(f"Failed to extract text from image: {e}") from e 