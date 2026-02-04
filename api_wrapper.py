"""
File Parser Agent - Claude API Wrapper
Provides tool-use integration with Claude API for document parsing.
"""

import anthropic
import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import parsers
from parsers.pdf_parser import parse_pdf
from parsers.word_parser import parse_word
from parsers.excel_parser import parse_excel
from parsers.pptx_parser import parse_pptx
from parsers.image_analyzer import get_image_description, analyze_chart_image


class FileParserAgent:
    """
    Claude-powered file parsing agent with tool-use capabilities.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize the File Parser Agent.

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var.
            model: Claude model to use for conversations.
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it as environment variable or pass to constructor.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)

        # File type mappings
        self.extension_map = {
            'pdf': 'pdf',
            'docx': 'word', 'doc': 'word',
            'xlsx': 'excel', 'xls': 'excel',
            'pptx': 'powerpoint', 'ppt': 'powerpoint'
        }

        self.parser_map = {
            'pdf': parse_pdf,
            'word': parse_word,
            'excel': parse_excel,
            'powerpoint': parse_pptx
        }

    def get_tools(self) -> List[Dict]:
        """Return tool definitions for Claude API."""
        return [
            {
                "name": "file_reader",
                "description": "Read and validate an uploaded document file. Accepts PDF, Word (DOCX/DOC), Excel (XLSX/XLS), and PowerPoint (PPTX/PPT) files. Returns file metadata and validation status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_content": {
                            "type": "string",
                            "description": "Base64-encoded file content"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Original filename with extension"
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, only validate without full read"
                        }
                    },
                    "required": ["file_content", "filename"]
                }
            },
            {
                "name": "parse_document",
                "description": "Parse a document and extract structured content. Handles PDF, Word, Excel, and PowerPoint files. Returns structured data with text, tables, images, and metadata.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_content": {
                            "type": "string",
                            "description": "Base64-encoded file content"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Original filename with extension"
                        },
                        "options": {
                            "type": "object",
                            "properties": {
                                "extract_images": {"type": "boolean", "default": True},
                                "extract_tables": {"type": "boolean", "default": True},
                                "extract_metadata": {"type": "boolean", "default": True}
                            }
                        }
                    },
                    "required": ["file_content", "filename"]
                }
            },
            {
                "name": "analyze_image",
                "description": "Analyze an image using AI vision. Returns detailed description of image content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_content": {
                            "type": "string",
                            "description": "Base64-encoded image data"
                        },
                        "image_format": {
                            "type": "string",
                            "enum": ["png", "jpg", "jpeg", "gif", "webp"],
                            "description": "Image format"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["general", "chart"],
                            "default": "general"
                        },
                        "context": {
                            "type": "string",
                            "description": "Optional context about the image"
                        }
                    },
                    "required": ["image_content", "image_format"]
                }
            },
            {
                "name": "format_as_json",
                "description": "Format parsed document data as clean JSON.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_data": {
                            "type": "object",
                            "description": "Parsed document data"
                        },
                        "pretty_print": {
                            "type": "boolean",
                            "default": True
                        }
                    },
                    "required": ["parsed_data"]
                }
            },
            {
                "name": "format_as_markdown",
                "description": "Convert parsed document data to Markdown format.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_data": {
                            "type": "object",
                            "description": "Parsed document data"
                        },
                        "include_toc": {
                            "type": "boolean",
                            "default": False
                        }
                    },
                    "required": ["parsed_data"]
                }
            },
            {
                "name": "create_artifact",
                "description": "Generate a downloadable output file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to write to file"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Output filename"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown", "txt", "csv"]
                        }
                    },
                    "required": ["content", "filename", "format"]
                }
            },
            {
                "name": "extract_tables",
                "description": "Extract only table data from a document.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_content": {
                            "type": "string",
                            "description": "Base64-encoded file content"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Original filename"
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["json", "csv", "markdown"],
                            "default": "json"
                        }
                    },
                    "required": ["file_content", "filename"]
                }
            },
            {
                "name": "summarize_document",
                "description": "Generate a summary of a parsed document.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_data": {
                            "type": "object",
                            "description": "Parsed document data"
                        },
                        "summary_length": {
                            "type": "string",
                            "enum": ["brief", "standard", "detailed"],
                            "default": "standard"
                        }
                    },
                    "required": ["parsed_data"]
                }
            }
        ]

    def _get_file_type(self, filename: str) -> Optional[str]:
        """Determine file type from filename extension."""
        ext = filename.rsplit('.', 1)[-1].lower()
        return self.extension_map.get(ext)

    def _save_temp_file(self, content_b64: str, filename: str) -> Path:
        """Save base64 content to temporary file."""
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)

        filepath = temp_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"

        file_bytes = base64.b64decode(content_b64)
        filepath.write_bytes(file_bytes)

        return filepath

    def _cleanup_temp_file(self, filepath: Path):
        """Remove temporary file."""
        try:
            filepath.unlink()
        except Exception:
            pass

    # Tool implementations
    def tool_file_reader(self, file_content: str, filename: str, validate_only: bool = False) -> Dict:
        """Read and validate an uploaded file."""
        file_type = self._get_file_type(filename)

        if not file_type:
            return {
                "success": False,
                "error": f"Unsupported file type. Supported: {', '.join(self.extension_map.keys())}"
            }

        try:
            file_bytes = base64.b64decode(file_content)
            file_size = len(file_bytes)

            if file_size > 50 * 1024 * 1024:  # 50MB limit
                return {
                    "success": False,
                    "error": "File exceeds 50MB limit"
                }

            return {
                "success": True,
                "filename": filename,
                "file_type": file_type,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "validated": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}"
            }

    def tool_parse_document(self, file_content: str, filename: str, options: Optional[Dict] = None) -> Dict:
        """Parse a document and extract content."""
        file_type = self._get_file_type(filename)

        if not file_type:
            return {"error": f"Unsupported file type for {filename}"}

        # Save to temp file for parsing
        filepath = self._save_temp_file(file_content, filename)

        try:
            parser = self.parser_map[file_type]

            # PowerPoint supports AI vision option
            if file_type == 'powerpoint':
                enable_vision = options.get('extract_images', True) if options else True
                result = parser(str(filepath), enable_ai_vision=enable_vision)
            else:
                result = parser(str(filepath))

            return result
        except Exception as e:
            return {"error": f"Parsing failed: {str(e)}"}
        finally:
            self._cleanup_temp_file(filepath)

    def tool_analyze_image(self, image_content: str, image_format: str,
                          analysis_type: str = "general", context: str = "") -> Dict:
        """Analyze an image using AI vision."""
        try:
            image_bytes = base64.b64decode(image_content)

            if analysis_type == "chart":
                return analyze_chart_image(image_bytes, image_format)
            else:
                return get_image_description(image_bytes, image_format, context)
        except Exception as e:
            return {"error": f"Image analysis failed: {str(e)}"}

    def tool_format_as_json(self, parsed_data: Dict, pretty_print: bool = True) -> Dict:
        """Format parsed data as JSON."""
        try:
            if pretty_print:
                json_str = json.dumps(parsed_data, indent=2, ensure_ascii=False)
            else:
                json_str = json.dumps(parsed_data, ensure_ascii=False)

            return {
                "success": True,
                "format": "json",
                "content": json_str,
                "size_bytes": len(json_str.encode('utf-8'))
            }
        except Exception as e:
            return {"error": f"JSON formatting failed: {str(e)}"}

    def tool_format_as_markdown(self, parsed_data: Dict, include_toc: bool = False) -> Dict:
        """Convert parsed data to Markdown."""
        try:
            md = self._convert_to_markdown(parsed_data, include_toc)
            return {
                "success": True,
                "format": "markdown",
                "content": md,
                "size_bytes": len(md.encode('utf-8'))
            }
        except Exception as e:
            return {"error": f"Markdown formatting failed: {str(e)}"}

    def _convert_to_markdown(self, data: Dict, include_toc: bool = False) -> str:
        """Convert parsed data to Markdown format."""
        md = []

        # Header
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
                        # Header row
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

                # Image descriptions
                for shape in slide.get('shapes', []):
                    if shape.get('content_type') == 'image' and shape.get('description'):
                        md.append(f"\n*[Image: {shape['description']}]*\n")

        return '\n'.join(md)

    def tool_create_artifact(self, content: str, filename: str, format: str) -> Dict:
        """Create a downloadable output file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{Path(filename).stem}_{timestamp}.{format}"
            output_path = self.output_dir / output_filename

            output_path.write_text(content, encoding='utf-8')

            return {
                "success": True,
                "filename": output_filename,
                "path": str(output_path),
                "size_bytes": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {"error": f"Failed to create artifact: {str(e)}"}

    def tool_extract_tables(self, file_content: str, filename: str,
                           output_format: str = "json") -> Dict:
        """Extract only table data from a document."""
        # First parse the document
        parsed = self.tool_parse_document(file_content, filename)

        if 'error' in parsed:
            return parsed

        tables = []
        file_type = parsed.get('file_type')

        if file_type == 'word':
            tables = parsed.get('tables', [])
        elif file_type == 'excel':
            for sheet in parsed.get('sheets', []):
                tables.append({
                    'name': sheet['name'],
                    'data': sheet.get('data', [])
                })
        elif file_type == 'powerpoint':
            for slide in parsed.get('slides', []):
                for shape in slide.get('shapes', []):
                    if shape.get('content_type') == 'table':
                        tables.append({
                            'slide': slide['slide_number'],
                            'rows': shape.get('rows'),
                            'columns': shape.get('columns')
                        })

        if output_format == 'csv' and tables:
            # Convert first table to CSV
            csv_lines = []
            table_data = tables[0].get('data', [])
            for row in table_data:
                csv_lines.append(','.join(f'"{c}"' for c in row))
            return {
                "success": True,
                "format": "csv",
                "table_count": len(tables),
                "content": '\n'.join(csv_lines)
            }
        elif output_format == 'markdown':
            return self.tool_format_as_markdown({'file_type': file_type, 'tables': tables})

        return {
            "success": True,
            "format": "json",
            "table_count": len(tables),
            "tables": tables
        }

    def tool_summarize_document(self, parsed_data: Dict, summary_length: str = "standard") -> Dict:
        """Generate a document summary using Claude."""
        file_type = parsed_data.get('file_type', 'document')

        # Build content summary
        stats = {
            "file_type": file_type,
            "filename": parsed_data.get('filename', 'Unknown')
        }

        content_preview = ""

        if file_type == 'pdf':
            stats['total_pages'] = parsed_data.get('total_pages', 0)
            pages = parsed_data.get('pages', [])
            if pages:
                content_preview = pages[0].get('text', '')[:2000]

        elif file_type == 'word':
            stats['total_paragraphs'] = parsed_data.get('total_paragraphs', 0)
            stats['total_tables'] = parsed_data.get('total_tables', 0)
            paras = parsed_data.get('paragraphs', [])
            texts = [p.get('text', '') if isinstance(p, dict) else p for p in paras[:10]]
            content_preview = '\n'.join(texts)[:2000]

        elif file_type == 'excel':
            sheets = parsed_data.get('sheets', [])
            stats['total_sheets'] = len(sheets)
            stats['sheet_names'] = [s['name'] for s in sheets]

        elif file_type == 'powerpoint':
            slides = parsed_data.get('slides', [])
            stats['total_slides'] = len(slides)
            titles = [s.get('title', '') for s in slides if s.get('title')]
            stats['slide_titles'] = titles
            content_preview = '\n'.join([s.get('text', '')[:200] for s in slides[:5]])

        # Use Claude to generate summary
        length_tokens = {"brief": 100, "standard": 300, "detailed": 600}
        max_tokens = length_tokens.get(summary_length, 300)

        prompt = f"""Summarize this {file_type} document based on the following information:

Statistics: {json.dumps(stats, indent=2)}

Content Preview:
{content_preview}

Provide a {summary_length} summary focusing on the main topics and key points."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            summary = response.content[0].text

            return {
                "success": True,
                "summary": summary,
                "statistics": stats,
                "length": summary_length
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Summary generation failed: {str(e)}",
                "statistics": stats
            }

    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Any:
        """Process a tool call and return the result."""
        tool_handlers = {
            "file_reader": self.tool_file_reader,
            "parse_document": self.tool_parse_document,
            "analyze_image": self.tool_analyze_image,
            "format_as_json": self.tool_format_as_json,
            "format_as_markdown": self.tool_format_as_markdown,
            "create_artifact": self.tool_create_artifact,
            "extract_tables": self.tool_extract_tables,
            "summarize_document": self.tool_summarize_document
        }

        handler = tool_handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}

        return handler(**tool_input)

    def chat(self, user_message: str, file_content: Optional[str] = None,
             filename: Optional[str] = None) -> str:
        """
        Have a conversation with the agent, optionally including a file.

        Args:
            user_message: User's message/instruction
            file_content: Optional base64-encoded file content
            filename: Optional filename (required if file_content provided)

        Returns:
            Agent's response as string
        """
        messages = []

        # Build initial message
        if file_content and filename:
            content = f"I'm uploading a file: {filename}\n\nFile content (base64): {file_content[:100]}...[truncated]\n\nRequest: {user_message}"
        else:
            content = user_message

        messages.append({"role": "user", "content": content})

        # Store file info for tool calls
        self._current_file = (file_content, filename) if file_content else None

        # Initial API call
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            tools=self.get_tools(),
            messages=messages
        )

        # Process tool calls in a loop
        while response.stop_reason == "tool_use":
            # Find tool use blocks
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            # Add assistant's response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call
            tool_results = []
            for tool_use in tool_uses:
                tool_input = tool_use.input

                # Inject file content if tool needs it and we have it
                if self._current_file and 'file_content' in str(tool_use.input):
                    if not tool_input.get('file_content'):
                        tool_input['file_content'] = self._current_file[0]
                    if not tool_input.get('filename'):
                        tool_input['filename'] = self._current_file[1]

                result = self.process_tool_call(tool_use.name, tool_input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result) if isinstance(result, dict) else str(result)
                })

            messages.append({"role": "user", "content": tool_results})

            # Continue conversation
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=self.get_tools(),
                messages=messages
            )

        # Extract final text response
        text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
        return '\n'.join(text_blocks)

    def parse_file(self, filepath: str, output_format: str = "json") -> Dict:
        """
        Convenience method to parse a file directly.

        Args:
            filepath: Path to the file to parse
            output_format: 'json' or 'markdown'

        Returns:
            Parsed data or formatted output
        """
        path = Path(filepath)

        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        # Read and encode file
        file_bytes = path.read_bytes()
        file_content = base64.b64encode(file_bytes).decode('utf-8')

        # Parse
        parsed = self.tool_parse_document(file_content, path.name)

        if 'error' in parsed:
            return parsed

        # Format output
        if output_format == 'markdown':
            return self.tool_format_as_markdown(parsed)
        else:
            return self.tool_format_as_json(parsed)


# CLI interface
if __name__ == "__main__":
    import sys

    print("=" * 50)
    print("File Parser Agent - API Wrapper")
    print("=" * 50)

    try:
        agent = FileParserAgent()
        print("Agent initialized successfully.\n")

        if len(sys.argv) > 1:
            # Parse file from command line
            filepath = sys.argv[1]
            output_format = sys.argv[2] if len(sys.argv) > 2 else "json"

            print(f"Parsing: {filepath}")
            print(f"Output format: {output_format}\n")

            result = agent.parse_file(filepath, output_format)

            if 'content' in result:
                print(result['content'])
            else:
                print(json.dumps(result, indent=2))
        else:
            # Interactive mode
            print("Interactive mode. Type 'quit' to exit.\n")
            print("Commands:")
            print("  parse <filepath> [json|markdown]  - Parse a file")
            print("  chat <message>                    - Chat with agent")
            print("  quit                              - Exit\n")

            while True:
                try:
                    user_input = input(">>> ").strip()

                    if not user_input:
                        continue

                    if user_input.lower() == 'quit':
                        break

                    if user_input.startswith('parse '):
                        parts = user_input[6:].split()
                        filepath = parts[0]
                        fmt = parts[1] if len(parts) > 1 else "json"

                        result = agent.parse_file(filepath, fmt)
                        if 'content' in result:
                            print(result['content'])
                        else:
                            print(json.dumps(result, indent=2))

                    elif user_input.startswith('chat '):
                        message = user_input[5:]
                        response = agent.chat(message)
                        print(f"\nAgent: {response}\n")

                    else:
                        # Treat as chat message
                        response = agent.chat(user_input)
                        print(f"\nAgent: {response}\n")

                except KeyboardInterrupt:
                    print("\n")
                    break
                except Exception as e:
                    print(f"Error: {e}\n")

    except ValueError as e:
        print(f"Error: {e}")
        print("Set ANTHROPIC_API_KEY environment variable or create .env file")
        sys.exit(1)
