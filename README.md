# File Parser Agent

A web-based document parser that converts PDF, Word, Excel, and PowerPoint files into structured JSON or Markdown format.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-gray)

## Features

- **Multi-format Support**: Parse PDF, DOCX, XLSX, and PPTX files
- **Dual Output**: Export as JSON or Markdown
- **Drag & Drop**: Modern web interface with drag-and-drop upload
- **AI Vision**: Claude-powered image analysis for PowerPoint (NEW)
- **Real-time Preview**: See parsing results immediately
- **File History**: View, download, and manage previously parsed files
- **Clean Architecture**: Modular design with separated concerns

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

Navigate to: **http://localhost:5000**

## Screenshots

```
┌────────────────────────────────────────────────────────────────┐
│                    📄 File Parser Agent                        │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────┐           │
│  │                     │    │   Parsed Files      │           │
│  │   📁 Drag & Drop    │    │                     │           │
│  │      file here      │    │  📋 report.json     │           │
│  │         or          │    │  📝 slides.md       │           │
│  │   [Browse Files]    │    │  📋 data.json       │           │
│  │                     │    │                     │           │
│  │  ○ JSON  ○ Markdown │    │  [🔄] [🗑️ Clear]   │           │
│  └─────────────────────┘    └─────────────────────┘           │
└────────────────────────────────────────────────────────────────┘
```

## AI Vision (NEW in v2.1)

AI Vision uses Claude to automatically analyze and describe images in PowerPoint presentations.

### Features

- **General Image Analysis**: Describes photos, illustrations, icons, logos
- **Chart Analysis**: Identifies chart types, data trends, axes labels
- **Diagram Analysis**: Describes flowcharts, org charts, process diagrams
- **Automatic Compression**: Large images are automatically compressed

### Setup

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

Or add to `.env` file:

```
ANTHROPIC_API_KEY=your-api-key-here
```

### Usage

AI Vision is enabled by default in the web interface. Toggle it off for faster processing without image analysis.

**Programmatic usage:**

```python
from core.parser_manager import ParserManager

# With AI Vision
result = ParserManager.parse('presentation.pptx', enable_ai_vision=True)

# Without AI Vision
result = ParserManager.parse('presentation.pptx', enable_ai_vision=False)
```

### Output Example

```json
{
  "slides": [{
    "slide_number": 1,
    "shapes": [{
      "content_type": "image",
      "ai_analysis": {
        "enabled": true,
        "description": "A bar chart showing quarterly sales data...",
        "model": "claude-sonnet-4-20250514",
        "tokens_used": 150
      }
    }]
  }]
}
```

### Graceful Degradation

When the API key is not configured:
- AI Vision shows as "not available" in the UI
- Images are still detected and basic metadata is extracted
- Fallback descriptions indicate AI analysis is unavailable

## MCP Server for Claude Desktop (NEW in v2.1)

The File Parser Agent can run as an MCP (Model Context Protocol) server, allowing Claude Desktop to parse documents directly.

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Claude Desktop** (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "file-parser-agent": {
         "command": "python",
         "args": ["/absolute/path/to/file-parser-agent/mcp_server.py"],
         "env": {
           "ANTHROPIC_API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

   Config file locations:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. **Restart Claude Desktop**

### Available Tools

| Tool | Description |
|------|-------------|
| `parse_document` | Parse PDF, Word, Excel, PowerPoint files |
| `analyze_image` | Analyze images using Claude Vision |
| `format_output` | Convert parsed data to JSON or Markdown |
| `save_output` | Save content to outputs directory |
| `list_outputs` | List saved output files |
| `read_output` | Read a saved output file |
| `delete_output` | Delete a saved output file |
| `get_info` | Get agent version and capabilities |

### Example Usage in Claude Desktop

Once configured, you can ask Claude:

- "Parse this PDF file at /path/to/document.pdf"
- "Convert this Word document to Markdown"
- "Analyze the charts in this PowerPoint presentation"
- "List all the files you've parsed for me"

### Testing the MCP Server

```bash
# Test the server tools directly
python tests/test_mcp_server.py

# Run the server manually (for debugging)
python mcp_server.py
```

## Command-Line Interface (NEW in v2.1)

Parse documents directly from the command line.

### Basic Usage

```bash
# Parse to JSON (stdout)
python cli.py document.pdf

# Parse to Markdown
python cli.py report.docx -f markdown

# Save to file
python cli.py data.xlsx -o output.json

# Parse PowerPoint with AI Vision
python cli.py slides.pptx --ai-vision

# Save to outputs directory
python cli.py document.pdf -s
```

### Commands

```bash
python cli.py --help           # Show help
python cli.py --info           # System information
python cli.py --list           # List saved outputs
python cli.py --clear          # Clear all outputs
python cli.py -i               # Interactive mode
```

### Interactive Mode

```bash
$ python cli.py -i

FILE PARSER AGENT - Interactive Mode

parser> parse document.pdf
Saved to: document_20260204_120000.json
  Pages: 5

parser> list
document_20260204_120000.json    2.3 KB    2026-02-04T12:00:00

parser> quit
```

## Python API (NEW in v2.1)

Use the File Parser Agent programmatically in your Python code.

### Quick Start

```python
from api_wrapper import FileParserAgent

# Create agent
agent = FileParserAgent()

# Parse a file
result = agent.parse_file('document.pdf')
if result['success']:
    print(result['data'])  # Parsed data
    print(result['formatted'])  # JSON string
```

### Full API

```python
from api_wrapper import FileParserAgent

agent = FileParserAgent()

# Parse with options
result = agent.parse_file(
    'presentation.pptx',
    output_format='markdown',    # 'json' or 'markdown'
    enable_ai_vision=True,       # AI image analysis
    save_output=True             # Save to outputs/
)

# Parse from bytes
with open('document.pdf', 'rb') as f:
    result = agent.parse_bytes(f.read(), 'document.pdf')

# Parse from base64
result = agent.parse_base64(base64_content, 'document.pdf')

# Manage outputs
outputs = agent.list_outputs()
content = agent.read_output('document_20260204.json')
agent.delete_output('document_20260204.json')
agent.clear_outputs()

# Get system info
info = agent.get_info()
```

### Convenience Functions

```python
from api_wrapper import parse, parse_to_json, parse_to_markdown

# Quick parse
result = parse('document.pdf', enable_ai_vision=True)

# Get formatted output directly
json_str = parse_to_json('document.pdf')
md_str = parse_to_markdown('document.pdf')
```

### Claude Tool-Use Integration

The API wrapper includes tool definitions for Claude API integration:

```python
from api_wrapper import TOOL_DEFINITIONS, handle_tool_call

# Use TOOL_DEFINITIONS with Claude API
# Handle tool calls with handle_tool_call()
result = handle_tool_call('parse_document', {
    'file_path': 'document.pdf',
    'output_format': 'json'
})
```

## MCP Server (NEW in v2.1)

The MCP (Model Context Protocol) server enables Claude Desktop integration, allowing Claude to parse documents directly.

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Claude Desktop:**
   
   Edit your Claude Desktop config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "file-parser": {
         "command": "python",
         "args": ["/path/to/file-parser-agent/mcp_server.py"],
         "env": {
           "ANTHROPIC_API_KEY": "your-api-key"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Available Tools

| Tool | Description |
|------|-------------|
| `parse_document` | Parse PDF, Word, Excel, PowerPoint files |
| `analyze_image` | AI-powered image analysis |
| `format_output` | Convert between JSON and Markdown |
| `save_output` | Save parsed content to file |
| `list_outputs` | List saved output files |
| `read_output` | Read a saved output file |
| `delete_output` | Delete a saved output file |
| `extract_tables` | Extract only table data |
| `get_info` | Get agent capabilities and status |

### Example Usage in Claude Desktop

Once configured, you can ask Claude:

> "Parse the document at /path/to/report.pdf and summarize it"

> "Extract all tables from /path/to/data.xlsx"

> "Analyze the chart image at /path/to/chart.png"

### Running Standalone

```bash
# Test the server (will wait for MCP client)
python mcp_server.py
```

## MCP Server for Claude Desktop (NEW in v2.1)

The MCP (Model Context Protocol) server enables Claude Desktop to parse documents directly.

### Setup

1. **Install the MCP package:**
   ```bash
   pip install mcp
   ```

2. **Configure Claude Desktop** (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "file-parser": {
         "command": "python",
         "args": ["/path/to/file-parser-agent/mcp_server.py"],
         "env": {
           "ANTHROPIC_API_KEY": "your-api-key-for-ai-vision"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** to load the new server.

### Available Tools

| Tool | Description |
|------|-------------|
| `parse_document` | Parse PDF, Word, Excel, PowerPoint files |
| `analyze_image` | Analyze images with AI Vision |
| `format_output` | Convert between JSON and Markdown |
| `save_output` | Save parsed content to disk |
| `list_outputs` | List saved output files |
| `read_output` | Read a saved output file |
| `delete_output` | Delete a saved file |
| `get_info` | Get agent information |

### Example Usage in Claude Desktop

Once configured, you can ask Claude to:

- "Parse this PDF and summarize it" (with file attachment)
- "Convert this Word document to Markdown"
- "What images are in this PowerPoint presentation?"
- "List all my parsed documents"

### Running Standalone

```bash
# Test the MCP server
python tests/test_mcp_server.py

# Run the server (normally done by Claude Desktop)
python mcp_server.py
```

## Supported File Types

| Format | Extensions | What's Extracted |
|--------|------------|------------------|
| PDF | `.pdf` | Text, pages, metadata |
| Word | `.docx`, `.doc` | Paragraphs, tables, styles, metadata |
| Excel | `.xlsx`, `.xls` | All sheets, cell data, formulas |
| PowerPoint | `.pptx`, `.ppt` | Slides, titles, notes, shapes |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface |
| `POST` | `/upload` | Upload and parse file |
| `GET` | `/download/<filename>` | Download parsed file |
| `GET` | `/view/<filename>` | View file in browser |
| `GET` | `/list-outputs` | List all parsed files |
| `DELETE` | `/delete/<filename>` | Delete a parsed file |
| `POST` | `/clear-all` | Delete all parsed files |
| `GET` | `/api/info` | API information |

### Upload Example

```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@document.pdf" \
  -F "format=json"
```

### Response

```json
{
  "success": true,
  "filename": "document_20260204_120000.json",
  "original_filename": "document.pdf",
  "format": "json",
  "parsed_data": {
    "filename": "document.pdf",
    "file_type": "pdf",
    "total_pages": 5,
    "pages": [...]
  }
}
```

## Output Formats

### JSON Output

```json
{
  "filename": "report.pdf",
  "file_type": "pdf",
  "parsed_at": "2026-02-04T12:00:00",
  "total_pages": 3,
  "metadata": {
    "title": "Annual Report",
    "author": "John Doe"
  },
  "pages": [
    {
      "page_number": 1,
      "text": "Page content...",
      "char_count": 1234
    }
  ]
}
```

### Markdown Output

```markdown
# report.pdf

**File Type:** pdf
**Parsed:** 2026-02-04T12:00:00

---

**Total Pages:** 3

## Page 1
Page content...
```

## Project Structure

```
file-parser-agent/
├── app.py                  # Flask web application
├── cli.py                  # Command-line interface
├── api_wrapper.py          # Python API wrapper
├── mcp_server.py           # MCP server for Claude Desktop (NEW)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
│
├── core/                  # Core engine
│   ├── parser_manager.py  # Routes files to parsers
│   ├── output_formatter.py # JSON/Markdown formatting
│   ├── file_manager.py    # File I/O operations
│   └── ai_vision.py       # Claude Vision integration
│
├── parsers/               # Document parsers
│   ├── base_parser.py     # Abstract base class
│   ├── pdf_parser.py      # PDF parsing
│   ├── word_parser.py     # Word document parsing
│   ├── excel_parser.py    # Excel spreadsheet parsing
│   └── pptx_parser.py     # PowerPoint parsing
│
├── templates/             # HTML templates
│   └── index.html         # Main web interface
│
├── static/                # Static assets
│   └── style.css          # Stylesheet
│
├── uploads/               # Temporary upload storage
├── outputs/               # Parsed output storage
│
└── tests/                 # Test suite
    ├── test_parsers.py    # Unit tests
    ├── test_ai_vision.py  # AI Vision tests
    ├── test_mcp_server.py # MCP server tests (NEW)
    └── sample_files/      # Test documents
```

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# Flask
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Limits
MAX_CONTENT_LENGTH=52428800  # 50MB

# AI Vision (Phase 3)
ANTHROPIC_API_KEY=your-api-key
```

### File Size Limit

Default: 50MB. Configurable via `MAX_CONTENT_LENGTH` environment variable.

## Programmatic Usage

```python
from core.parser_manager import ParserManager
from core.output_formatter import OutputFormatter

# Parse a file
result = ParserManager.parse('document.pdf')

# Format as JSON
json_output = OutputFormatter.to_json(result)

# Format as Markdown
md_output = OutputFormatter.to_markdown(result)
```

## Running Tests

```bash
# Run unit tests
python -m unittest tests.test_parsers -v

# Run integration test
python tests/quick_test.py
```

## Requirements

- Python 3.8+
- Flask 3.0+
- PyPDF2, python-docx, openpyxl, python-pptx

## Limitations

- **No OCR**: Scanned PDFs with image-only content have limited text extraction
- **No Password Protection**: Encrypted files are not supported
- **Size Limit**: Maximum file size is 50MB
- **Formatting**: Complex formatting may not be fully preserved

## Roadmap

- [x] Phase 1: Core parsing engine
- [x] Phase 2: Web interface
- [x] Phase 3: AI Vision integration
- [x] Phase 4: CLI and Python API
- [x] Phase 5: MCP Server for Claude Desktop

**All phases complete! 🎉**

## License

MIT License - Free to use and modify

## Author

Created with Claude
