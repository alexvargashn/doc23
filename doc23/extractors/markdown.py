"""
Markdown extraction module.
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

import markdown

from doc23.exceptions import ExtractionError
from doc23.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class MarkdownExtractor(BaseExtractor):
    """
    Extractor for Markdown files.
    """
    
    def extract_text(
        self, 
        file_obj: Union[str, Path, BytesIO, BinaryIO], 
        scan_or_image: Union[bool, str] = False
    ) -> str:
        """
        Extract text from a Markdown file.
        
        This extractor preserves the original markdown text rather than converting to HTML,
        as the structure is often important for subsequent parsing.
        
        Args:
            file_obj: The Markdown file object, which can be a path string,
                      Path object, or a file-like object.
            scan_or_image: Ignored for Markdown files.
                           
        Returns:
            The extracted text as a string.
            
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
            logger.error(f"Error extracting text from Markdown file: {e}")
            raise ExtractionError(f"Failed to extract text from Markdown: {e}") from e
    
    def convert_to_html(self, markdown_text: str) -> str:
        """
        Convert Markdown text to HTML.
        
        This is provided as a convenience method but is not used by default
        in the extract_text method.
        
        Args:
            markdown_text: The Markdown text to convert.
            
        Returns:
            HTML representation of the Markdown text.
        """
        try:
            return markdown.markdown(markdown_text)
        except Exception as e:
            logger.error(f"Error converting Markdown to HTML: {e}")
            raise ExtractionError(f"Failed to convert Markdown to HTML: {e}") from e
    
    def convert_to_plain_text(self, markdown_text: str) -> str:
        """
        Convert Markdown text to plain text.
        
        This strips out Markdown formatting and returns plain text.
        
        Args:
            markdown_text: The Markdown text to convert.
            
        Returns:
            Plain text representation of the Markdown text.
        """
        # Simple Markdown to text conversion
        # This is a basic implementation; a more comprehensive one would handle
        # all Markdown syntax elements
        text = markdown_text
        
        # Remove headers
        for i in range(6, 0, -1):
            heading_marker = '#' * i + ' '
            text = text.replace(heading_marker, '')
        
        # Remove emphasis markers
        for marker in ['**', '__', '*', '_', '~~', '`']:
            text = text.replace(marker, '')
        
        # Remove links, keeping the text
        import re
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        return text.strip() 