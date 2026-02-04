"""Base parser class - abstract interface for all document parsers."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List
import os


class BaseParser(ABC):
    """
    Abstract base class for all document parsers.
    
    All parsers must implement the `parse()` method and define
    their supported file extensions and file type identifier.
    """
    
    SUPPORTED_EXTENSIONS: List[str] = []
    FILE_TYPE: str = ""
    
    def __init__(self, filepath: str):
        """
        Initialize parser with file path.
        
        Args:
            filepath: Path to the document file
        """
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.parsed_at = datetime.now().isoformat()
    
    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """
        Parse the document and return structured data.
        
        Returns:
            Dictionary containing parsed document data with at minimum:
            - filename: Original filename
            - file_type: Type identifier (pdf, word, excel, powerpoint)
            - parsed_at: ISO timestamp of when parsing occurred
            - Additional fields specific to document type
        """
        pass
    
    def get_base_output(self) -> Dict[str, Any]:
        """
        Return common output fields for all document types.
        
        Returns:
            Dictionary with filename, file_type, and parsed_at
        """
        return {
            "filename": self.filename,
            "file_type": self.FILE_TYPE,
            "parsed_at": self.parsed_at
        }
    
    @classmethod
    def can_handle(cls, filepath: str) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            filepath: Path to the file to check
            
        Returns:
            True if file extension matches supported extensions
        """
        ext = os.path.splitext(filepath)[1].lower()
        return ext in cls.SUPPORTED_EXTENSIONS
    
    def _safe_str(self, value: Any) -> str:
        """
        Safely convert a value to string.
        
        Args:
            value: Any value to convert
            
        Returns:
            String representation or empty string if None
        """
        if value is None:
            return ''
        return str(value)
