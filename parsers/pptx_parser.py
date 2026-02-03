"""PowerPoint Parser - Extract text and content from PPTX files"""

from pptx import Presentation
from datetime import datetime
from pathlib import Path

def parse_pptx(filepath):
    """
    Parse PowerPoint file and extract slide content

    Args:
        filepath: Path to PPTX file

    Returns:
        dict: Parsed PowerPoint data
    """
    result = {
        'filename': Path(filepath).name,
        'file_type': 'powerpoint',
        'parsed_at': datetime.now().isoformat(),
        'slides': [],
        'metadata': {}
    }

    try:
        prs = Presentation(filepath)

        # Extract metadata
        result['metadata'] = {
            'total_slides': len(prs.slides),
            'slide_width': prs.slide_width,
            'slide_height': prs.slide_height
        }

        # Extract content from each slide
        for slide_num, slide in enumerate(prs.slides, start=1):
            slide_data = {
                'slide_number': slide_num,
                'title': '',
                'text': '',
                'shapes': [],
                'notes': ''
            }

            # Extract title
            if slide.shapes.title:
                slide_data['title'] = slide.shapes.title.text.strip()

            # Extract text from all shapes
            text_content = []
            for shape in slide.shapes:
                if hasattr(shape, 'text') and shape.text.strip():
                    text_content.append(shape.text.strip())

                    shape_info = {
                        'type': shape.shape_type.name if hasattr(shape.shape_type, 'name') else str(shape.shape_type),
                        'text': shape.text.strip()
                    }
                    slide_data['shapes'].append(shape_info)

            slide_data['text'] = '\n\n'.join(text_content)

            # Extract notes
            if slide.has_notes_slide:
                notes_frame = slide.notes_slide.notes_text_frame
                if notes_frame:
                    slide_data['notes'] = notes_frame.text.strip()

            result['slides'].append(slide_data)

    except Exception as e:
        result['error'] = str(e)

    return result
