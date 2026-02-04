```markdown
# File Parser Agent - AI Coding Assistant Instructions

## Project Context

### Overview
The File Parser Agent is a document processing system that extracts structured content from business documents (PDF, Word, Excel, PowerPoint) and converts them into machine-readable formats (JSON, Markdown, CSV, TXT). This is a **Government of Alberta** project designed to support document analysis, content migration, data extraction, and AI-assisted document understanding.

### Project Goals
1. Extract text and structured content from common business document formats
2. Preserve document structure (pages, slides, sheets, tables)
3. Provide AI-powered image analysis for visual content using Claude Vision
4. Support multiple output formats for different use cases
5. Enable integration through multiple interfaces (web, CLI, API, MCP server)

### Current Status
- **Version**: 3.0 (Implemented)
- **Status**: DESIGN phase
- **Priority**: Medium

---

## Technical Stack

### Core Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Primary language |
| Flask | >= 3.0.0 | Web application framework |
| Anthropic SDK | >= 0.77.1 | Claude API for AI vision |

### Document Parsing Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| PyPDF2 | >= 3.0.1 | PDF text extraction |
| python-docx | >= 1.1.0 | Word document parsing |
| openpyxl | >= 3.1.2 | Excel spreadsheet parsing |
| python-pptx | >= 0.6.23 | PowerPoint parsing |
| Pillow | >= 10.2.0 | Image processing/compression |

### Integration Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| mcp | >= 1.0.0 | Model Context Protocol server |
| python-dotenv | >= 1.0.0 | Environment variable loading |
| Werkzeug | >= 3.0.1 | WSGI utilities |

### External Services
- **Anthropic API**: For AI vision analysis (optional, required only for image descriptions)

---

## Code Style & Conventions

### File Structure
```
file-parser-agent/
├── app.py                 # Flask web application
├── cli.py                 # Command-line interface
├── api_wrapper.py         # Python API wrapper with tool-use support
├── mcp_server.py          # MCP server for Claude Desktop
├── parsers/
│   ├── __init__.py
│   ├── pdf_parser.py      # PDF extraction logic
│   ├── word_parser.py     # Word document extraction
│   ├── excel_parser.py    # Excel spreadsheet extraction
│   └── pptx_parser.py     # PowerPoint extraction
├── formatters/
│   ├── __init__.py
│   ├── json_formatter.py  # JSON output generation
│   ├── markdown_formatter.py  # Markdown output generation
│   └── csv_formatter.py   # CSV output generation
├── utils/
│   ├── __init__.py
│   ├── file_utils.py      # File I/O utilities
│   ├── image_utils.py     # Image processing utilities
│   └── vision.py          # AI vision integration
├── outputs/               # Directory for saved parsed files
├── uploads/               # Temporary upload directory
├── templates/             # Flask HTML templates
├── static/                # Static assets (CSS, JS)
├── requirements.txt
├── .env.example
└── README.md
```

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Files | snake_case | `pdf_parser.py` |
| Classes | PascalCase | `DocumentParser` |
| Functions | snake_case | `parse_document()` |
| Constants | UPPER_SNAKE_CASE | `MAX_FILE_SIZE` |
| Variables | snake_case | `file_content` |
| Private methods | _leading_underscore | `_extract_text()` |

### Import Organization
```python
# Standard library imports
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Third-party imports
from flask import Flask, request, jsonify
from anthropic import Anthropic
from PIL import Image

# Local imports
from parsers.pdf_parser import PDFParser
from utils.file_utils import save_output
```

### Type Hints
Always use type hints for function signatures:
```python
def parse_document(
    file_path: Optional[str] = None,
    file_content: Optional[str] = None,
    filename: str = "",
    enable_ai_vision: bool = True
) -> Dict[str, Any]:
    """Parse a document and return structured data."""
    ...
```

### Docstrings
Use Google-style docstrings:
```python
def extract_tables(file_path: str) -> List[Dict[str, Any]]:
    """Extract all tables from a document.
    
    Args:
        file_path: Path to the document file.
        
    Returns:
        List of dictionaries containing table data with keys:
        - table_number: Sequential table identifier
        - rows: Number of rows
        - columns: Number of columns
        - data: 2D array of cell values
        
    Raises:
        ValueError: If file type is not supported.
        FileNotFoundError: If file does not exist.
    """
```

---

## Architecture Guidance

### Parser Architecture
Each document type has a dedicated parser class following this pattern:

```python
class BaseParser:
    """Base class for document parsers."""
    
    def __init__(self, file_path: Optional[str] = None, file_content: Optional[bytes] = None):
        self.file_path = file_path
        self.file_content = file_content
        
    def parse(self) -> Dict[str, Any]:
        """Parse the document and return structured data."""
        raise NotImplementedError
        
    def extract_metadata(self) -> Dict[str, Any]:
        """Extract document metadata."""
        raise NotImplementedError
        
    def extract_text(self) -> str:
        """Extract all text content."""
        raise NotImplementedError
```

### Output Structure Standards

#### PDF Output
```json
{
  "filename": "report.pdf",
  "file_type": "pdf",
  "parsed_at": "2024-01-15T10:30:00Z",
  "total_pages": 12,
  "metadata": {
    "title": "Quarterly Report",
    "author": "Jane Doe",
    "subject": "Q4 2024 Results",
    "creator": "Microsoft Word"
  },
  "pages": [
    {
      "page_number": 1,
      "text": "Content here...",
      "char_count": 1500
    }
  ]
}
```

#### Word Output
```json
{
  "filename": "document.docx",
  "file_type": "word",
  "parsed_at": "2024-01-15T10:30:00Z",
  "total_paragraphs": 45,
  "total_tables": 3,
  "image_count": 5,
  "embedded_object_count": 2,
  "metadata": {
    "title": "Project Plan",
    "author": "John Smith",
    "created": "2024-01-10",
    "modified": "2024-01-14"
  },
  "paragraphs": [
    {
      "text": "Paragraph content...",
      "style": "Normal",
      "has_embedded_objects": false
    }
  ],
  "tables": [
    {
      "table_number": 1,
      "rows": 5,
      "columns": 4,
      "data": [["Header1", "Header2"], ["Cell1", "Cell2"]]
    }
  ]
}
```

#### PowerPoint Output
```json
{
  "filename": "presentation.pptx",
  "file_type": "powerpoint",
  "parsed_at": "2024-01-15T10:30:00Z",
  "ai_vision_enabled": true,
  "metadata": {
    "total_slides": 20,
    "slide_width": 9144000,
    "slide_height": 6858000
  },
  "slides": [
    {
      "slide_number": 1,
      "title": "Introduction",
      "text": "Welcome to...",
      "notes": "Speaker notes here...",
      "image_count": 2,
      "chart_count": 1,
      "shapes": [
        {
          "type": "picture",
          "content_type": "image",
          "has_text": false,
          "description": "Company logo",
          "ai_analysis": {
            "description": "A blue corporate logo...",
            "tokens_used": 150
          }
        }
      ]
    }
  ]
}
```

### Error Handling Pattern
```python
class ParserError(Exception):
    """Base exception for parser errors."""
    pass

class UnsupportedFileTypeError(ParserError):
    """Raised when file type is not supported."""
    pass

class FileTooLargeError(ParserError):
    """Raised when file exceeds size limit."""
    pass

def parse_document(file_path: str) -> Dict[str, Any]:
    try:
        # Validate file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            raise FileTooLargeError(f"File exceeds {MAX_FILE_SIZE // 1024 // 1024}MB limit")
            
        # Parse based on extension
        ext = os.path.splitext(file_path)[1].lower()
        parser = get_parser_for_extension(ext)
        return parser.parse()
        
    except ParserError:
        raise
    except Exception as e:
        raise ParserError(f"Failed to parse document: {str(e)}")
```

---

## Requirements Summary

### Core Parsing Requirements
- Extract text from PDF, Word, Excel, PowerPoint
- Preserve document structure (pages, paragraphs, sheets, slides)
- Extract metadata (title, author, dates)
- Detect and catalog tables, images, charts
- Handle files up to 50MB

### AI Vision Requirements
- Generate AI descriptions for PowerPoint images/charts
- Support enabling/disabling per request
- Compress images exceeding 5MB API limit
- Gracefully degrade when API key unavailable

### Output Requirements
- JSON with consistent structure per file type
- Markdown with proper formatting and optional TOC
- CSV for table data export
- Save outputs with timestamp-based unique names

### Interface Requirements
- **Web**: Flask app with drag-drop upload, format selection, download
- **CLI**: Accept file path and output format arguments
- **API**: Python class with tool methods and chat interface
- **MCP**: Full tool suite for Claude Desktop integration

---

## Do's and Don'ts

### DO ✅

1. **Always validate file types before processing**
   ```python
   SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'}
   if ext not in SUPPORTED_EXTENSIONS:
       raise UnsupportedFileTypeError(f"Unsupported file type: {ext}")
   ```

2. **Always clean up temporary files**
   ```python
   try:
       result = process_file(temp_path)
   finally:
       if os.path.exists(temp_path):
           os.remove(temp_path)
   ```

3. **Always include timestamps in output**
   ```python
   result["parsed_at"] = datetime.utcnow().isoformat() + "Z"
   ```

4. **Always sanitize filenames**
   ```python
   from werkzeug.utils import secure_filename
   safe_filename = secure_filename(original_filename)
   ```

5. **Always handle empty/missing content gracefully**
   ```python
   text = paragraph.text.strip() if paragraph.text else ""
   ```

6. **Always use UTF-8 encoding**
   ```python
   with open(output_path, 'w', encoding='utf-8') as f:
       json.dump(data, f, ensure_ascii=False, indent=2)
   ```

7. **Always compress images before AI analysis**
   ```python
   if image_size > MAX_API_IMAGE_SIZE:
       image = compress_image(image, target_size=MAX_API_IMAGE_SIZE)
   ```

8. **Always provide meaningful error messages**
   ```python
   raise ValueError(f"Cannot parse '{filename}': {specific_reason}")
   ```

### DON'T ❌

1. **Don't log or expose file contents in errors**
   ```python
   # BAD
   logger.error(f"Failed to parse: {file_content[:1000]}")
   
   # GOOD
   logger.error(f"Failed to parse file: {filename}")
   ```

2. **Don't expose API keys in output or logs**
   ```python
   # BAD
   result["api_key"] = os.getenv("ANTHROPIC_API_KEY")
   
   # GOOD
   result["ai_vision_enabled"] = bool(os.getenv("ANTHROPIC_API_KEY"))
   ```

3. **Don't hardcode file paths**
   ```python
   # BAD
   OUTPUT_DIR = "/home/user/outputs"
   
   # GOOD
   OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(os.getcwd(), "outputs"))
   ```

4. **Don't assume file exists or is accessible**
   ```python
   # BAD
   with open(file_path) as f:
       content = f.read()
   
   # GOOD
   if not os.path.exists(file_path):
       raise FileNotFoundError(f"File not found: {file_path}")
   ```

5. **Don't silently swallow exceptions**
   ```python
   # BAD
   try:
       parse_table(table)
   except:
       pass
   
   # GOOD
   try:
       parse_table(table)
   except Exception as e:
       logger.warning(f"Failed to parse table {table_num}: {e}")
       tables.append({"error": str(e), "table_number": table_num})
   ```

6. **Don't process password-protected files**
   ```python
   if is_encrypted(file_path):
       raise ValueError("Password-protected files are not supported")
   ```

7. **Don't attempt OCR on scanned documents**
   ```python
   # Just extract what text is available - don't fail
   # but inform user if no text found
   if not extracted_text.strip():
       result["warning"] = "No extractable text found. File may be scanned/image-based."
   ```

8. **Don't block on AI vision failures**
   ```python
   try:
       ai_description = analyze_image(image_data)
   except Exception as e:
       ai_description = {"error": f"AI analysis unavailable: {e}"}
   ```

---

## Example Code Patterns

### Parser Implementation
```python
# parsers/pdf_parser.py
import os
from datetime import datetime
from typing import Dict, Any, Optional
from PyPDF2 import PdfReader

class PDFParser:
    """Parser for PDF documents."""
    
    def __init__(self, file_path: Optional[str] = None, file_content: Optional[bytes] = None):
        self.file_path = file_path
        self.file_content = file_content
        
    def parse(self) -> Dict[str, Any]:
        """Parse PDF and return structured data."""
        if self.file_path:
            reader = PdfReader(self.file_path)
            filename = os.path.basename(self.file_path)
        else:
            from io import BytesIO
            reader = PdfReader(BytesIO(self.file_content))
            filename = "uploaded.pdf"
            
        result = {
            "filename": filename,
            "file_type": "pdf",
            "parsed_at": datetime.utcnow().isoformat() + "Z",
            "total_pages": len(reader.pages),
            "metadata": self._extract_metadata(reader),
            "pages": []
        }
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            result["pages"].append({
                "page_number": i + 1,
                "text": text,
                "char_count": len(text)
            })
            
        return result
        
    def _extract_metadata(self, reader: PdfReader) -> Dict[str, Any]:
        """Extract PDF metadata."""
        meta = reader.metadata or {}
        return {
            "title": meta.get("/Title", ""),
            "author": meta.get("/Author", ""),
            "subject": meta.get("/Subject", ""),
            "creator": meta.get("/Creator", "")
        }
```

### MCP Tool Implementation
```python
# mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

server = Server("file-parser-agent")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="parse_document",
            description="Extract content from PDF, Word, Excel, or PowerPoint files",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file"
                    },
                    "file_content": {
                        "type": "string",
                        "description": "Base64-encoded file content"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Original filename with extension"
                    },
                    "enable_ai_vision": {
                        "type": "boolean",
                        "description": "Enable AI image analysis",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        # ... other tools
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "parse_document":
        result = parse_document(**arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    # ... handle other tools
```

### API Wrapper Pattern
```python
# api_wrapper.py
from typing import Dict, Any, Optional
from anthropic import Anthropic
import json

class FileParserAgent:
    """Python API wrapper with Claude tool-use support."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key) if api_key else Anthropic()
        self.tools = self._define_tools()
        
    def parse(self, file_path: str, output_format: str = "json") -> Dict[str, Any]:
        """Convenience method for direct file parsing."""
        result = self._execute_tool("parse_document", {"file_path": file_path})
        if output_format != "json":
            result = self._execute_tool("format_output", {
                "parsed_data": result,
                "format": output_format
            })
        return result
        
    def chat(self, message: str) -> str:
        """Conversational interface with tool-use support."""
        messages = [{"role": "user", "content": message}]
        
        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=self.tools,
                messages=messages
            )
            
            if response.stop_reason == "tool_use":
                # Execute tool calls
                tool_results = self._process_tool_calls(response)
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            else:
                # Return final text response
                return self._extract_text(response)
```

### Flask Endpoint Pattern
```python
# app.py
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}"}), 400
        
    filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(temp_path)
        
        output_format = request.form.get('format', 'json')
        enable_vision = request.form.get('enable_ai_vision', 'true').lower() == 'true'
        
        result = parse_document(
            file_path=temp_path,
            enable_ai_vision=enable_vision
        )
        
        if output_format == 'markdown':
            result = format_as_markdown(result)
            
        return jsonify(result)
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

---

## Testing Requirements

### Unit Tests
Each parser must have unit tests covering:
- Valid file parsing
- Empty file handling
- Malformed file handling
- Metadata extraction
- Table extraction (where applicable)

```python
# tests/test_pdf_parser.py
import pytest
from parsers.pdf_parser import PDFParser

class TestPDFParser:
    def test_parse_valid_pdf(self, sample_pdf_path):
        parser = PDFParser(file_path=sample_pdf_path)
        result = parser.parse()
        
        assert result["file_type"] == "pdf"
        assert result["total_pages"] > 0
        assert "pages" in result
        assert all("text" in page for page in result["pages"])
        
    def test_parse_empty_pdf(self, empty_pdf_path):
        parser = PDFParser(file_path=empty_pdf_path)
        result = parser.parse()
        
        assert result["total_pages"] == 0
        assert result["pages"] == []
        
    def test_parse_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            parser = PDFParser(file_path="/nonexistent/file.pdf")
            parser.parse()
```

### Integration Tests
Test complete workflows:
- File upload → Parse → Save → Download
- API wrapper tool-use loops
- MCP server tool calls

### Test Coverage Requirements
- Minimum 80% code coverage
- 100% coverage on parser core logic
- All error paths tested

### Test Data
Create test fixtures for:
- Small valid files of each type
- Files with tables
- Files with images/charts
- Files with complex metadata
- Edge cases (empty files, single page, 100+ pages)

---

## Environment Configuration

### Required Environment Variables
```bash
# .env.example
ANTHROPIC_API_KEY=sk-ant-...  # Required for AI vision features
OUTPUT_DIR=./outputs           # Directory for saved outputs
UPLOAD_DIR=./uploads          # Temporary upload directory
MAX_FILE_SIZE=52428800        # 50MB in bytes
FLASK_DEBUG=false             # Enable debug mode
```

### Configuration Loading
```python
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))
    
    @classmethod
    def ensure_directories(cls):
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
```

---

## Limitations to Enforce

The AI assistant should **refuse or warn** when asked to implement:

1. **OCR functionality** - Out of scope, recommend external OCR service
2. **Password-protected file handling** - Not supported
3. **Document editing/creation** - Parse-only tool
4. **Cloud storage integration** - Future consideration
5. **Multi-user authentication** - Single-user design
6. **Batch processing queues** - Future consideration
7. **Email parsing (.eml, .msg)** - Not supported
8. **Archive extraction (.zip, .rar)** - Not supported

When these are requested, respond with:
> "This functionality is out of scope for the File Parser Agent. The current scope focuses on extracting content from PDF, Word, Excel, and PowerPoint files. See the scope document for future considerations."
```