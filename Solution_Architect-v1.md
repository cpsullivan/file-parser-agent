# File Parser Agent - Solution Architecture Document

## Document Information

| Field | Value |
|-------|-------|
| Project | File Parser Agent |
| Version | 1.0 |
| Status | Design |
| Last Updated | 2026-02-04 |
| Organization | Government of Alberta |

---

## Executive Summary

This document describes the solution architecture for the File Parser Agent, a document processing system that extracts structured content from business documents (PDF, Word, Excel, PowerPoint) and converts them into machine-readable formats. The architecture supports multiple integration patterns including a web interface, command-line interface, Python API, and Model Context Protocol (MCP) server for Claude Desktop integration.

---

## 1. System Architecture

### 1.1 High-Level Architecture Overview

The File Parser Agent follows a **modular monolithic architecture** pattern, designed as a single deployable unit with well-defined internal boundaries. This approach balances simplicity of deployment with maintainability through clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FILE PARSER AGENT                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Web UI      │  │    CLI      │  │ Python API  │  │ MCP Server  │            │
│  │ (Flask)     │  │             │  │  Wrapper    │  │             │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                │                    │
│         └────────────────┴────────────────┴────────────────┘                    │
│                                   │                                             │
│                    ┌──────────────▼──────────────┐                              │
│                    │      Core Service Layer      │                              │
│                    │   (Tool Orchestration)       │                              │
│                    └──────────────┬──────────────┘                              │
│                                   │                                             │
│    ┌──────────────┬───────────────┼───────────────┬──────────────┐              │
│    │              │               │               │              │              │
│    ▼              ▼               ▼               ▼              ▼              │
│ ┌──────┐    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐          │
│ │ PDF  │    │   Word   │   │  Excel   │   │PowerPoint│   │  Output  │          │
│ │Parser│    │  Parser  │   │  Parser  │   │  Parser  │   │Formatter │          │
│ └──────┘    └──────────┘   └──────────┘   └──────────┘   └──────────┘          │
│                                   │                                             │
│                    ┌──────────────▼──────────────┐                              │
│                    │     External Services        │                              │
│                    │    (Anthropic Claude API)    │                              │
│                    └─────────────────────────────┘                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         File System Storage                              │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                │    │
│  │  │ Upload (temp) │  │    Outputs    │  │     Logs      │                │    │
│  │  └───────────────┘  └───────────────┘  └───────────────┘                │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Architectural Style

**Primary Pattern: Modular Monolith**

Rationale:
- Single deployment unit simplifies operations for a standalone tool
- Clear module boundaries enable future microservice extraction if needed
- Reduced operational complexity compared to distributed systems
- Appropriate for the expected load and single-user operation model

**Secondary Patterns:**
- **Strategy Pattern**: For document-type-specific parsing logic
- **Facade Pattern**: For API wrapper providing simplified interface
- **Plugin Pattern**: For MCP tool registration

### 1.3 System Context (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM CONTEXT                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
    │  Developer   │         │   Analyst    │         │   AI System  │
    │              │         │              │         │   (Claude)   │
    └──────┬───────┘         └──────┬───────┘         └──────┬───────┘
           │                        │                        │
           │ Python API/CLI         │ Web UI                 │ MCP Protocol
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │                               │
                    │     FILE PARSER AGENT         │
                    │                               │
                    │  Extracts structured content  │
                    │  from business documents      │
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    │ API Calls
                                    ▼
                    ┌───────────────────────────────┐
                    │                               │
                    │    Anthropic Claude API       │
                    │                               │
                    │  AI-powered image analysis    │
                    │                               │
                    └───────────────────────────────┘
```

---

## 2. Component Design

### 2.1 Container Diagram (C4 Level 2)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONTAINER DIAGRAM                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           File Parser Agent Application                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────┐    ┌────────────────────┐    ┌────────────────────┐     │
│  │   Web Application  │    │   CLI Application  │    │    MCP Server      │     │
│  │                    │    │                    │    │                    │     │
│  │  [Flask + HTML]    │    │  [Python argparse] │    │  [mcp library]     │     │
│  │                    │    │                    │    │                    │     │
│  │  - File upload     │    │  - parse command   │    │  - Tool handlers   │     │
│  │  - Result display  │    │  - chat command    │    │  - stdio transport │     │
│  │  - File download   │    │  - Interactive     │    │  - JSON responses  │     │
│  └─────────┬──────────┘    └─────────┬──────────┘    └─────────┬──────────┘     │
│            │                         │                         │                │
│            └─────────────────────────┼─────────────────────────┘                │
│                                      │                                          │
│                        ┌─────────────▼─────────────┐                            │
│                        │                           │                            │
│                        │    API Wrapper Layer      │                            │
│                        │    [FileParserAgent]      │                            │
│                        │                           │                            │
│                        │    - Tool definitions     │                            │
│                        │    - Tool execution       │                            │
│                        │    - Claude integration   │                            │
│                        │                           │                            │
│                        └─────────────┬─────────────┘                            │
│                                      │                                          │
│            ┌─────────────────────────┼─────────────────────────┐                │
│            │                         │                         │                │
│  ┌─────────▼─────────┐    ┌─────────▼─────────┐    ┌─────────▼─────────┐       │
│  │                   │    │                   │    │                   │       │
│  │  Parsing Engine   │    │  Vision Service   │    │  Output Manager   │       │
│  │                   │    │                   │    │                   │       │
│  │  - PDF parser     │    │  - Image analysis │    │  - JSON formatter │       │
│  │  - Word parser    │    │  - Chart analysis │    │  - MD formatter   │       │
│  │  - Excel parser   │    │  - Compression    │    │  - File I/O       │       │
│  │  - PPTX parser    │    │                   │    │                   │       │
│  │                   │    │                   │    │                   │       │
│  └───────────────────┘    └─────────┬─────────┘    └───────────────────┘       │
│                                     │                                           │
└─────────────────────────────────────┼───────────────────────────────────────────┘
                                      │
                                      │ HTTPS
                                      ▼
                        ┌─────────────────────────────┐
                        │    Anthropic Claude API     │
                        │    [External Service]       │
                        └─────────────────────────────┘
```

### 2.2 Component Specifications

#### 2.2.1 Web Application Component

| Attribute | Value |
|-----------|-------|
| Technology | Flask 3.0+ |
| Responsibility | HTTP request handling, file upload, result display |
| Dependencies | Werkzeug, Jinja2 |

**Endpoints:**

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Render web interface |
| `/upload` | POST | Accept file upload, return parsed content |
| `/download/<filename>` | GET | Download saved output file |
| `/list-outputs` | GET | List all saved outputs |
| `/delete/<filename>` | DELETE | Remove specific output file |
| `/clear-all` | POST | Remove all output files |

**Design Decisions:**
- Synchronous request handling (appropriate for single-user operation)
- Temporary file storage for uploads (cleaned after processing)
- Server-side rendering for simplicity

#### 2.2.2 CLI Application Component

| Attribute | Value |
|-----------|-------|
| Technology | Python argparse |
| Responsibility | Command-line interaction, script integration |
| Dependencies | API Wrapper |

**Commands:**

```
file-parser-cli <file_path> [--format json|markdown]
file-parser-cli --interactive
  > parse <file_path> [format]
  > chat <message>
  > help
  > quit
```

#### 2.2.3 MCP Server Component

| Attribute | Value |
|-----------|-------|
| Technology | mcp library (Anthropic) |
| Responsibility | Claude Desktop integration via MCP protocol |
| Dependencies | Parsing Engine, Vision Service |

**Registered Tools:**

| Tool Name | Input | Output |
|-----------|-------|--------|
| `parse_document` | file_path/content, filename, enable_ai_vision | Parsed JSON |
| `analyze_image` | image_path/content, format, type, context | Analysis JSON |
| `format_output` | parsed_data, format, include_toc, pretty_print | Formatted string |
| `save_output` | content, filename, format | Confirmation |
| `extract_tables` | file_path/content, filename, output_format | Table data |
| `list_outputs` | - | File list |
| `read_output` | filename | File content |
| `delete_output` | filename | Confirmation |

#### 2.2.4 API Wrapper Component

| Attribute | Value |
|-----------|-------|
| Technology | Python class |
| Responsibility | Unified interface for all parsing operations |
| Dependencies | Anthropic SDK |

**Class: FileParserAgent**

```python
class FileParserAgent:
    """Primary API for document parsing operations."""
    
    def __init__(self, api_key: str = None):
        """Initialize with optional API key for AI features."""
    
    def parse_file(self, file_path: str, output_format: str = "json", 
                   enable_ai_vision: bool = True) -> dict:
        """Direct file parsing without conversation."""
    
    def chat(self, message: str, file_path: str = None) -> str:
        """Conversational interface with tool-use support."""
    
    def get_tools(self) -> list:
        """Return tool definitions for Claude API."""
    
    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a specific tool with given parameters."""
```

#### 2.2.5 Parsing Engine Component

| Attribute | Value |
|-----------|-------|
| Technology | PyPDF2, python-docx, openpyxl, python-pptx |
| Responsibility | Document format-specific content extraction |
| Dependencies | Pillow (for image handling) |

**Parser Hierarchy:**

```
┌─────────────────────────────────────────┐
│         BaseDocumentParser              │
│  ┌──────────────────────────────────┐   │
│  │  + parse(file_path) -> dict      │   │
│  │  + extract_metadata() -> dict    │   │
│  │  + get_supported_extensions()    │   │
│  └──────────────────────────────────┘   │
└───────────────────┬─────────────────────┘
                    │
    ┌───────────────┼───────────────┬───────────────┐
    │               │               │               │
    ▼               ▼               ▼               ▼
┌────────┐    ┌──────────┐   ┌──────────┐   ┌──────────────┐
│PDFParser│   │WordParser│   │ExcelParser│  │PowerPointParser│
└────────┘    └──────────┘   └──────────┘   └──────────────┘
```

**Parser Selection Logic:**

```python
PARSER_REGISTRY = {
    '.pdf': PDFParser,
    '.docx': WordParser,
    '.doc': WordParser,
    '.xlsx': ExcelParser,
    '.xls': ExcelParser,
    '.pptx': PowerPointParser,
    '.ppt': PowerPointParser,
}

def get_parser(filename: str) -> BaseDocumentParser:
    ext = Path(filename).suffix.lower()
    parser_class = PARSER_REGISTRY.get(ext)
    if not parser_class:
        raise UnsupportedFormatError(f"Unsupported format: {ext}")
    return parser_class()
```

#### 2.2.6 Vision Service Component

| Attribute | Value |
|-----------|-------|
| Technology | Anthropic Claude API (Vision) |
| Responsibility | AI-powered image and chart analysis |
| Dependencies | Anthropic SDK, Pillow |

**Capabilities:**

| Analysis Type | Description | Use Case |
|---------------|-------------|----------|
| `general` | Overall image description | Photos, diagrams |
| `chart` | Data visualization analysis | Bar charts, pie charts |
| `diagram` | Technical diagram analysis | Flowcharts, architecture |

**Image Processing Pipeline:**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Extract   │───▶│   Validate  │───▶│  Compress   │───▶│   Encode    │
│   Image     │    │   Format    │    │   if > 5MB  │    │   Base64    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Return    │◀───│   Parse     │◀───│   Claude    │◀───│   Build     │
│   Analysis  │    │   Response  │    │   API Call  │    │   Request   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

#### 2.2.7 Output Manager Component

| Attribute | Value |
|-----------|-------|
| Technology | Python standard library |
| Responsibility | Format conversion and file persistence |
| Dependencies | None |

**Formatters:**

| Format | Implementation | Output |
|--------|----------------|--------|
| JSON | `json.dumps()` with indentation | `.json` file |
| Markdown | Custom renderer | `.md` file |
| CSV | `csv` module | `.csv` file |
| Text | Plain extraction | `.txt` file |

**File Naming Convention:**

```
{original_name}_{timestamp}.{extension}
Example: quarterly_report_20260204_143022.json
```

---

## 3. Integration Patterns

### 3.1 Interface Integration Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          INTEGRATION PATTERNS                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┬─────────────────┬──────────────────┬─────────────────────────────┐
│  Interface  │    Protocol     │   Data Format    │        Use Case             │
├─────────────┼─────────────────┼──────────────────┼─────────────────────────────┤
│  Web UI     │  HTTP/HTTPS     │  multipart/form  │  Interactive browser use    │
│             │                 │  JSON response   │                             │
├─────────────┼─────────────────┼──────────────────┼─────────────────────────────┤
│  CLI        │  stdio          │  Text/JSON       │  Script automation          │
│             │                 │                  │  DevOps pipelines           │
├─────────────┼─────────────────┼──────────────────┼─────────────────────────────┤
│  Python API │  Function call  │  Python dict     │  Application integration    │
│             │                 │  Tool-use JSON   │  Custom workflows           │
├─────────────┼─────────────────┼──────────────────┼─────────────────────────────┤
│  MCP Server │  JSON-RPC       │  MCP Tool format │  Claude Desktop             │
│             │  over stdio     │                  │  AI assistant integration   │
└─────────────┴─────────────────┴──────────────────┴─────────────────────────────┘
```

### 3.2 Web Interface Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Browser │     │    Flask     │     │   Parsing    │     │   Storage    │
│          │     │    Server    │     │   Engine     │     │              │
└────┬─────┘     └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
     │                  │                    │                    │
     │  POST /upload    │                    │                    │
     │  (multipart)     │                    │                    │
     │─────────────────▶│                    │                    │
     │                  │                    │                    │
     │                  │  Save to temp      │                    │
     │                  │─────────────────────────────────────────▶
     │                  │                    │                    │
     │                  │  parse(file_path)  │                    │
     │                  │───────────────────▶│                    │
     │                  │                    │                    │
     │                  │   parsed_data      │                    │
     │                  │◀───────────────────│                    │
     │                  │                    │                    │
     │                  │  Delete temp file  │                    │
     │                  │─────────────────────────────────────────▶
     │                  │                    │                    │
     │                  │  Save output       │                    │
     │                  │─────────────────────────────────────────▶
     │                  │                    │                    │
     │  JSON Response   │                    │                    │
     │◀─────────────────│                    │                    │
     │                  │                    │                    │
```

### 3.3 MCP Integration Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Claude    │     │  MCP Server  │     │   Parsing    │     │   Vision     │
│   Desktop    │     │              │     │   Engine     │     │   Service    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │                    │
       │  tools/list        │                    │                    │
       │───────────────────▶│                    │                    │
       │                    │                    │                    │
       │  [tool_list]       │                    │                    │
       │◀───────────────────│                    │                    │
       │                    │                    │                    │
       │  tools/call        │                    │                    │
       │  parse_document    │                    │                    │
       │───────────────────▶│                    │                    │
       │                    │                    │                    │
       │                    │  parse(file)       │                    │
       │                    │───────────────────▶│                    │
       │                    │                    │                    │
       │                    │  [has_images]      │                    │
       │                    │◀───────────────────│                    │
       │                    │                    │                    │
       │                    │  analyze(images)   │                    │
       │                    │────────────────────────────────────────▶│
       │                    │                    │                    │
       │                    │  [descriptions]    │                    │
       │                    │◀────────────────────────────────────────│
       │                    │                    │                    │
       │  [tool_result]     │                    │                    │
       │◀───────────────────│                    │                    │
       │                    │                    │                    │
```

### 3.4 Python API Integration

```python
# Direct usage
from file_parser_agent import FileParserAgent

agent = FileParserAgent(api_key="sk-...")
result = agent.parse_file("document.pdf", output_format="json")

# Tool-use integration with Claude
from anthropic import Anthropic

client = Anthropic()
agent = FileParserAgent()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    tools=agent.get_tools(),
    messages=[{"role": "user", "content": "Parse this document..."}]
)

# Handle tool use
for block in response.content:
    if block.type == "tool_use":
        result = agent.execute_tool(block.name, block.input)
```

### 3.5 Error Handling Strategy

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          ERROR HANDLING HIERARCHY                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  FileParserError (base)                                                         │
│  ├── UnsupportedFormatError     - Unrecognized file extension                   │
│  ├── FileSizeError              - Exceeds 50MB limit                            │
│  ├── ParseError                 - Document parsing failure                      │
│  │   ├── CorruptedFileError     - Invalid file structure                        │
│  │   └── EncodingError          - Character encoding issues                     │
│  ├── VisionError                - AI vision service failure                     │
│  │   ├── APIKeyError            - Missing/invalid API key                       │
│  │   ├── RateLimitError         - API rate limit exceeded                       │
│  │   └── ImageError             - Image processing failure                      │
│  └── OutputError                - Output generation/storage failure             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Error Response Format:**

```json
{
  "success": false,
  "error": {
    "type": "ParseError",
    "message": "Unable to extract text from PDF",
    "details": "File may be scanned or image-based",
    "recoverable": false
  }
}
```

---

## 4. Data Architecture

### 4.1 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                           │
└─────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │           INPUT DOCUMENTS           │
                    │  PDF | DOCX | XLSX | PPTX          │
                    │         (Max 50MB)                 │
                    └───────────────┬─────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │         FILE VALIDATION             │
                    │  • Extension check                  │
                    │  • Size validation                  │
                    │  • Filename sanitization            │
                    └───────────────┬─────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
    ┌───────────────────────────┐   ┌───────────────────────────┐
    │     TEXT EXTRACTION       │   │     IMAGE EXTRACTION      │
    │  • Page/slide content     │   │  • Embedded images        │
    │  • Table data             │   │  • Charts/graphs          │
    │  • Metadata               │   │  • Shapes with images     │
    └─────────────┬─────────────┘   └─────────────┬─────────────┘
                  │                               │
                  │                               ▼
                  │               ┌───────────────────────────┐
                  │               │     AI VISION ANALYSIS    │
                  │               │  • Image compression      │
                  │               │  • Base64 encoding        │
                  │               │  • Claude API call        │
                  │               │  • Description extraction │
                  │               └─────────────┬─────────────┘
                  │                             │
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │    STRUCTURED OUTPUT      │
                    │  • JSON object            │
                    │  • Markdown document      │
                    │  • CSV tables             │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
    ┌───────────────────────────┐   ┌───────────────────────────┐
    │     API RESPONSE          │   │     FILE STORAGE          │
    │  • Return to caller       │   │  • outputs/ directory     │
    │  • Stream to client       │   │  • Timestamped names      │
    └───────────────────────────┘   └───────────────────────────┘
```

### 4.2 Data Models

#### 4.2.1 Core Document Model

```python
@dataclass
class ParsedDocument:
    """Base model for all parsed documents."""
    filename: str
    file_type: str
    parsed_at: datetime
    metadata: DocumentMetadata
    content: DocumentContent
    ai_vision_enabled: bool = False

@dataclass
class DocumentMetadata:
    """Document metadata extracted from file properties."""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    custom: Dict[str, Any] = field(default_factory=dict)
```

#### 4.2.2 Format-Specific Models

**PDF Model:**
```python
@dataclass
class PDFDocument(ParsedDocument):
    total_pages: int
    pages: List[PDFPage]

@dataclass
class PDFPage:
    page_number: int
    text: str
    char_count: int
```

**Word Model:**
```python
@dataclass
class WordDocument(ParsedDocument):
    total_paragraphs: int
    total_tables: int
    image_count: int
    embedded_object_count: int
    paragraphs: List[WordParagraph]
    tables: List[WordTable]

@dataclass
class WordParagraph:
    text: str
    style: Optional[str]
    has_embedded_objects: bool

@dataclass
class WordTable:
    table_number: int
    rows: int
    columns: int
    data: List[List[str]]
```

**Excel Model:**
```python
@dataclass
class ExcelDocument(ParsedDocument):
    sheets: List[ExcelSheet]

@dataclass
class ExcelSheet:
    name: str
    rows: int
    columns: int
    data: List[List[Any]]
```

**PowerPoint Model:**
```python
@dataclass
class PowerPointDocument(ParsedDocument):
    slide_width: int
    slide_height: int
    slides: List[PowerPointSlide]

@dataclass
class PowerPointSlide:
    slide_number: int
    title: Optional[str]
    text: str
    notes: Optional[str]
    image_count: int
    chart_count: int
    shapes: List[SlideShape]

@dataclass
class SlideShape:
    type: str  # image, chart, table, text, group
    content_type: Optional[str]
    has_text: bool
    text: Optional[str]
    description: Optional[str]  # For images/charts
    ai_analysis: Optional[Dict[str, Any]]
```

### 4.3 Storage Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FILE SYSTEM LAYOUT                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

file-parser-agent/
├── uploads/                    # Temporary upload storage
│   └── .gitkeep               # (files deleted after processing)
│
├── outputs/                    # Persistent output storage
│   ├── report_20260204_143022.json
│   ├── presentation_20260204_150045.md
│   └── data_20260204_152130.csv
│
├── logs/                       # Application logs
│   └── parser.log
│
└── temp/                       # Temporary processing files
    └── .gitkeep               # (auto-cleaned)
```

**Storage Policies:**

| Location | Retention | Cleanup Trigger |
|----------|-----------|-----------------|
| `uploads/` | 0 (immediate) | After parse completion |
| `outputs/` | Indefinite | Manual deletion or `clear-all` |
| `temp/` | Session | On process exit |
| `logs/` | 7 days | Log rotation |

### 4.4 Data Validation Rules

| Field | Rule | Error |
|-------|------|-------|
| File size | ≤ 50MB | `FileSizeError` |
| File extension | In supported list | `UnsupportedFormatError` |
| Filename | Alphanumeric + `._-` | Sanitized |
| Image size | ≤ 5MB for API | Auto-compressed |
| Output format | `json\|markdown\|csv\|txt` | Default to JSON |

---

## 5. Scalability Design

### 5.1 Current Scale Characteristics

The File Parser Agent is designed as a **single-user, single-instance** application with the following baseline characteristics:

| Metric | Current Design | Limit |
|--------|----------------|-------|
| Concurrent users | 1 | Single process |
| File size | Up to 50MB | Memory constraint |
| Processing time | Variable | No timeout |
| Storage | Local filesystem | Disk space |

### 5.2 Horizontal Scaling Strategy

While not required for current scope, the architecture supports future horizontal scaling:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    FUTURE HORIZONTAL SCALING ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────────┐
                         │     Load Balancer       │
                         │       (nginx)           │
                         └───────────┬─────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │  Parser Node 1  │    │  Parser Node 2  │    │  Parser Node N  │
    │   (Stateless)   │    │   (Stateless)   │    │   (Stateless)   │
    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │   Shared Storage    │
                         │  (S3 / MinIO / NFS) │
                         └─────────────────────┘
```

**Scaling Considerations:**

| Component | Scaling Approach |
|-----------|------------------|
| Web Server | Multiple Flask instances behind load balancer |
| File Storage | Shared object storage (S3-compatible) |
| Vision API | Rate limiting per instance |
| MCP Server | One instance per Claude Desktop connection |

### 5.3 Vertical Scaling Factors

| Resource | Impact | Optimization |
|----------|--------|--------------|
| Memory | Large file processing | Stream processing for PDFs |
| CPU | PDF/PPTX parsing | Parallel page processing |
| Disk I/O | Temporary files | SSD storage, tmpfs for temp |
| Network | Vision API calls | Request batching |

### 5.4 Resource Estimation

**Memory Requirements:**

```
Base application:        ~50MB
Per PDF page:           ~2-5MB
Per PPTX slide:         ~5-10MB (with images)
Per Excel sheet:        ~1-2MB per 10K cells
Image processing:       ~20-50MB per large image

Recommended minimum:    512MB
Recommended for 50MB files: 2GB
```

**Processing Time Estimates:**

| File Type | Size | Expected Time |
|-----------|------|---------------|
| PDF | 10 pages | 2-5 seconds |
| DOCX | 50 pages | 3-8 seconds |
| XLSX | 10 sheets, 10K rows | 5-15 seconds |
| PPTX | 30 slides | 5-10 seconds |
| PPTX with AI vision | 30 slides, 10 images | 30-60 seconds |

---

## 6. Performance Considerations

### 6.1 Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Parse latency (10MB PDF) | < 10 seconds | End-to-end |
| Parse latency (10MB PPTX) | < 15 seconds | Without AI |
| AI vision latency | < 5 seconds | Per image |
| Memory usage | < 2GB | Peak |
| API response time | < 30 seconds | 95th percentile |

### 6.2 Performance Optimization Strategies

#### 6.2.1 Document Processing Optimizations

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       PARSING OPTIMIZATION PIPELINE                              │
└─────────────────────────────────────────────────────────────────────────────────┘

1. LAZY LOADING
   ┌────────────────────────────────────────────────────────────────┐
   │  • Load document structure first                               │
   │  • Extract content on-demand for large files                   │
   │  • Stream pages/slides for memory efficiency                   │
   └────────────────────────────────────────────────────────────────┘

2. PARALLEL PROCESSING (Future)
   ┌────────────────────────────────────────────────────────────────┐
   │  • Process independent pages/slides concurrently               │
   │  • Batch image extraction                                      │
   │  • Parallel AI vision requests                                 │
   └────────────────────────────────────────────────────────────────┘

3. CACHING
   ┌────────────────────────────────────────────────────────────────┐
   │  • Cache parsed structures for re-formatting                   │
   │  • Cache AI descriptions for identical images                  │
   │  • Memory-mapped file access for large documents               │
   └────────────────────────────────────────────────────────────────┘
```

#### 6.2.2 AI Vision Optimizations

| Optimization | Implementation | Impact |
|--------------|----------------|--------|
| Image compression | Pillow JPEG 85% quality | Reduce API payload |
| Batch requests | Group images from same slide | Reduce API calls |
| Early termination | Skip if no images | Avoid unnecessary work |
| Async processing | Parallel image analysis | Reduce total time |

**Image Compression Logic:**

```python
def compress_image_for_api(image_bytes: bytes, max_size: int = 5_000_000) -> bytes:
    """Compress image to meet API size limits."""
    if len(image_bytes) <= max_size:
        return image_bytes
    
    img = Image.open(BytesIO(image_bytes))
    quality = 85
    
    while quality > 20:
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        if buffer.tell() <= max_size:
            return buffer.getvalue()
        quality -= 10
    
    # Resize if compression insufficient
    scale = 0.8
    while scale > 0.2:
        new_size = (int(img.width * scale), int(img.height * scale))
        resized = img.resize(new_size, Image.LANCZOS)
        buffer = BytesIO()
        resized.save(buffer, format='JPEG', quality=60)
        if buffer.tell() <= max_size:
            return buffer.getvalue()
        scale -= 0.1
    
    raise ImageError("Unable to compress image to acceptable size")
```

### 6.3 Bottleneck Analysis

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           BOTTLENECK IDENTIFICATION                              │
└─────────────────────────────────────────────────────────────────────────────────┘

Priority 1: AI Vision API
├── Latency: 2-5 seconds per image
├── Impact: Dominates total processing time
├── Mitigation: Batch processing, optional disable
└── Monitoring: Track API response times

Priority 2: Large File Memory
├── Latency: Memory allocation for 50MB files
├── Impact: Can cause OOM on constrained systems
├── Mitigation: Streaming, temp file processing
└── Monitoring: Peak memory usage

Priority 3: Complex Documents
├── Latency: Nested tables, many images
├── Impact: Exponential parsing time
├── Mitigation: Depth limits, early termination
└── Monitoring: Parse time per element type

Priority 4: Disk I/O
├── Latency: Temp file operations
├── Impact: Noticeable on slow storage
├── Mitigation: tmpfs, SSD
└── Monitoring: I/O wait time
```

### 6.4 Performance Monitoring Points

| Metric | Collection Point | Alert Threshold |
|--------|------------------|-----------------|
| Parse duration | End of parse() | > 60 seconds |
| Memory usage | Process level | > 2GB |
| API latency | Vision service | > 10 seconds |
| Error rate | All operations | > 5% |
| File queue depth | Upload handler | > 10 files |

---

## 7. Technology Decisions

### 7.1 Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TECHNOLOGY STACK                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Flask 3.0+          │ Web framework - lightweight, Python-native               │
│  Jinja2              │ Templating - included with Flask                         │
│  HTML/CSS/JS         │ Simple frontend - no framework needed                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Python 3.8+         │ Runtime - mature, extensive library ecosystem            │
│  argparse            │ CLI - standard library, no dependencies                  │
│  mcp                 │ MCP protocol - Anthropic's official library              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  PARSING LAYER                                                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  PyPDF2 3.0+         │ PDF parsing - pure Python, well-maintained               │
│  python-docx 1.1+    │ Word parsing - official Microsoft format support         │
│  openpyxl 3.1+       │ Excel parsing - full xlsx support                        │
│  python-pptx 0.6+    │ PowerPoint parsing - comprehensive slide access          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  AI/ML LAYER                                                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  anthropic 0.77+     │ Claude API client - official SDK                         │
│  Pillow 10.2+        │ Image processing - compression, format conversion        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Local filesystem    │ Storage - simple, no additional services                 │
│  Environment vars    │ Configuration - standard, secure                         │
│  python-dotenv       │ Local config - .env file support                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Technology Decision Records

#### TDR-001: Web Framework Selection

| Aspect | Decision |
|--------|----------|
| **Context** | Need web interface for file upload and result display |
| **Decision** | Flask 3.0+ |
| **Rationale** | Lightweight, Python-native, sufficient for single-user tool |
| **Alternatives** | FastAPI (async overkill), Django (too heavy), Streamlit (less control) |
| **Consequences** | Simple deployment, no async complexity, manual scaling if needed |

#### TDR-002: PDF Library Selection

| Aspect | Decision |
|--------|----------|
| **Context** | Need to extract text from PDF files |
| **Decision** | PyPDF2 |
| **Rationale** | Pure Python, active maintenance, handles most PDF types |
| **Alternatives** | pdfplumber (heavier), pdfminer (complex), PyMuPDF (native deps) |
| **Consequences** | No OCR support, some complex PDFs may not parse fully |

#### TDR-003: AI Vision Provider

| Aspect | Decision |
|--------|----------|
| **Context** | Need AI-powered image and chart analysis |
| **Decision** | Anthropic Claude API (Vision) |
| **Rationale** | High-quality analysis, consistent with MCP integration |
| **Alternatives** | OpenAI GPT-4V, Google Gemini, local models |
| **Consequences** | API cost per image, requires API key, network dependency |

#### TDR-004: Storage Strategy

| Aspect | Decision |
|--------|----------|
| **Context** | Need to store parsed outputs |
| **Decision** | Local filesystem |
| **Rationale** | Simple, no additional services, appropriate for single-user |
| **Alternatives** | SQLite (schema overhead), S3 (external dependency) |
| **Consequences** | Not suitable for multi-node, manual backup needed |

### 7.3 Dependency Version Matrix

| Package | Minimum | Recommended | Notes |
|---------|---------|-------------|-------|
| Python | 3.8 | 3.11+ | Performance improvements |
| Flask | 3.0.0 | 3.0.x | Stable release |
| PyPDF2 | 3.0.1 | 3.x | Breaking changes in 3.0 |
| python-docx | 1.1.0 | 1.x | Stable API |
| openpyxl | 3.1.2 | 3.x | XLSX support |
| python-pptx | 0.6.23 | 0.6.x | Limited maintenance |
| anthropic | 0.77.1 | Latest | Frequent updates |
| Pillow | 10.2.0 | 10.x | Security updates |
| mcp | 1.0.0 | Latest | Protocol changes |

### 7.4 Future Technology Considerations

| Capability | Current Gap | Potential Technology |
|------------|-------------|---------------------|
| OCR | Scanned PDFs | Tesseract, Azure Form Recognizer |
| Batch Processing | Queue management | Celery, Redis |
| Multi-user | Authentication | Flask-Login, OAuth |
| Cloud Storage | Scalable storage | boto3, Azure Blob |
| Async Processing | Long-running tasks | FastAPI, asyncio |

---

## 8. Architecture Diagrams

### 8.1 C4 Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           C4 CONTEXT DIAGRAM                                     │
│                        (System Context - Level 1)                                │
└─────────────────────────────────────────────────────────────────────────────────┘

                                   ┌─────────────┐
                                   │             │
                                   │  Developer  │
                                   │             │
                                   └──────┬──────┘
                                          │
                    Uses Python API/CLI   │
                    to integrate parsing  │
                                          │
    ┌─────────────┐                       │                      ┌─────────────┐
    │             │                       │                      │             │
    │   Analyst   │                       │                      │  Claude     │
    │             │                       │                      │  Desktop    │
    └──────┬──────┘                       │                      └──────┬──────┘
           │                              │                             │
           │ Uploads documents            │                             │ Connects via
           │ via web browser              │                             │ MCP protocol
           │                              ▼                             │
           │              ┌───────────────────────────────┐             │
           └─────────────▶│                               │◀────────────┘
                          │     FILE PARSER AGENT         │
                          │                               │
                          │  • Extracts text from docs    │
                          │  • Detects tables and images  │
                          │  • Generates structured output│
                          │  • AI-powered image analysis  │
                          │                               │
                          └───────────────┬───────────────┘
                                          │
                                          │ Sends images for
                                          │ AI analysis
                                          │
                                          ▼
                          ┌───────────────────────────────┐
                          │                               │
                          │    ANTHROPIC CLAUDE API       │
                          │                               │
                          │  External AI service for      │
                          │  image understanding          │
                          │                               │
                          └───────────────────────────────┘
```

### 8.2 C4 Container Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           C4 CONTAINER DIAGRAM                                   │
│                          (Containers - Level 2)                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FILE PARSER AGENT                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                    │
│   │                │  │                │  │                │                    │
│   │  Web App       │  │  CLI           │  │  MCP Server    │                    │
│   │  [Flask]       │  │  [Python]      │  │  [mcp lib]     │                    │
│   │                │  │                │  │                │                    │
│   │  Handles HTTP  │  │  Command-line  │  │  Claude        │                    │
│   │  file upload   │  │  interface     │  │  Desktop       │                    │
│   │  and display   │  │  for scripts   │  │  integration   │                    │
│   │                │  │                │  │                │                    │
│   └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                    │
│           │                   │                   │                             │
│           │        HTTP       │      Import       │      JSON-RPC               │
│           │                   │                   │                             │
│           └───────────────────┼───────────────────┘                             │
│                               │                                                 │
│                               ▼                                                 │
│                   ┌───────────────────────────┐                                 │
│                   │                           │                                 │
│                   │   API Wrapper             │                                 │
│                   │   [FileParserAgent]       │                                 │
│                   │                           │                                 │
│                   │   Unified interface       │                                 │
│                   │   for all parsing         │                                 │
│                   │   operations              │                                 │
│                   │                           │                                 │
│                   └─────────────┬─────────────┘                                 │
│                                 │                                               │
│           ┌─────────────────────┼─────────────────────┐                         │
│           │                     │                     │                         │
│           ▼                     ▼                     ▼                         │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐                  │
│   │               │    │               │    │               │                  │
│   │ Parsing       │    │ Vision        │    │ Output        │                  │
│   │ Engine        │    │ Service       │    │ Manager       │                  │
│   │               │    │               │    │               │                  │
│   │ Format-       │    │ AI image      │    │ Format        │                  │
│   │ specific      │    │ analysis      │    │ conversion    │                  │
│   │ parsers       │    │               │    │ and storage   │                  │
│   │               │    │               │    │               │                  │
│   └───────────────┘    └───────┬───────┘    └───────┬───────┘                  │
│                                │                    │                          │
└────────────────────────────────┼────────────────────┼──────────────────────────┘
                                 │                    │
                                 │ HTTPS              │ File I/O
                                 ▼                    ▼
                   ┌────────────────────┐  ┌────────────────────┐
                   │  Anthropic API     │  │  File System       │
                   │  [External]        │  │  [Local Storage]   │
                   └────────────────────┘  └────────────────────┘
```

### 8.3 C4 Component Diagram - Parsing Engine

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           C4 COMPONENT DIAGRAM                                   │
│                    (Parsing Engine Components - Level 3)                         │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PARSING ENGINE                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                       ┌───────────────────────────┐                             │
│                       │                           │                             │
│                       │    Parser Factory         │                             │
│                       │                           │                             │
│                       │    Routes files to        │                             │
│                       │    appropriate parser     │                             │
│                       │                           │                             │
│                       └─────────────┬─────────────┘                             │
│                                     │                                           │
│           ┌─────────────┬───────────┼───────────┬─────────────┐                │
│           │             │           │           │             │                │
│           ▼             ▼           ▼           ▼             ▼                │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│   │             │ │             │ │             │ │             │              │
│   │ PDF Parser  │ │ Word Parser │ │Excel Parser │ │ PPTX Parser │              │
│   │             │ │             │ │             │ │             │              │
│   │ [PyPDF2]    │ │[python-docx]│ │ [openpyxl]  │ │[python-pptx]│              │
│   │             │ │             │ │             │ │             │              │
│   │ • Pages     │ │ • Paragraphs│ │ • Sheets    │ │ • Slides    │              │
│   │ • Text      │ │ • Tables    │ │ • Cells     │ │ • Shapes    │              │
│   │ • Metadata  │ │ • Images    │ │ • Formulas  │ │ • Images    │              │
│   │             │ │ • Styles    │ │             │ │ • Charts    │              │
│   │             │ │ • OLE       │ │             │ │ • Notes     │              │
│   │             │ │             │ │             │ │             │              │
│   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘              │
│          │               │               │               │                      │
│          └───────────────┴───────────────┴───────────────┘                      │
│                                  │                                              │
│                                  ▼                                              │
│                   ┌───────────────────────────┐                                 │
│                   │                           │                                 │
│                   │  Metadata Extractor       │                                 │
│                   │                           │                                 │
│                   │  Common metadata          │                                 │
│                   │  extraction logic         │                                 │
│                   │                           │                                 │
│                   └───────────────────────────┘                                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 8.4 Deployment Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DEPLOYMENT DIAGRAM                                     │
│                        (Single-Node Deployment)                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           HOST MACHINE                                           │
│                    (Windows / macOS / Linux)                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                      PYTHON VIRTUAL ENVIRONMENT                          │   │
│   │                           (venv / conda)                                 │   │
│   ├─────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                          │   │
│   │   ┌────────────────────┐                    ┌────────────────────┐      │   │
│   │   │                    │                    │                    │      │   │
│   │   │   Flask App        │                    │   MCP Server       │      │   │
│   │   │   (port 5000)      │                    │   (stdio)          │      │   │
│   │   │                    │                    │                    │      │   │
│   │   │   python app.py    │                    │   python mcp_      │      │   │
│   │   │                    │                    │   server.py        │      │   │
│   │   │                    │                    │                    │      │   │
│   │   └─────────┬──────────┘                    └─────────┬──────────┘      │   │
│   │             │                                         │                 │   │
│   │             │                                         │                 │   │
│   │   ┌─────────▼──────────────────────────────────────────▼─────────┐      │   │
│   │   │                                                              │      │   │
│   │   │                    Shared Libraries                          │      │   │
│   │   │                                                              │      │   │
│   │   │   PyPDF2 │ python-docx │ openpyxl │ python-pptx │ Pillow    │      │   │
│   │   │                                                              │      │   │
│   │   └──────────────────────────────────────────────────────────────┘      │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                         FILE SYSTEM                                      │   │
│   ├─────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                          │   │
│   │   /app                     Application code                              │   │
│   │   /app/uploads             Temporary uploads (auto-cleaned)              │   │
│   │   /app/outputs             Persistent output storage                     │   │
│   │   /app/.env                Environment configuration                     │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                    │
                    │  HTTPS (443)
                    ▼
         ┌─────────────────────┐
         │                     │
         │  Anthropic API      │
         │  api.anthropic.com  │
         │                     │
         └─────────────────────┘
```

### 8.5 Sequence Diagram - Document Parsing Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SEQUENCE DIAGRAM                                         │
│                    (Parse Document with AI Vision)                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌───────┐  ┌───────────┐  ┌─────────────┐  ┌───────────┐  ┌─────────┐  ┌─────────┐
│ User  │  │  Web App  │  │ API Wrapper │  │  Parser   │  │ Vision  │  │ Output  │
└───┬───┘  └─────┬─────┘  └──────┬──────┘  └─────┬─────┘  └────┬────┘  └────┬────┘
    │            │               │               │              │            │
    │  Upload    │               │               │              │            │
    │  PPTX      │               │               │              │            │
    │───────────▶│               │               │              │            │
    │            │               │               │              │            │
    │            │  Save temp    │               │              │            │
    │            │─────────────────────────────────────────────────────────────▶
    │            │               │               │              │            │
    │            │  parse_file() │               │              │            │
    │            │──────────────▶│               │              │            │
    │            │               │               │              │            │
    │            │               │  get_parser() │              │            │
    │            │               │──────────────▶│              │            │
    │            │               │               │              │            │
    │            │               │  PPTXParser   │              │            │
    │            │               │◀──────────────│              │            │
    │            │               │               │              │            │
    │            │               │  parse()      │              │            │
    │            │               │──────────────▶│              │            │
    │            │               │               │              │            │
    │            │               │               │  Extract     │            │
    │            │               │               │  slides      │            │
    │            │               │               │──────┐       │            │
    │            │               │               │      │       │            │
    │            │               │               │◀─────┘       │            │
    │            │               │               │              │            │
    │            │               │               │  Extract     │            │
    │            │               │               │  images      │            │
    │            │               │               │──────┐       │            │
    │            │               │               │      │       │            │
    │            │               │               │◀─────┘       │            │
    │            │               │               │              │            │
    │            │               │  slides +     │              │            │
    │            │               │  images       │              │            │
    │            │               │◀──────────────│              │            │
    │            │               │               │              │            │
    │            │               │            analyze_images()  │            │
    │            │               │─────────────────────────────▶│            │
    │            │               │               │              │            │
    │            │               │               │              │ Claude     │
    │            │               │               │              │ API call   │
    │            │               │               │              │────────┐   │
    │            │               │               │              │        │   │
    │            │               │               │              │◀───────┘   │
    │            │               │               │              │            │
    │            │               │            descriptions      │            │
    │            │               │◀─────────────────────────────│            │
    │            │               │               │              │            │
    │            │               │         format_output()      │            │
    │            │               │───────────────────────────────────────────▶
    │            │               │               │              │            │
    │            │               │         JSON/Markdown        │            │
    │            │               │◀───────────────────────────────────────────
    │            │               │               │              │            │
    │            │  parsed_data  │               │              │            │
    │            │◀──────────────│               │              │            │
    │            │               │               │              │            │
    │            │  Delete temp  │               │              │            │
    │            │─────────────────────────────────────────────────────────────▶
    │            │               │               │              │            │
    │  Response  │               │               │              │            │
    │  (JSON)    │               │              │              │            │
    │◀───────────│               │               │              │            │
    │            │               │               │              │            │
```

---

## 9. Security Considerations

### 9.1 Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          SECURITY BOUNDARIES                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  TRUST BOUNDARY: External                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  • User file uploads (untrusted)                                        │    │
│  │  • User input parameters (untrusted)                                    │    │
│  │  • External network requests                                            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  INPUT VALIDATION LAYER                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  • File extension whitelist                                             │    │
│  │  • File size limits (50MB)                                              │    │
│  │  • Filename sanitization                                                │    │
│  │  • Path traversal prevention                                            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  TRUST BOUNDARY: Application                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  • Parsing libraries (trusted but sandboxed)                            │    │
│  │  • Local file operations (restricted paths)                             │    │
│  │  • Environment variables (API keys)                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  TRUST BOUNDARY: External Services                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  • Anthropic API (TLS encrypted)                                        │    │
│  │  • API key transmission (Authorization header)                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Security Controls

| Threat | Control | Implementation |
|--------|---------|----------------|
| Path traversal | Filename sanitization | `werkzeug.utils.secure_filename()` |
| Malicious files | Extension whitelist | Check against allowed list |
| DoS via large files | Size limits | Check before processing |
| API key exposure | Environment variables | Never log or return |
| Data leakage | Temp file cleanup | Delete after processing |
| Injection attacks | Input validation | Sanitize all user input |

### 9.3 Data Protection

| Data Type | At Rest | In Transit | Retention |
|-----------|---------|------------|-----------|
| Uploaded files | Local filesystem | HTTP (local) | Immediate deletion |
| Parsed output | Local filesystem | HTTP (local) | Until manual deletion |
| Images for AI | Memory only | HTTPS to Anthropic | Not retained |
| API keys | Environment variable | HTTPS header | Session lifetime |

---

## 10. Operational Considerations

### 10.1 Deployment Checklist

```
□ Python 3.8+ installed
□ Virtual environment created
□ Dependencies installed (pip install -r requirements.txt)
□ ANTHROPIC_API_KEY environment variable set
□ uploads/ directory created with write permissions
□ outputs/ directory created with write permissions
□ Port 5000 available (web interface)
```

### 10.2 Configuration Management

**Environment Variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | For AI vision | None | Claude API key |
| `FLASK_ENV` | No | production | Flask environment |
| `UPLOAD_FOLDER` | No | ./uploads | Temp upload path |
| `OUTPUT_FOLDER` | No | ./outputs | Output storage path |
| `MAX_FILE_SIZE` | No | 50MB | Maximum upload size |

### 10.3 Monitoring and Logging

**Log Format:**
```
[{timestamp}] [{level}] [{component}] {message}
[2026-02-04 14:30:22] [INFO] [parser] Parsing document: report.pdf
[2026-02-04 14:30:25] [INFO] [parser] Extracted 12 pages
[2026-02-04 14:30:25] [INFO] [vision] Analyzing 3 images
[2026-02-04 14:30:35] [INFO] [output] Saved: report_20260204_143035.json
```

**Key Metrics:**
- Parse requests per hour
- Average parse duration
- Error rate by file type
- AI vision API usage
- Storage utilization

### 10.4 Backup and Recovery

| Component | Backup Strategy | Recovery |
|-----------|-----------------|----------|
| Application code | Version control (Git) | Clone repository |
| Configuration | .env.example template | Recreate from template |
| Output files | User responsibility | N/A (not critical) |
| Logs | Log rotation (7 days) | N/A (operational only) |

---

## 11. Appendices

### Appendix A: API Reference Summary

**FileParserAgent Class:**

```python
class FileParserAgent:
    def __init__(self, api_key: str = None)
    def parse_file(self, file_path: str, output_format: str = "json", 
                   enable_ai_vision: bool = True) -> dict
    def chat(self, message: str, file_path: str = None) -> str
    def get_tools(self) -> list
    def execute_tool(self, tool_name: str, tool_input: dict) -> str
```

### Appendix B: Output Schema Reference

See Section 5.2 for complete data model definitions.

### Appendix C: Error Code Reference

| Code | Type | Description |
|------|------|-------------|
| E001 | UnsupportedFormat | File extension not in whitelist |
| E002 | FileSizeError | File exceeds 50MB limit |
| E003 | ParseError | Unable to extract content |
| E004 | VisionError | AI analysis failed |
| E005 | OutputError | Unable to save/format output |

### Appendix D: Glossary

| Term | Definition |
|------|------------|
| MCP | Model Context Protocol - Anthropic's protocol for AI tool integration |
| OLE | Object Linking and Embedding - Microsoft's embedded object technology |
| PPTX | PowerPoint Open XML format |
| DOCX | Word Open XML format |
| XLSX | Excel Open XML format |
| Tool-use | Claude API feature for calling external functions |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-04 | Solution Architect | Initial architecture document |