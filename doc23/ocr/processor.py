"""
OCR processor for handling image-to-text conversion.
"""

import logging
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Union

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from doc23.exceptions import OCRError


logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Handles OCR (Optical Character Recognition) operations using Tesseract.
    """
    
    def __init__(self, language: str = 'eng', config: Optional[str] = None):
        """
        Initialize OCR processor.
        
        Args:
            language: OCR language code (default: 'eng' for English)
            config: Additional Tesseract configuration parameters
        
        Raises:
            OCRError: If Tesseract is not available
        """
        if not TESSERACT_AVAILABLE:
            raise OCRError(
                "Tesseract not available. Install with: pip install pytesseract"
            )
        
        self.language = language
        self.config = config
        
        # Check if tesseract is installed
        if not self._is_tesseract_available():
            raise OCRError(
                "Tesseract is not installed or not in PATH. "
                "Please install Tesseract OCR on your system."
            )
    
    def _is_tesseract_available(self) -> bool:
        """Check if Tesseract is available on the system."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    def process_image(
        self, 
        image: Union[str, Path, BytesIO, BinaryIO, Image.Image]
    ) -> str:
        """
        Process an image and extract text using OCR.
        
        Args:
            image: Image to process. Can be a path string, Path object,
                  file-like object, or PIL Image.
                  
        Returns:
            Extracted text as a string.
            
        Raises:
            OCRError: If OCR processing fails.
        """
        try:
            # Convert to PIL Image if not already
            if isinstance(image, Image.Image):
                img = image
            elif isinstance(image, (str, Path)):
                img = Image.open(image)
            elif isinstance(image, (BytesIO, BinaryIO)):
                img = Image.open(image)
            else:
                raise OCRError(f"Unsupported image type: {type(image).__name__}")
            
            # Process with tesseract
            text = pytesseract.image_to_string(
                img, 
                lang=self.language,
                config=self.config
            )
            
            return text.strip()
            
        except Exception as e:
            if isinstance(e, OCRError):
                raise
            logger.error(f"OCR processing error: {e}")
            raise OCRError(f"Failed to process image with OCR: {e}") from e
    
    def process_images(self, images: list) -> str:
        """
        Process multiple images and combine the extracted text.
        
        Args:
            images: List of images to process.
            
        Returns:
            Combined extracted text as a string.
        """
        results = []
        for img in images:
            results.append(self.process_image(img))
        
        return "\n\n".join(results)
    
    def process_pdf_page(
        self, 
        pdf_path: Union[str, Path], 
        page_num: int
    ) -> str:
        """
        Extract text from a specific PDF page using OCR.
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number to process (0-based)
            
        Returns:
            Extracted text from the page
        """
        try:
            from pdf2image import convert_from_path
            
            # Convert specific page to image
            images = convert_from_path(
                pdf_path, 
                first_page=page_num+1, 
                last_page=page_num+1
            )
            
            if not images:
                raise OCRError(f"Failed to convert PDF page {page_num} to image")
                
            # Process the image
            return self.process_image(images[0])
            
        except Exception as e:
            if isinstance(e, OCRError):
                raise
            logger.error(f"Error processing PDF page with OCR: {e}")
            raise OCRError(f"Failed to process PDF page with OCR: {e}") from e 