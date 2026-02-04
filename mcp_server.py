"""
File Parser Agent - MCP Server
Model Context Protocol server for document parsing tools.

Run with: python mcp_server.py
Or configure in Claude Desktop's claude_desktop_config.json
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    EmbeddedResource,
    BlobResourceContents,
)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from parsers.pdf_parser import parse_pdf
from parsers.word_parser import parse_word
from parsers.excel_parser import parse_excel
from parsers.pptx_parser import parse_pptx
from parsers.image_analyzer import get_image_description, analyze_chart_image

# Initialize MCP server
server = Server("file-parser-agent")

# Configuration
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)

# File type mappings
EXTENSION_MAP = {
    'pdf': 'pdf',
    'docx': 'word', 'doc': 'word',
    'xlsx': 'excel', 'xls': 'excel',
    'pptx': 'powerpoint', 'ppt': 'powerpoint'
}

PARSER_MAP = {
    'pdf': parse_pdf,
    'word': parse_word,
    'excel': parse_excel,
    'powerpoint': parse_pptx
}


def get_file_type(filename: str) -> str | None:
    """Determine file type from extension."""
    ext = filename.rsplit('.', 1)[-1].lower()
    return EXTENSION_MAP.get(ext)


def save_temp_file(content_b64: str, filename: str) -> Path:
    """Save base64 content to temporary file."""
    filepath = TEMP_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    file_bytes = base64.b64decode(content_b64)
    filepath.write_bytes(file_bytes)
    return filepath


def cleanup_temp_file(filepath: Path):
    """Remove temporary file."""
    try:
        filepath.unlink()
    except Exception:
        pass


def convert_to_markdown(data: dict, include_toc: bool = False) -> str:
    """Convert parsed data to Markdown format."""
    md = []

    md.append(f"# {data.get('filename', 'Parsed Document')}\n")
    md.append(f"**File Type:** {data.get('file_type', 'Unknown')}")
    md.append(f"**Parsed:** {data.get('parsed_at', '')}\n")
    md.append("---\n")

    file_type = data.get('file_type')

    if file_type == 'pdf':
        if include_toc:
            md.append("## Table of Contents\n")
            for page in data.get('pages', []):
                md.append(f"- [Page {page['page_number']}](#page-{page['page_number']})\n")
            md.append("\n---\n")

        for page in data.get('pages', []):
            md.append(f"## Page {page['page_number']}\n")
            md.append(f"{page.get('text', '')}\n")

    elif file_type == 'word':
        md.append("## Document Content\n")
        for para in data.get('paragraphs', []):
            if isinstance(para, dict):
                md.append(f"{para.get('text', '')}\n")
            else:
                md.append(f"{para}\n")

        if data.get('tables'):
            md.append("\n## Tables\n")
            for table in data.get('tables', []):
                md.append(f"### Table {table.get('table_number', '')}\n")
                if table.get('data'):
                    md.append("| " + " | ".join(str(c) for c in table['data'][0]) + " |")
                    md.append("| " + " | ".join("---" for _ in table['data'][0]) + " |")
                    for row in table['data'][1:]:
                        md.append("| " + " | ".join(str(c) for c in row) + " |")
                md.append("\n")

    elif file_type == 'excel':
        for sheet in data.get('sheets', []):
            md.append(f"## Sheet: {sheet['name']}\n")
            if sheet.get('data'):
                md.append("| " + " | ".join(str(c) for c in sheet['data'][0]) + " |")
                md.append("| " + " | ".join("---" for _ in sheet['data'][0]) + " |")
                for row in sheet['data'][1:]:
                    md.append("| " + " | ".join(str(c) for c in row) + " |")
            md.append("\n")

    elif file_type == 'powerpoint':
        if include_toc:
            md.append("## Table of Contents\n")
            for slide in data.get('slides', []):
                title = slide.get('title', f"Slide {slide['slide_number']}")
                md.append(f"- [{title}](#slide-{slide['slide_number']})\n")
            md.append("\n---\n")

        for slide in data.get('slides', []):
            md.append(f"## Slide {slide['slide_number']}")
            if slide.get('title'):
                md.append(f": {slide['title']}")
            md.append("\n")

            if slide.get('text'):
                md.append(f"{slide['text']}\n")

            if slide.get('notes'):
                md.append(f"\n> **Speaker Notes:** {slide['notes']}\n")

            for shape in slide.get('shapes', []):
                if shape.get('content_type') == 'image' and shape.get('description'):
                    md.append(f"\n*[Image: {shape['description']}]*\n")

    return '\n'.join(md)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="parse_document",
            description="Parse a document (PDF, Word, Excel, PowerPoint) and extract structured content. Returns JSON with text, tables, metadata, and detected images/charts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to parse"
                    },
                    "file_content": {
                        "type": "string",
                        "description": "Base64-encoded file content (alternative to file_path)"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename with extension (required if using file_content)"
                    },
                    "enable_ai_vision": {
                        "type": "boolean",
                        "description": "Enable AI image analysis for PowerPoint (default: true)",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="analyze_image",
            description="Analyze an image using AI vision. Returns detailed description of image content, charts, or diagrams.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Absolute path to the image file"
                    },
                    "image_content": {
                        "type": "string",
                        "description": "Base64-encoded image data (alternative to image_path)"
                    },
                    "image_format": {
                        "type": "string",
                        "enum": ["png", "jpg", "jpeg", "gif", "webp"],
                        "description": "Image format (required if using image_content)"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["general", "chart"],
                        "description": "Type of analysis: 'general' for images, 'chart' for data visualizations",
                        "default": "general"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about the image (e.g., 'Slide 3 of quarterly report')"
                    }
                }
            }
        ),
        Tool(
            name="format_output",
            description="Format parsed document data as JSON or Markdown.",
            inputSchema={
                "type": "object",
                "properties": {
                    "parsed_data": {
                        "type": "object",
                        "description": "Parsed document data from parse_document"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "markdown"],
                        "description": "Output format",
                        "default": "json"
                    },
                    "include_toc": {
                        "type": "boolean",
                        "description": "Include table of contents (markdown only)",
                        "default": False
                    },
                    "pretty_print": {
                        "type": "boolean",
                        "description": "Pretty print JSON output",
                        "default": True
                    }
                },
                "required": ["parsed_data"]
            }
        ),
        Tool(
            name="save_output",
            description="Save content to a file in the outputs directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Content to save"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (without path)"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "md", "txt", "csv"],
                        "description": "File format/extension"
                    }
                },
                "required": ["content", "filename", "format"]
            }
        ),
        Tool(
            name="extract_tables",
            description="Extract only table data from a document. Returns tables in structured format.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file"
                    },
                    "file_content": {
                        "type": "string",
                        "description": "Base64-encoded file content (alternative to file_path)"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename with extension (required if using file_content)"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "csv", "markdown"],
                        "description": "Output format for tables",
                        "default": "json"
                    }
                }
            }
        ),
        Tool(
            name="list_outputs",
            description="List all previously saved output files.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="read_output",
            description="Read a previously saved output file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the output file to read"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="delete_output",
            description="Delete a saved output file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the output file to delete"
                    }
                },
                "required": ["filename"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    try:
        if name == "parse_document":
            return await handle_parse_document(arguments)
        elif name == "analyze_image":
            return await handle_analyze_image(arguments)
        elif name == "format_output":
            return await handle_format_output(arguments)
        elif name == "save_output":
            return await handle_save_output(arguments)
        elif name == "extract_tables":
            return await handle_extract_tables(arguments)
        elif name == "list_outputs":
            return await handle_list_outputs(arguments)
        elif name == "read_output":
            return await handle_read_output(arguments)
        elif name == "delete_output":
            return await handle_delete_output(arguments)
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def handle_parse_document(args: dict) -> list[TextContent]:
    """Parse a document file."""
    file_path = args.get("file_path")
    file_content = args.get("file_content")
    filename = args.get("filename")
    enable_ai_vision = args.get("enable_ai_vision", True)

    # Determine file path
    if file_path:
        filepath = Path(file_path)
        if not filepath.exists():
            return [TextContent(type="text", text=json.dumps({"error": f"File not found: {file_path}"}))]
        filename = filepath.name
    elif file_content and filename:
        filepath = save_temp_file(file_content, filename)
    else:
        return [TextContent(type="text", text=json.dumps({"error": "Provide either file_path or both file_content and filename"}))]

    # Get file type and parser
    file_type = get_file_type(filename)
    if not file_type:
        if file_content:
            cleanup_temp_file(filepath)
        return [TextContent(type="text", text=json.dumps({"error": f"Unsupported file type: {filename}"}))]

    parser = PARSER_MAP[file_type]

    try:
        # Parse file
        if file_type == 'powerpoint':
            result = parser(str(filepath), enable_ai_vision=enable_ai_vision)
        else:
            result = parser(str(filepath))

        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    finally:
        if file_content:
            cleanup_temp_file(filepath)


async def handle_analyze_image(args: dict) -> list[TextContent]:
    """Analyze an image with AI vision."""
    image_path = args.get("image_path")
    image_content = args.get("image_content")
    image_format = args.get("image_format")
    analysis_type = args.get("analysis_type", "general")
    context = args.get("context", "")

    # Get image bytes
    if image_path:
        filepath = Path(image_path)
        if not filepath.exists():
            return [TextContent(type="text", text=json.dumps({"error": f"Image not found: {image_path}"}))]
        image_bytes = filepath.read_bytes()
        image_format = filepath.suffix.lstrip('.').lower()
    elif image_content and image_format:
        image_bytes = base64.b64decode(image_content)
    else:
        return [TextContent(type="text", text=json.dumps({"error": "Provide either image_path or both image_content and image_format"}))]

    # Analyze image
    if analysis_type == "chart":
        result = analyze_chart_image(image_bytes, image_format)
    else:
        result = get_image_description(image_bytes, image_format, context)

    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_format_output(args: dict) -> list[TextContent]:
    """Format parsed data as JSON or Markdown."""
    parsed_data = args.get("parsed_data", {})
    output_format = args.get("format", "json")
    include_toc = args.get("include_toc", False)
    pretty_print = args.get("pretty_print", True)

    if output_format == "markdown":
        content = convert_to_markdown(parsed_data, include_toc)
        result = {"format": "markdown", "content": content}
    else:
        if pretty_print:
            content = json.dumps(parsed_data, indent=2, ensure_ascii=False)
        else:
            content = json.dumps(parsed_data, ensure_ascii=False)
        result = {"format": "json", "content": content}

    result["size_bytes"] = len(content.encode('utf-8'))
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_save_output(args: dict) -> list[TextContent]:
    """Save content to output file."""
    content = args.get("content", "")
    filename = args.get("filename", "output")
    file_format = args.get("format", "txt")

    # Sanitize filename
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{safe_filename}_{timestamp}.{file_format}"
    output_path = OUTPUT_DIR / output_filename

    output_path.write_text(content, encoding='utf-8')

    result = {
        "success": True,
        "filename": output_filename,
        "path": str(output_path.absolute()),
        "size_bytes": len(content.encode('utf-8'))
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_extract_tables(args: dict) -> list[TextContent]:
    """Extract tables from a document."""
    # First parse the document
    parse_result = await handle_parse_document(args)
    parsed_text = parse_result[0].text
    parsed_data = json.loads(parsed_text)

    if "error" in parsed_data:
        return parse_result

    tables = []
    file_type = parsed_data.get('file_type')

    if file_type == 'word':
        tables = parsed_data.get('tables', [])
    elif file_type == 'excel':
        for sheet in parsed_data.get('sheets', []):
            tables.append({
                'name': sheet['name'],
                'rows': sheet.get('rows', 0),
                'columns': sheet.get('columns', 0),
                'data': sheet.get('data', [])
            })
    elif file_type == 'powerpoint':
        for slide in parsed_data.get('slides', []):
            for shape in slide.get('shapes', []):
                if shape.get('content_type') == 'table':
                    tables.append({
                        'slide': slide['slide_number'],
                        'rows': shape.get('rows'),
                        'columns': shape.get('columns')
                    })

    output_format = args.get("output_format", "json")

    if output_format == "csv" and tables:
        csv_lines = []
        for table in tables:
            if 'data' in table:
                for row in table['data']:
                    csv_lines.append(','.join(f'"{c}"' for c in row))
                csv_lines.append('')  # Empty line between tables
        result = {"format": "csv", "table_count": len(tables), "content": '\n'.join(csv_lines)}
    elif output_format == "markdown":
        md_lines = []
        for i, table in enumerate(tables):
            md_lines.append(f"### Table {i + 1}: {table.get('name', 'Unnamed')}\n")
            if 'data' in table and table['data']:
                md_lines.append("| " + " | ".join(str(c) for c in table['data'][0]) + " |")
                md_lines.append("| " + " | ".join("---" for _ in table['data'][0]) + " |")
                for row in table['data'][1:]:
                    md_lines.append("| " + " | ".join(str(c) for c in row) + " |")
            md_lines.append("")
        result = {"format": "markdown", "table_count": len(tables), "content": '\n'.join(md_lines)}
    else:
        result = {"format": "json", "table_count": len(tables), "tables": tables}

    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_list_outputs(args: dict) -> list[TextContent]:
    """List output files."""
    files = []
    for filepath in OUTPUT_DIR.iterdir():
        if filepath.is_file():
            stat = filepath.stat()
            files.append({
                "filename": filepath.name,
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    files.sort(key=lambda x: x['modified'], reverse=True)
    result = {"count": len(files), "files": files}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_read_output(args: dict) -> list[TextContent]:
    """Read an output file."""
    filename = args.get("filename", "")
    filepath = OUTPUT_DIR / filename

    if not filepath.exists():
        return [TextContent(type="text", text=json.dumps({"error": f"File not found: {filename}"}))]

    content = filepath.read_text(encoding='utf-8')
    result = {
        "filename": filename,
        "size_bytes": len(content.encode('utf-8')),
        "content": content
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_delete_output(args: dict) -> list[TextContent]:
    """Delete an output file."""
    filename = args.get("filename", "")
    filepath = OUTPUT_DIR / filename

    if not filepath.exists():
        return [TextContent(type="text", text=json.dumps({"error": f"File not found: {filename}"}))]

    filepath.unlink()
    result = {"success": True, "deleted": filename}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    print("Starting File Parser Agent MCP Server...", file=sys.stderr)
    asyncio.run(main())
