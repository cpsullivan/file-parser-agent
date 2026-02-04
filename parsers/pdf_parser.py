"""PDF document parser using PyPDF2."""

from typing import Dict, Any, List
from PyPDF2 import PdfReader
from .base_parser import BaseParser


class PDFParser(BaseParser):
    """
    Parser for PDF documents.
    
    Extracts:
    - Text content page-by-page
    - Document metadata (title, author, subject, creator)
    - Page count and character counts
    """
    
    SUPPORTED_EXTENSIONS = ['.pdf']
    FILE_TYPE = 'pdf'
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse PDF file and extract content.
        
        Returns:
            Dictionary containing:
            - filename, file_type, parsed_at (base fields)
            - total_pages: Number of pages
            - metadata: Document metadata dict
            - pages: List of page objects with text and char_count
        """
        output = self.get_base_output()
        
        try:
            reader = PdfReader(self.filepath)
            
            # Extract metadata
            output['metadata'] = self._extract_metadata(reader)
            
            # Extract pages
            pages = self._extract_pages(reader)
            output['total_pages'] = len(pages)
            output['pages'] = pages
            
        except Exception as e:
            output['error'] = f"PDF parsing error: {str(e)}"
            output['total_pages'] = 0
            output['pages'] = []
            output['metadata'] = {}
        
        return output
    
    def _extract_metadata(self, reader: PdfReader) -> Dict[str, str]:
        """
        Extract document metadata from PDF.
        
        Args:
            reader: PyPDF2 PdfReader instance
            
        Returns:
            Dictionary with title, author, subject, creator
        """
        meta = reader.metadata or {}
        
        return {
            'title': self._safe_str(meta.get('/Title', '')),
            'author': self._safe_str(meta.get('/Author', '')),
            'subject': self._safe_str(meta.get('/Subject', '')),
            'creator': self._safe_str(meta.get('/Creator', ''))
        }
    
    def _extract_pages(self, reader: PdfReader) -> List[Dict[str, Any]]:
        """
        Extract text content from all pages.
        
        Args:
            reader: PyPDF2 PdfReader instance
            
        Returns:
            List of page dictionaries with page_number, text, char_count
        """
        pages = []
        
        for i, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text() or ''
            except Exception:
                text = '[Error extracting text from this page]'
            
            pages.append({
                'page_number': i,
                'text': text,
                'char_count': len(text)
            })
        
        return pages
