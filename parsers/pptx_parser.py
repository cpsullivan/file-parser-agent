"""PowerPoint Parser - Extract text and content from PPTX files"""

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from datetime import datetime
from pathlib import Path
import io
from PIL import Image
from parsers.image_analyzer import get_image_description, analyze_chart_image

def parse_pptx(filepath, enable_ai_vision=True):
    """
    Parse PowerPoint file and extract slide content

    Args:
        filepath: Path to PPTX file
        enable_ai_vision: Whether to use AI for image descriptions (default: True)

    Returns:
        dict: Parsed PowerPoint data
    """
    result = {
        'filename': Path(filepath).name,
        'file_type': 'powerpoint',
        'parsed_at': datetime.now().isoformat(),
        'slides': [],
        'metadata': {},
        'ai_vision_enabled': enable_ai_vision
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

            # Extract text and images from all shapes
            text_content = []
            image_count = 0
            chart_count = 0

            for shape in slide.shapes:
                shape_info = {
                    'type': str(shape.shape_type),
                    'has_text': hasattr(shape, 'text') and bool(shape.text.strip()),
                    'text': ''
                }

                # Extract text
                if hasattr(shape, 'text') and shape.text.strip():
                    text_content.append(shape.text.strip())
                    shape_info['text'] = shape.text.strip()

                # Detect images
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    image_count += 1
                    shape_info['content_type'] = 'image'
                    shape_info['image_number'] = image_count

                    # Try to get image metadata
                    try:
                        image = shape.image
                        shape_info['image_format'] = image.ext
                        shape_info['image_size_bytes'] = len(image.blob)

                        # Get image dimensions if available
                        try:
                            img_stream = io.BytesIO(image.blob)
                            pil_image = Image.open(img_stream)
                            shape_info['image_width'] = pil_image.width
                            shape_info['image_height'] = pil_image.height
                            shape_info['image_mode'] = pil_image.mode
                        except:
                            pass

                        # Position and size in presentation
                        shape_info['left'] = shape.left
                        shape_info['top'] = shape.top
                        shape_info['width'] = shape.width
                        shape_info['height'] = shape.height

                        # Generate AI description if enabled
                        if enable_ai_vision:
                            context = f"Slide {slide_num} ({slide_data.get('title', 'untitled')})"
                            ai_result = get_image_description(image.blob, image.ext, context)
                            shape_info['ai_analysis'] = ai_result
                            shape_info['description'] = ai_result['description']

                            if ai_result.get('enabled'):
                                shape_info['note'] = f"Image {image_count} ({image.ext}, {len(image.blob)//1024}KB) - AI-described"
                            else:
                                shape_info['note'] = f"Image {image_count} ({image.ext}, {len(image.blob)//1024}KB) - {ai_result.get('note', 'AI vision not available')}"
                        else:
                            shape_info['description'] = "[AI description disabled]"
                            shape_info['note'] = f"Image {image_count} ({image.ext}, {len(image.blob)//1024}KB) - AI vision disabled"
                    except Exception as e:
                        shape_info['note'] = f"Image {image_count} detected - {str(e)[:50]}"

                # Detect charts (embedded Excel)
                elif shape.shape_type == MSO_SHAPE_TYPE.CHART:
                    chart_count += 1
                    shape_info['content_type'] = 'chart'
                    shape_info['chart_number'] = chart_count

                    try:
                        # Extract chart data if available
                        chart = shape.chart
                        shape_info['chart_type'] = str(chart.chart_type)
                        shape_info['has_data'] = hasattr(chart, 'chart_data')
                        shape_info['note'] = f"Chart {chart_count} - Type: {chart.chart_type}"

                        # Try to extract chart data
                        if hasattr(chart, 'plots') and len(chart.plots) > 0:
                            shape_info['series_count'] = len(chart.plots[0].series)

                        # For charts that are images (screenshots or embedded), try AI analysis
                        # Note: Native PPTX charts don't have image data, only embedded/pasted charts do
                    except Exception as e:
                        shape_info['note'] = f"Chart {chart_count} detected - {str(e)[:50]}"

                # Detect tables
                elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                    shape_info['content_type'] = 'table'
                    try:
                        table = shape.table
                        shape_info['rows'] = len(table.rows)
                        shape_info['columns'] = len(table.columns)
                        shape_info['note'] = f"Table: {len(table.rows)}x{len(table.columns)}"
                    except:
                        shape_info['note'] = "Table detected"

                # Detect grouped shapes or embedded objects
                elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                    shape_info['content_type'] = 'group'
                    try:
                        shape_info['shape_count'] = len(shape.shapes)
                        shape_info['note'] = f"Group containing {len(shape.shapes)} shapes - Complex visual element, AI analysis recommended"
                    except:
                        shape_info['note'] = "Grouped shapes - Complex visual element"

                elif shape.shape_type == MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT:
                    shape_info['content_type'] = 'embedded_object'
                    shape_info['note'] = "Embedded object (possibly Excel chart or document) - Data extraction needed"

                # For shapes with no text but are visual elements
                elif not shape_info['has_text'] and shape.shape_type not in [MSO_SHAPE_TYPE.TEXT_BOX, MSO_SHAPE_TYPE.PLACEHOLDER]:
                    shape_info['visual_element'] = True
                    shape_info['note'] = f"Visual element (type: {shape.shape_type}) - AI analysis would provide description"

                slide_data['shapes'].append(shape_info)

            slide_data['image_count'] = image_count
            slide_data['chart_count'] = chart_count

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
