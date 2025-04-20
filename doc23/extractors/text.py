"""
Plain text extraction module.
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

from doc23.exceptions import ExtractionError
from doc23.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class TextExtractor(BaseExtractor):
    """
    Extractor for plain text files.
    """
    
    def extract_text(
        self, 
        file_obj: Union[str, Path, BytesIO, BinaryIO], 
        scan_or_image: Union[bool, str] = False
    ) -> str:
        """
        Extract text from a plain text file.
        
        The scan_or_image parameter is ignored for text files since they are
        already in text format.
        
        Args:
            file_obj: The text file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: Ignored for text files.
                           
        Returns:
            Extracted text as a string.
            
        Raises:
            ExtractionError: If text extraction fails.
        """
        try:
            validated_file = self._validate_file_object(file_obj)
            
            # Handle file paths
            if isinstance(validated_file, str):
                with open(validated_file, "r", encoding="utf-8", errors="replace") as f:
                    return f.read().strip()
            
            # Handle file-like objects
            validated_file.seek(0)
            try:
                # Try first with utf-8
                return validated_file.read().decode("utf-8", errors="replace").strip()
            except UnicodeDecodeError:
                # Fallback to latin-1 if utf-8 fails
                validated_file.seek(0)
                return validated_file.read().decode("latin-1", errors="replace").strip()
                
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            logger.error(f"Error extracting text from plain text file: {e}")
            raise ExtractionError(f"Failed to extract text: {e}") from e 