#!/usr/bin/env python3
"""
File Parser Agent - MCP Server

Model Context Protocol server for Claude Desktop integration.
Enables Claude to parse documents directly through tool calls.

Usage:
    python mcp_server.py

Configuration (claude_desktop_config.json):
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
"""

import asyncio
import json
import base64
import os
import sys
from typing import Any, Sequence

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Local imports
from core.parser_manager import ParserManager
from core.output_formatter import OutputFormatter
from core.file_manager import FileManager
from core.ai_vision import AIVision


# Initialize components
file_manager = FileManager()
ai_vision = AIVision()

# Create MCP server
if MCP_AVAILABLE:
    server = Server("file-parser-agent")


# =============================================================================
# Tool Definitions
# =============================================================================

TOOLS = [
    {
        "name": "parse_document",
        "description": """Parse a document file and extract structured content.

Supports: PDF, Word (DOCX/DOC), Excel (XLSX/XLS), PowerPoint (PPTX/PPT)

Returns structured data including:
- PDF: Pages with text content, metadata
- Word: Paragraphs, tables, embedded objects, metadata
- Excel: All sheets with cell data
- PowerPoint: Slides with text, shapes, images, charts, notes

Use enable_ai_vision=true for PowerPoint files to get AI descriptions of images.""",
        "inputSchema": {
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
                    "description": "Original filename with extension (required with file_content)"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "json",
                    "description": "Output format"
                },
                "enable_ai_vision": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable AI image analysis for PowerPoint files"
                }
            }
        }
    },
    {
        "name": "analyze_image",
        "description": """Analyze an image using Claude Vision API.

Supports: PNG, JPG, JPEG, GIF, WebP

Analysis types:
- general: General image description
- chart: Data visualization analysis (identifies trends, axes, values)
- diagram: Flowchart/architecture diagram analysis

Returns a detailed description of the image content.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to image file"
                },
                "image_content": {
                    "type": "string",
                    "description": "Base64-encoded image data"
                },
                "image_format": {
                    "type": "string",
                    "enum": ["png", "jpg", "jpeg", "gif", "webp"],
                    "description": "Image format (required with image_content)"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["general", "chart", "diagram"],
                    "default": "general",
                    "description": "Type of analysis to perform"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context about the image"
                }
            }
        }
    },
    {
        "name": "format_output",
        "description": """Convert parsed document data between formats.

Takes previously parsed data and converts it to JSON or Markdown format.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "parsed_data": {
                    "type": "object",
                    "description": "Previously parsed document data"
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "description": "Target format"
                },
                "pretty_print": {
                    "type": "boolean",
                    "default": True,
                    "description": "Pretty-print JSON output"
                }
            },
            "required": ["parsed_data", "format"]
        }
    },
    {
        "name": "save_output",
        "description": """Save content to the outputs directory.

Saves parsed content with a timestamped filename for later retrieval.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Content to save (JSON or Markdown string)"
                },
                "original_filename": {
                    "type": "string",
                    "description": "Original document filename (used in output name)"
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown", "txt"],
                    "default": "json",
                    "description": "Output file format"
                }
            },
            "required": ["content", "original_filename"]
        }
    },
    {
        "name": "list_outputs",
        "description": """List all saved output files.

Returns a list of previously parsed and saved documents with metadata.""",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "read_output",
        "description": """Read a saved output file.

Retrieves the content of a previously saved parsed document.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the output file to read"
                }
            },
            "required": ["filename"]
        }
    },
    {
        "name": "delete_output",
        "description": """Delete a saved output file.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the file to delete"
                }
            },
            "required": ["filename"]
        }
    },
    {
        "name": "get_info",
        "description": """Get information about the File Parser Agent.

Returns version, supported formats, AI Vision status, and other system information.""",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


# =============================================================================
# Tool Handlers
# =============================================================================

async def handle_parse_document(arguments: dict) -> dict:
    """Handle parse_document tool call."""
    file_path = arguments.get('file_path')
    file_content = arguments.get('file_content')
    filename = arguments.get('filename')
    output_format = arguments.get('output_format', 'json')
    enable_ai_vision = arguments.get('enable_ai_vision', False)
    
    temp_path = None
    
    try:
        # Handle base64 content
        if file_content and filename:
            try:
                decoded = base64.b64decode(file_content)
            except Exception as e:
                return {'success': False, 'error': f'Invalid base64 content: {str(e)}'}
            
            temp_path = os.path.join(file_manager.upload_dir, filename)
            os.makedirs(file_manager.upload_dir, exist_ok=True)
            
            with open(temp_path, 'wb') as f:
                f.write(decoded)
            file_path = temp_path
        
        if not file_path:
            return {'success': False, 'error': 'Provide either file_path or (file_content and filename)'}
        
        # Validate file
        valid, message = ParserManager.validate_file(file_path)
        if not valid:
            return {'success': False, 'error': message}
        
        # Parse
        data = ParserManager.parse(file_path, enable_ai_vision=enable_ai_vision)
        
        # Format output
        if output_format == 'markdown':
            formatted = OutputFormatter.to_markdown(data)
        else:
            formatted = OutputFormatter.to_json(data)
        
        return {
            'success': True,
            'data': data,
            'formatted': formatted,
            'format': output_format
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


async def handle_analyze_image(arguments: dict) -> dict:
    """Handle analyze_image tool call."""
    image_path = arguments.get('image_path')
    image_content = arguments.get('image_content')
    image_format = arguments.get('image_format', 'png')
    analysis_type = arguments.get('analysis_type', 'general')
    context = arguments.get('context', '')
    
    try:
        # Get image data
        if image_path:
            if not os.path.exists(image_path):
                return {'success': False, 'error': f'Image not found: {image_path}'}
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Detect format from extension
            ext = os.path.splitext(image_path)[1].lower().lstrip('.')
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                image_format = ext
        
        elif image_content:
            try:
                image_data = base64.b64decode(image_content)
            except Exception as e:
                return {'success': False, 'error': f'Invalid base64 image: {str(e)}'}
        
        else:
            return {'success': False, 'error': 'Provide either image_path or image_content'}
        
        # Analyze
        result = ai_vision.analyze_image(
            image_data,
            image_format,
            analysis_type=analysis_type,
            context=context
        )
        
        return {'success': True, **result}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


async def handle_format_output(arguments: dict) -> dict:
    """Handle format_output tool call."""
    parsed_data = arguments.get('parsed_data', {})
    fmt = arguments.get('format', 'json')
    pretty = arguments.get('pretty_print', True)
    
    try:
        if fmt == 'markdown':
            content = OutputFormatter.to_markdown(parsed_data)
        else:
            content = OutputFormatter.to_json(parsed_data, pretty=pretty)
        
        return {'success': True, 'formatted': content, 'format': fmt}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


async def handle_save_output(arguments: dict) -> dict:
    """Handle save_output tool call."""
    content = arguments.get('content', '')
    original_filename = arguments.get('original_filename', 'output')
    fmt = arguments.get('format', 'json')
    
    try:
        filename = file_manager.save_output(content, original_filename, fmt)
        return {
            'success': True,
            'saved_as': filename,
            'path': os.path.join(file_manager.output_dir, filename)
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


async def handle_list_outputs(arguments: dict) -> dict:
    """Handle list_outputs tool call."""
    try:
        outputs = file_manager.list_outputs()
        return {
            'success': True,
            'count': len(outputs),
            'files': outputs
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


async def handle_read_output(arguments: dict) -> dict:
    """Handle read_output tool call."""
    filename = arguments.get('filename', '')
    
    try:
        content = file_manager.read_output(filename)
        if content:
            return {'success': True, 'filename': filename, 'content': content}
        else:
            return {'success': False, 'error': f'File not found: {filename}'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


async def handle_delete_output(arguments: dict) -> dict:
    """Handle delete_output tool call."""
    filename = arguments.get('filename', '')
    
    try:
        success = file_manager.delete_output(filename)
        if success:
            return {'success': True, 'deleted': filename}
        else:
            return {'success': False, 'error': f'File not found: {filename}'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


async def handle_get_info(arguments: dict) -> dict:
    """Handle get_info tool call."""
    return {
        'success': True,
        'name': 'File Parser Agent',
        'version': '2.1',
        'supported_extensions': list(sorted(ParserManager.ALLOWED_EXTENSIONS.keys())),
        'supported_types': ParserManager.get_supported_types(),
        'output_formats': ['json', 'markdown'],
        'max_file_size_mb': ParserManager.MAX_FILE_SIZE / (1024 * 1024),
        'ai_vision': {
            'available': ai_vision.is_available(),
            'model': ai_vision.model if ai_vision.is_available() else None
        },
        'output_directory': os.path.abspath(file_manager.output_dir)
    }


# Tool handler dispatch
TOOL_HANDLERS = {
    'parse_document': handle_parse_document,
    'analyze_image': handle_analyze_image,
    'format_output': handle_format_output,
    'save_output': handle_save_output,
    'list_outputs': handle_list_outputs,
    'read_output': handle_read_output,
    'delete_output': handle_delete_output,
    'get_info': handle_get_info,
}


# =============================================================================
# MCP Server Implementation
# =============================================================================

if MCP_AVAILABLE:
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name=tool['name'],
                description=tool['description'],
                inputSchema=tool['inputSchema']
            )
            for tool in TOOLS
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls."""
        handler = TOOL_HANDLERS.get(name)
        
        if handler:
            result = await handler(arguments)
        else:
            result = {'success': False, 'error': f'Unknown tool: {name}'}
        
        # Return result as JSON text
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str, ensure_ascii=False)
            )
        ]


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Run the MCP server."""
    if not MCP_AVAILABLE:
        print("Error: MCP library not installed.", file=sys.stderr)
        print("Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def run_server():
    """Entry point for running the server."""
    asyncio.run(main())


if __name__ == '__main__':
    run_server()
