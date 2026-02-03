# File Parser Agent

A simple web-based file parser that converts PDF, Word, Excel, and PowerPoint files into JSON or Markdown format.

## Features

- **Multi-format Support**: Parse PDF, DOCX, XLSX, and PPTX files
- **Dual Output**: Export as JSON or Markdown
- **Simple Interface**: Two-column layout for easy file upload and download
- **Drag & Drop**: Drag files directly onto the upload area
- **Real-time Processing**: See parsing results immediately
- **File History**: View and download previously parsed files
- **Clear/Delete**: Remove individual files or clear all parsed files ✨ NEW
- **Enhanced PowerPoint**: Detect images, charts, tables, and embedded objects ✨ NEW
- **Enhanced Word**: Detect embedded Excel charts and inline images ✨ NEW

## Supported File Types

- **PDF** (.pdf) - Text extraction with page-by-page content and metadata
- **Word** (.docx, .doc) - Paragraphs, tables, embedded objects (charts/images), metadata
- **Excel** (.xlsx, .xls) - All sheets with complete data in tabular format
- **PowerPoint** (.pptx, .ppt) - Text, titles, notes, images, charts, tables, embedded objects

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open in Browser

Navigate to: `http://localhost:5000`

## Usage

1. **Upload Files**: Drag and drop files or click "Browse Files"
2. **Choose Format**: Select JSON or Markdown output
3. **View Results**: Parsed files appear in the right column
4. **Download**: Click download button to save the parsed file

## Output Formats

### JSON Output
Structured data with metadata, content, and file-specific fields:
```json
{
  "filename": "example.pdf",
  "file_type": "pdf",
  "parsed_at": "2026-02-03T13:00:00",
  "pages": [
    {"page_number": 1, "text": "..."}
  ]
}
```

### Markdown Output
Human-readable format with headers and tables:
```markdown
# Document Title
**File Type:** PDF
**Parsed:** 2026-02-03

## Content
...
```

## Project Structure

```
file-parser-agent/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── parsers/           # File parser modules
│   ├── pdf_parser.py
│   ├── word_parser.py
│   ├── excel_parser.py
│   └── pptx_parser.py
├── templates/         # HTML templates
│   └── index.html
├── static/           # CSS and assets
│   └── style.css
├── uploads/          # Temporary file storage
└── outputs/          # Parsed file storage
```

## API Endpoints

- `GET /` - Main application interface
- `POST /upload` - Upload and parse file
- `GET /download/<filename>` - Download parsed file
- `GET /list-outputs` - List all parsed files
- `DELETE /delete/<filename>` - Delete individual parsed file ✨ NEW
- `POST /clear-all` - Clear all parsed files ✨ NEW

## Configuration

- **Max File Size**: 50MB (configurable in `app.py`)
- **Port**: 5000 (configurable in `app.py`)
- **Upload Directory**: `uploads/`
- **Output Directory**: `outputs/`

## Requirements

- Python 3.8+
- Flask 3.0+
- PyPDF2, python-docx, openpyxl, python-pptx

## Limitations

- OCR not included (scanned PDFs may have limited text)
- Complex formatting may not be fully preserved
- Large files (>50MB) are rejected
- Images are not extracted from documents

## Version 2.0 Enhancements ✅

- ✅ Clear/Delete functionality (individual and bulk)
- ✅ Enhanced PowerPoint parsing (images, charts, tables detection)
- ✅ Enhanced Word parsing (embedded Excel detection)
- ✅ Rich metadata extraction for all file types

## Future Enhancements

- [ ] AI-powered image descriptions (Claude Vision / GPT-4 Vision)
- [ ] Advanced embedded Excel chart data extraction
- [ ] Add OCR support for scanned documents
- [ ] Extract and save images from files
- [ ] Batch processing of multiple files
- [ ] Cloud storage integration
- [ ] API authentication

📘 See [ENHANCEMENTS_V2.md](ENHANCEMENTS_V2.md) for detailed documentation.

## License

MIT License - Free to use and modify

## Author

Created with Claude Code
