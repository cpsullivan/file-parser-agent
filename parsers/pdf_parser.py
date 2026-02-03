"""PDF Parser - Extract text and metadata from PDF files"""

import PyPDF2
from datetime import datetime
from pathlib import Path

def parse_pdf(filepath):
    """
    Parse PDF file and extract text content

    Args:
        filepath: Path to PDF file

    Returns:
        dict: Parsed PDF data
    """
    result = {
        'filename': Path(filepath).name,
        'file_type': 'pdf',
        'parsed_at': datetime.now().isoformat(),
        'pages': [],
        'metadata': {}
    }

    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Extract metadata
            if pdf_reader.metadata:
                result['metadata'] = {
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                }

            # Extract text from each page
            result['total_pages'] = len(pdf_reader.pages)

            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                result['pages'].append({
                    'page_number': page_num,
                    'text': text.strip(),
                    'char_count': len(text)
                })

    except Exception as e:
        result['error'] = str(e)

    return result
