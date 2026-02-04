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

### 2. Set Up Environment

Create a `.env` file with your Anthropic API key (for AI vision features):
```bash
ANTHROPIC_API_KEY=your-api-key-here
ENABLE_AI_VISION=true
```

### 3. Run the Application

**Web Interface:**
```bash
python app.py
```
Navigate to: `http://localhost:5000`

**API Wrapper (CLI):**
```bash
python api_wrapper.py document.pdf json
```

**Interactive Mode:**
```bash
python api_wrapper.py
>>> parse report.pdf markdown
>>> chat What file formats do you support?
```

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
├── app.py                    # Flask web application
├── api_wrapper.py            # Claude API integration with tools
├── examples.py               # Usage examples
├── requirements.txt          # Python dependencies
├── parsers/                  # File parser modules
│   ├── pdf_parser.py
│   ├── word_parser.py
│   ├── excel_parser.py
│   ├── pptx_parser.py
│   └── image_analyzer.py     # AI vision for images
├── templates/                # HTML templates
│   └── index.html
├── static/                   # CSS and assets
│   └── style.css
├── claude-agent-config.json  # Claude console agent definition
├── claude-instructions.md    # Project instructions for Claude
├── claude-tool-schemas.json  # Tool schemas for Claude API
├── mcp_server.py             # MCP server for Claude Desktop
├── claude_desktop_config.json # Claude Desktop configuration
├── uploads/                  # Temporary file storage
└── outputs/                  # Parsed file storage
```

## Claude API Integration

The `api_wrapper.py` provides full Claude API integration with tool-use:

### Available Tools

| Tool | Description |
|------|-------------|
| `file_reader` | Validate and read uploaded files |
| `parse_document` | Extract structured content from documents |
| `analyze_image` | AI vision for images and charts |
| `format_as_json` | Format output as JSON |
| `format_as_markdown` | Format output as Markdown |
| `create_artifact` | Save output to file |
| `extract_tables` | Extract only table data |
| `summarize_document` | Generate document summaries |

### Python Usage

```python
from api_wrapper import FileParserAgent

# Initialize agent
agent = FileParserAgent()

# Parse a file directly
result = agent.parse_file("report.pdf", output_format="markdown")
print(result['content'])

# Chat with the agent
response = agent.chat("Summarize the key points from this document",
                      file_content=base64_content,
                      filename="report.pdf")

# Use individual tools
parsed = agent.tool_parse_document(file_content, filename)
summary = agent.tool_summarize_document(parsed, summary_length="detailed")
```

### Claude Console Setup

1. Create a new project at [claude.ai](https://claude.ai)
2. Add contents of `claude-instructions.md` to custom instructions
3. Upload `claude-tool-schemas.json` as project knowledge

For full API integration, use `api_wrapper.py` with your application.

## MCP Server (Claude Desktop)

The `mcp_server.py` provides Model Context Protocol integration for Claude Desktop.

### Setup

1. Install the MCP package:
```bash
pip install mcp
```

2. Add to Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json` on Windows):
```json
{
  "mcpServers": {
    "file-parser-agent": {
      "command": "python",
      "args": ["C:\\path\\to\\file-parser-agent\\mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key"
      }
    }
  }
}
```

3. Restart Claude Desktop

### MCP Tools

| Tool | Description |
|------|-------------|
| `parse_document` | Parse PDF/Word/Excel/PowerPoint files |
| `analyze_image` | AI vision for images and charts |
| `format_output` | Format as JSON or Markdown |
| `save_output` | Save to outputs directory |
| `extract_tables` | Extract only table data |
| `list_outputs` | List saved output files |
| `read_output` | Read a saved output file |
| `delete_output` | Delete an output file |

### Usage in Claude Desktop

Once configured, you can ask Claude:
- "Parse the document at C:\Users\me\report.pdf"
- "Extract tables from this Excel file and format as markdown"
- "Analyze the chart image and describe the trends"
- "List my parsed output files"

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

## Version 3.0 Enhancements ✅

- ✅ AI-powered image descriptions (Claude Vision)
- ✅ Claude API wrapper with tool-use integration
- ✅ Interactive CLI mode
- ✅ Document summarization
- ✅ Chat-based file parsing
- ✅ MCP server for Claude Desktop

## Future Enhancements

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
