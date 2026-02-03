"""Word Document Parser - Extract text from DOCX files"""

from docx import Document
from datetime import datetime
from pathlib import Path

def parse_word(filepath):
    """
    Parse Word document and extract text content

    Args:
        filepath: Path to DOCX file

    Returns:
        dict: Parsed Word document data
    """
    result = {
        'filename': Path(filepath).name,
        'file_type': 'word',
        'parsed_at': datetime.now().isoformat(),
        'paragraphs': [],
        'tables': [],
        'metadata': {}
    }

    try:
        doc = Document(filepath)

        # Extract core properties
        core_props = doc.core_properties
        result['metadata'] = {
            'title': core_props.title or '',
            'author': core_props.author or '',
            'subject': core_props.subject or '',
            'created': str(core_props.created) if core_props.created else '',
            'modified': str(core_props.modified) if core_props.modified else '',
        }

        # Extract paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                result['paragraphs'].append({
                    'text': para.text.strip(),
                    'style': para.style.name if para.style else 'Normal'
                })

        # Extract tables
        for table_idx, table in enumerate(doc.tables, start=1):
            table_data = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_data.append(row_data)

            result['tables'].append({
                'table_number': table_idx,
                'rows': len(table.rows),
                'columns': len(table.columns),
                'data': table_data
            })

        result['total_paragraphs'] = len(result['paragraphs'])
        result['total_tables'] = len(result['tables'])

    except Exception as e:
        result['error'] = str(e)

    return result
