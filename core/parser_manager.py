"""Parser Manager - routes files to appropriate parsers and validates input."""

import os
from typing import Dict, Any, Optional, Type, List

# Import parsers
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.pdf_parser import PDFParser
from parsers.word_parser import WordParser
from parsers.excel_parser import ExcelParser
from parsers.pptx_parser import PowerPointParser
from parsers.base_parser import BaseParser


class ParserManager:
    """
    Routes files to appropriate parsers and manages the parsing workflow.
    
    This is the main entry point for document parsing. It:
    - Validates file existence, size, and type
    - Selects the appropriate parser based on file extension
    - Returns structured parsing results
    """
    
    # Available parsers in priority order
    PARSERS: List[Type[BaseParser]] = [
        PDFParser,
        WordParser,
        ExcelParser,
        PowerPointParser
    ]
    
    # Extension to file type mapping
    ALLOWED_EXTENSIONS: Dict[str, str] = {
        '.pdf': 'pdf',
        '.docx': 'word',
        '.doc': 'word',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.pptx': 'powerpoint',
        '.ppt': 'powerpoint'
    }
    
    # Maximum file size: 50MB
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    
    @classmethod
    def validate_file(cls, filepath: str) -> tuple:
        """
        Validate that file exists, is within size limits, and is a supported type.
        
        Args:
            filepath: Path to the file to validate
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        # Check existence
        if not os.path.exists(filepath):
            return False, "File not found"
        
        if not os.path.isfile(filepath):
            return False, "Path is not a file"
        
        # Check size
        file_size = os.path.getsize(filepath)
        if file_size > cls.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"File exceeds 50MB limit ({size_mb:.1f}MB)"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check extension
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            supported = ', '.join(sorted(cls.ALLOWED_EXTENSIONS.keys()))
            return False, f"Unsupported file type: {ext}. Supported: {supported}"
        
        return True, "Valid"
    
    @classmethod
    def get_file_type(cls, filepath: str) -> Optional[str]:
        """
        Get the file type based on extension.
        
        Args:
            filepath: Path to the file
            
        Returns:
            File type string or None if unsupported
        """
        ext = os.path.splitext(filepath)[1].lower()
        return cls.ALLOWED_EXTENSIONS.get(ext)
    
    @classmethod
    def get_parser(cls, filepath: str, **kwargs) -> Optional[BaseParser]:
        """
        Get the appropriate parser instance for a file.
        
        Args:
            filepath: Path to the file
            **kwargs: Additional arguments to pass to parser constructor
            
        Returns:
            Parser instance or None if no parser available
        """
        for parser_class in cls.PARSERS:
            if parser_class.can_handle(filepath):
                return parser_class(filepath, **kwargs)
        return None
    
    @classmethod
    def parse(cls, filepath: str, enable_ai_vision: bool = False) -> Dict[str, Any]:
        """
        Parse a file and return structured data.
        
        This is the main entry point for parsing. It validates the file,
        selects the appropriate parser, and returns the parsed content.
        
        Args:
            filepath: Path to the file to parse
            enable_ai_vision: Enable AI image analysis for PowerPoint files
            
        Returns:
            Dictionary containing parsed document data, or error information
        """
        # Validate file
        is_valid, message = cls.validate_file(filepath)
        if not is_valid:
            return {
                'error': message,
                'filename': os.path.basename(filepath) if filepath else 'unknown'
            }
        
        # Prepare parser kwargs
        kwargs = {}
        file_type = cls.get_file_type(filepath)
        
        # PowerPoint-specific options
        if file_type == 'powerpoint':
            kwargs['enable_ai_vision'] = enable_ai_vision
        
        # Get parser
        parser = cls.get_parser(filepath, **kwargs)
        if not parser:
            return {
                'error': 'No parser available for this file type',
                'filename': os.path.basename(filepath)
            }
        
        # Parse and return result
        return parser.parse()
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get list of all supported file extensions.
        
        Returns:
            List of extension strings (e.g., ['.pdf', '.docx', ...])
        """
        return sorted(cls.ALLOWED_EXTENSIONS.keys())
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """
        Get list of all supported file type names.
        
        Returns:
            List of type names (e.g., ['pdf', 'word', 'excel', 'powerpoint'])
        """
        return sorted(set(cls.ALLOWED_EXTENSIONS.values()))
