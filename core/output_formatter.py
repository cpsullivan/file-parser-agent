"""Output Formatter - converts parsed data to JSON and Markdown formats."""

import json
from typing import Dict, Any, List
from datetime import datetime


class OutputFormatter:
    """
    Formats parsed document data into different output formats.
    
    Supported formats:
    - JSON: Structured data with consistent schema
    - Markdown: Human-readable formatted text
    """
    
    @staticmethod
    def to_json(data: Dict[str, Any], pretty: bool = True) -> str:
        """
        Format parsed data as JSON string.
        
        Args:
            data: Parsed document data dictionary
            pretty: Whether to pretty-print with indentation
            
        Returns:
            JSON string
        """
        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    
    @staticmethod
    def to_markdown(data: Dict[str, Any]) -> str:
        """
        Format parsed data as Markdown.
        
        Args:
            data: Parsed document data dictionary
            
        Returns:
            Markdown formatted string
        """
        lines = []
        
        # Document header
        filename = data.get('filename', 'Document')
        lines.append(f"# {filename}")
        lines.append("")
        
        # Metadata block
        file_type = data.get('file_type', 'unknown')
        parsed_at = data.get('parsed_at', datetime.now().isoformat())
        
        lines.append(f"**File Type:** {file_type}")
        lines.append(f"**Parsed:** {parsed_at}")
        
        # Add error if present
        if 'error' in data:
            lines.append(f"**Error:** {data['error']}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Format content based on file type
        if file_type == 'pdf':
            lines.extend(OutputFormatter._format_pdf_markdown(data))
        elif file_type == 'word':
            lines.extend(OutputFormatter._format_word_markdown(data))
        elif file_type == 'excel':
            lines.extend(OutputFormatter._format_excel_markdown(data))
        elif file_type == 'powerpoint':
            lines.extend(OutputFormatter._format_pptx_markdown(data))
        
        return '\n'.join(lines)
    
    @staticmethod
    def _format_pdf_markdown(data: Dict) -> List[str]:
        """Format PDF content as Markdown."""
        lines = []
        
        # Summary
        total_pages = data.get('total_pages', 0)
        lines.append(f"**Total Pages:** {total_pages}")
        
        # Metadata
        metadata = data.get('metadata', {})
        if any(metadata.values()):
            lines.append("")
            lines.append("## Metadata")
            lines.append("")
            for key, value in metadata.items():
                if value:
                    lines.append(f"- **{key.title()}:** {value}")
        
        lines.append("")
        
        # Pages
        pages = data.get('pages', [])
        for page in pages:
            page_num = page.get('page_number', '?')
            char_count = page.get('char_count', 0)
            text = page.get('text', '')
            
            lines.append(f"## Page {page_num}")
            lines.append(f"*{char_count} characters*")
            lines.append("")
            
            if text.strip():
                lines.append(text)
            else:
                lines.append("*[No text content]*")
            
            lines.append("")
        
        return lines
    
    @staticmethod
    def _format_word_markdown(data: Dict) -> List[str]:
        """Format Word document content as Markdown."""
        lines = []
        
        # Summary
        lines.append(f"**Paragraphs:** {data.get('total_paragraphs', 0)}")
        lines.append(f"**Tables:** {data.get('total_tables', 0)}")
        lines.append(f"**Images:** {data.get('image_count', 0)}")
        
        # Metadata
        metadata = data.get('metadata', {})
        if any(metadata.values()):
            lines.append("")
            lines.append("## Metadata")
            lines.append("")
            for key, value in metadata.items():
                if value:
                    lines.append(f"- **{key.title()}:** {value}")
        
        lines.append("")
        
        # Content (paragraphs)
        paragraphs = data.get('paragraphs', [])
        if paragraphs:
            lines.append("## Content")
            lines.append("")
            
            for para in paragraphs:
                text = para.get('text', '')
                style = para.get('style', 'Normal')
                
                # Format headings differently
                if 'Heading 1' in style:
                    lines.append(f"### {text}")
                elif 'Heading 2' in style:
                    lines.append(f"#### {text}")
                elif 'Heading' in style:
                    lines.append(f"##### {text}")
                else:
                    lines.append(text)
                
                lines.append("")
        
        # Tables
        tables = data.get('tables', [])
        if tables:
            lines.append("## Tables")
            lines.append("")
            
            for table in tables:
                table_num = table.get('table_number', '?')
                rows = table.get('rows', 0)
                cols = table.get('columns', 0)
                
                lines.append(f"### Table {table_num}")
                lines.append(f"*{rows} rows × {cols} columns*")
                lines.append("")
                
                table_data = table.get('data', [])
                if table_data:
                    lines.extend(OutputFormatter._format_table_markdown(table_data))
                else:
                    lines.append("*[Empty table]*")
                
                lines.append("")
        
        return lines
    
    @staticmethod
    def _format_excel_markdown(data: Dict) -> List[str]:
        """Format Excel spreadsheet content as Markdown."""
        lines = []
        
        # Summary
        metadata = data.get('metadata', {})
        total_sheets = metadata.get('total_sheets', 0)
        sheet_names = metadata.get('sheet_names', [])
        
        lines.append(f"**Total Sheets:** {total_sheets}")
        if sheet_names:
            lines.append(f"**Sheet Names:** {', '.join(sheet_names)}")
        
        lines.append("")
        
        # Sheets
        sheets = data.get('sheets', [])
        for sheet in sheets:
            name = sheet.get('name', 'Unnamed')
            rows = sheet.get('rows', 0)
            cols = sheet.get('columns', 0)
            
            lines.append(f"## {name}")
            lines.append(f"*{rows} rows × {cols} columns*")
            lines.append("")
            
            sheet_data = sheet.get('data', [])
            if sheet_data:
                # Limit to first 50 rows for display
                display_data = sheet_data[:50]
                lines.extend(OutputFormatter._format_table_markdown(display_data))
                
                if len(sheet_data) > 50:
                    lines.append(f"*...and {len(sheet_data) - 50} more rows*")
            else:
                lines.append("*[Empty sheet]*")
            
            lines.append("")
        
        return lines
    
    @staticmethod
    def _format_pptx_markdown(data: Dict) -> List[str]:
        """Format PowerPoint presentation content as Markdown."""
        lines = []
        
        # Summary
        metadata = data.get('metadata', {})
        total_slides = metadata.get('total_slides', 0)
        ai_enabled = data.get('ai_vision_enabled', False)
        ai_available = data.get('ai_vision_available', False)
        
        lines.append(f"**Total Slides:** {total_slides}")
        
        if ai_enabled:
            if ai_available:
                summary = data.get('ai_analysis_summary', {})
                analyzed = summary.get('images_analyzed', 0)
                total_images = summary.get('images_total', 0)
                lines.append(f"**AI Vision:** Enabled ({analyzed}/{total_images} images analyzed)")
            else:
                lines.append("**AI Vision:** Enabled but not configured")
        else:
            lines.append("**AI Vision:** Disabled")
        
        lines.append("")
        
        # Slides
        slides = data.get('slides', [])
        for slide in slides:
            slide_num = slide.get('slide_number', '?')
            title = slide.get('title', 'Untitled')
            
            lines.append(f"## Slide {slide_num}: {title}")
            lines.append("")
            
            # Content summary
            image_count = slide.get('image_count', 0)
            chart_count = slide.get('chart_count', 0)
            table_count = slide.get('table_count', 0)
            
            summary_parts = []
            if image_count:
                summary_parts.append(f"{image_count} image(s)")
            if chart_count:
                summary_parts.append(f"{chart_count} chart(s)")
            if table_count:
                summary_parts.append(f"{table_count} table(s)")
            
            if summary_parts:
                lines.append(f"*Contains: {', '.join(summary_parts)}*")
                lines.append("")
            
            # Text content
            text = slide.get('text', '').strip()
            if text:
                lines.append("### Content")
                lines.append("")
                lines.append(text)
                lines.append("")
            
            # Shapes with AI descriptions
            shapes = slide.get('shapes', [])
            
            # Images with AI analysis
            analyzed_images = [s for s in shapes 
                            if s.get('content_type') == 'image' 
                            and s.get('ai_analysis', {}).get('description')]
            
            if analyzed_images:
                lines.append("### Image Analysis (AI)")
                lines.append("")
                for i, img in enumerate(analyzed_images, 1):
                    desc = img['ai_analysis']['description']
                    lines.append(f"**Image {i}:**")
                    lines.append(f"> {desc}")
                    lines.append("")
            
            # Other visual elements (non-AI)
            other_visuals = [s for s in shapes 
                          if s.get('content_type') in ('image', 'chart', 'table', 'embedded_object')
                          and s.get('description')
                          and s not in analyzed_images]
            
            if other_visuals:
                lines.append("### Visual Elements")
                lines.append("")
                for shape in other_visuals:
                    content_type = shape.get('content_type', 'unknown')
                    description = shape.get('description', '')
                    lines.append(f"- **{content_type.title()}:** {description}")
                lines.append("")
            
            # Speaker notes
            notes = slide.get('notes', '').strip()
            if notes:
                lines.append("### Speaker Notes")
                lines.append("")
                lines.append(f"> {notes}")
                lines.append("")
        
        return lines
    
    @staticmethod
    def _format_table_markdown(data: List[List[Any]]) -> List[str]:
        """
        Convert 2D array to Markdown table format.
        
        Args:
            data: 2D list of cell values
            
        Returns:
            List of Markdown table lines
        """
        if not data:
            return ["*[Empty table]*"]
        
        lines = []
        
        # Calculate column widths for alignment
        col_count = max(len(row) for row in data) if data else 0
        if col_count == 0:
            return ["*[Empty table]*"]
        
        # Normalize rows to have same number of columns
        normalized_data = []
        for row in data:
            normalized_row = list(row) + [''] * (col_count - len(row))
            normalized_data.append(normalized_row)
        
        # Header row (first row of data)
        header = normalized_data[0]
        header_cells = [str(cell).replace('|', '\\|') for cell in header]
        lines.append("| " + " | ".join(header_cells) + " |")
        
        # Separator row
        lines.append("| " + " | ".join(["---"] * col_count) + " |")
        
        # Data rows
        for row in normalized_data[1:]:
            cells = [str(cell).replace('|', '\\|') for cell in row]
            lines.append("| " + " | ".join(cells) + " |")
        
        return lines
    
    @staticmethod
    def to_csv(data: Dict[str, Any]) -> str:
        """
        Extract table data and format as CSV.
        
        Only works for Excel files or documents with tables.
        
        Args:
            data: Parsed document data dictionary
            
        Returns:
            CSV formatted string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        file_type = data.get('file_type', '')
        
        if file_type == 'excel':
            # For Excel, export first sheet
            sheets = data.get('sheets', [])
            if sheets:
                for row in sheets[0].get('data', []):
                    writer.writerow(row)
        
        elif file_type == 'word':
            # For Word, export first table
            tables = data.get('tables', [])
            if tables:
                for row in tables[0].get('data', []):
                    writer.writerow(row)
        
        return output.getvalue()
