"""
Base class for document text extractors.
"""

from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Union

from doc23.exceptions import ExtractionError


class BaseExtractor(ABC):
    """
    Base extractor class that defines the interface for all text extractors.
    
    All extractor implementations should inherit from this class and
    implement the extract_text method.
    """
    
    def __init__(self, file_obj: Union[str, Path, BytesIO, BinaryIO]):
        """
        Initialize the base extractor with a file object.
        
        Args:
            file_obj: The document file object, which can be a path string,
                      Path object, or a file-like object.
        """
        self.file_obj = self._validate_file_object(file_obj)
    
    @abstractmethod
    def extract_text(
        self, 
        file_obj: Union[str, Path, BytesIO, BinaryIO], 
        scan_or_image: Union[bool, str] = False
    ) -> str:
        """
        Extract text from a document file.
        
        Args:
            file_obj: The document file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: Whether the document contains scanned pages or images.
                          If True, OCR will be used.
                          If 'auto', the method will try to detect if OCR is needed.
                          
        Returns:
            Extracted text as a string.
            
        Raises:
            ExtractionError: If text extraction fails.
        """
        pass
    
    def _validate_file_object(
        self, 
        file_obj: Union[str, Path, BytesIO, BinaryIO]
    ) -> Union[str, BytesIO]:
        """
        Validates the file object and returns a standardized form.
        
        Args:
            file_obj: The document file object.
            
        Returns:
            A standardized file object (either a path string or BytesIO).
            
        Raises:
            ExtractionError: If the file object is invalid.
        """
        if isinstance(file_obj, (str, Path)):
            path = Path(file_obj)
            if not path.exists():
                raise ExtractionError(f"File not found: {path}")
            return str(path.resolve())
        
        if isinstance(file_obj, (BytesIO, BinaryIO)):
            # Ensure we're at the start of the file
            try:
                file_obj.seek(0)
                return file_obj
            except Exception as e:
                raise ExtractionError(f"Invalid file object: {e}")
        
        raise ExtractionError(
            f"Unsupported file object type: {type(file_obj).__name__}"
        ) 