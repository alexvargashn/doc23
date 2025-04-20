"""
PDF text extraction module.
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Union

import pdfplumber
from pdf2image import convert_from_bytes

from doc23.exceptions import ExtractionError
from doc23.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class PDFExtractor(BaseExtractor):
    """
    Extractor for PDF files that handles text extraction and OCR when needed.
    """
    
    def __init__(self, ocr_language: str = 'eng'):
        """
        Initialize PDF extractor.
        
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
        Extract text from a PDF file.
        
        Args:
            file_obj: The PDF file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: How to handle potential scanned content:
                          - False: Only extract text (no OCR)
                          - True: Use OCR on all pages
                          - 'auto': Detect and use OCR only when needed
                           
        Returns:
            Extracted text as a string.
            
        Raises:
            ExtractionError: If text extraction fails.
        """
        try:
            validated_file = self._validate_file_object(file_obj)
            
            match scan_or_image:
                case False:
                    return self._extract_text_only(validated_file)
                case True:
                    return self._extract_with_ocr(validated_file)
                case "auto":
                    return self._extract_auto(validated_file)
                case _:
                    raise ExtractionError(
                        "scan_or_image must be a boolean or 'auto'"
                    )
                    
        except Exception as e:
            if not isinstance(e, ExtractionError):
                raise ExtractionError(f"Failed to extract text from PDF: {e}") from e
            raise
    
    def _extract_text_only(self, file_obj: Union[str, BytesIO]) -> str:
        """Extract text from PDF without using OCR."""
        try:
            with pdfplumber.open(file_obj) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ExtractionError(f"Failed to extract text from PDF: {e}") from e
    
    def _extract_with_ocr(self, file_obj: Union[str, BytesIO]) -> str:
        """Extract text from PDF using OCR on all pages."""
        try:
            # Import here to avoid circular imports
            from doc23.ocr.processor import OCRProcessor
            
            ocr = OCRProcessor(language=self.ocr_language)
            
            # Convert PDF to images
            if isinstance(file_obj, str):
                with open(file_obj, 'rb') as f:
                    pdf_bytes = BytesIO(f.read())
            else:
                file_obj.seek(0)
                pdf_bytes = file_obj
                
            images = convert_from_bytes(pdf_bytes.read())
            
            # Process each image with OCR
            text_parts = []
            for img in images:
                text_parts.append(ocr.process_image(img))
                
            return "\n\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF with OCR: {e}")
            raise ExtractionError(
                f"Failed to extract text from PDF with OCR: {e}"
            ) from e
    
    def _extract_auto(self, file_obj: Union[str, BytesIO]) -> str:
        """
        Automatically detect if OCR is needed and extract text accordingly.
        
        This will first try normal text extraction, and if no text is found,
        it will fall back to OCR.
        """
        # First check if the PDF contains extractable text
        with pdfplumber.open(file_obj) as pdf:
            has_text = any(page.extract_text() for page in pdf.pages)
            
            if has_text:
                return self._extract_text_only(file_obj)
            else:
                return self._extract_with_ocr(file_obj)
                
    def pdf_contains_text(self, file_obj: Union[str, BytesIO]) -> bool:
        """
        Check if a PDF file contains extractable text.
        
        Args:
            file_obj: The PDF file object.
            
        Returns:
            True if the PDF contains extractable text, False otherwise.
        """
        try:
            validated_file = self._validate_file_object(file_obj)
            with pdfplumber.open(validated_file) as pdf:
                return any(page.extract_text() for page in pdf.pages)
        except Exception as e:
            logger.warning(f"Error checking if PDF contains text: {e}")
            return False 