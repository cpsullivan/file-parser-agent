"""
File Parser Agent - Python API Wrapper

Provides a high-level Python API for document parsing with Claude tool-use support.

Usage:
    from api_wrapper import FileParserAgent
    
    # Create agent
    agent = FileParserAgent()
    
    # Parse a file
    result = agent.parse_file('document.pdf')
    
    # Parse with options
    result = agent.parse_file(
        'presentation.pptx',
        output_format='markdown',
        enable_ai_vision=True
    )
    
    # Parse from bytes
    with open('document.pdf', 'rb') as f:
        result = agent.parse_bytes(f.read(), 'document.pdf')
"""

import os
import base64
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from core.parser_manager import ParserManager
from core.output_formatter import OutputFormatter
from core.file_manager import FileManager
from core.ai_vision import AIVision


class FileParserAgent:
    """
    High-level API for document parsing.
    
    Provides methods for parsing documents from files, bytes, or base64,
    with support for various output formats and AI-powered image analysis.
    
    Attributes:
        file_manager: FileManager instance for output handling
        ai_vision: AIVision instance for image analysis
    """
    
    def __init__(self, output_dir: str = 'outputs', upload_dir: str = 'uploads'):
        """
        Initialize the File Parser Agent.
        
        Args:
            output_dir: Directory for saving parsed outputs
            upload_dir: Directory for temporary file uploads
        """
        self.file_manager = FileManager(upload_dir=upload_dir, output_dir=output_dir)
        self.ai_vision = AIVision()
        self._temp_files = []
    
    def parse_file(
        self,
        filepath: str,
        output_format: str = 'json',
        enable_ai_vision: bool = False,
        save_output: bool = False
    ) -> Dict[str, Any]:
        """
        Parse a document file.
        
        Args:
            filepath: Path to the file to parse
            output_format: Output format ('json' or 'markdown')
            enable_ai_vision: Enable AI image analysis for PowerPoint
            save_output: Save the result to the outputs directory
        
        Returns:
            Dictionary containing:
            - success: Whether parsing succeeded
            - data: Parsed document data
            - formatted: Formatted output string (JSON or Markdown)
            - output_file: Saved filename (if save_output=True)
            - error: Error message (if failed)
        """
        # Validate file
        valid, message = ParserManager.validate_file(filepath)
        if not valid:
            return {
                'success': False,
                'error': message,
                'filepath': filepath
            }
        
        # Parse
        try:
            data = ParserManager.parse(filepath, enable_ai_vision=enable_ai_vision)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filepath': filepath
            }
        
        # Check for parsing errors
        if 'error' in data and not any(k in data for k in ['pages', 'paragraphs', 'sheets', 'slides']):
            return {
                'success': False,
                'error': data['error'],
                'filepath': filepath
            }
        
        # Format output
        if output_format == 'markdown':
            formatted = OutputFormatter.to_markdown(data)
        else:
            formatted = OutputFormatter.to_json(data)
        
        result = {
            'success': True,
            'data': data,
            'formatted': formatted,
            'format': output_format,
            'filepath': filepath
        }
        
        # Save if requested
        if save_output:
            filename = self.file_manager.save_output(
                formatted,
                os.path.basename(filepath),
                output_format
            )
            result['output_file'] = filename
        
        return result
    
    def parse_bytes(
        self,
        content: bytes,
        filename: str,
        output_format: str = 'json',
        enable_ai_vision: bool = False,
        save_output: bool = False
    ) -> Dict[str, Any]:
        """
        Parse document from raw bytes.
        
        Args:
            content: Raw file bytes
            filename: Original filename (used to detect type)
            output_format: Output format ('json' or 'markdown')
            enable_ai_vision: Enable AI image analysis
            save_output: Save the result to outputs directory
        
        Returns:
            Same as parse_file()
        """
        # Save to temp file
        temp_path = os.path.join(self.file_manager.upload_dir, filename)
        os.makedirs(self.file_manager.upload_dir, exist_ok=True)
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            # Parse the temp file
            result = self.parse_file(
                temp_path,
                output_format=output_format,
                enable_ai_vision=enable_ai_vision,
                save_output=save_output
            )
            
            return result
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def parse_base64(
        self,
        content: str,
        filename: str,
        output_format: str = 'json',
        enable_ai_vision: bool = False,
        save_output: bool = False
    ) -> Dict[str, Any]:
        """
        Parse document from base64-encoded content.
        
        Args:
            content: Base64-encoded file content
            filename: Original filename
            output_format: Output format
            enable_ai_vision: Enable AI image analysis
            save_output: Save result to outputs
        
        Returns:
            Same as parse_file()
        """
        try:
            decoded = base64.b64decode(content)
        except Exception as e:
            return {
                'success': False,
                'error': f'Invalid base64 content: {str(e)}',
                'filename': filename
            }
        
        return self.parse_bytes(
            decoded,
            filename,
            output_format=output_format,
            enable_ai_vision=enable_ai_vision,
            save_output=save_output
        )
    
    def analyze_image(
        self,
        image_data: bytes,
        image_format: str,
        analysis_type: str = 'general',
        context: str = ''
    ) -> Dict[str, Any]:
        """
        Analyze an image using AI Vision.
        
        Args:
            image_data: Raw image bytes
            image_format: Image format (png, jpg, etc.)
            analysis_type: Type of analysis ('general', 'chart', 'diagram')
            context: Additional context about the image
        
        Returns:
            AI analysis result dictionary
        """
        return self.ai_vision.analyze_image(
            image_data,
            image_format,
            analysis_type=analysis_type,
            context=context
        )
    
    def list_outputs(self) -> List[Dict[str, Any]]:
        """
        List all saved output files.
        
        Returns:
            List of file metadata dictionaries
        """
        return self.file_manager.list_outputs()
    
    def read_output(self, filename: str) -> Optional[str]:
        """
        Read a saved output file.
        
        Args:
            filename: Name of the output file
        
        Returns:
            File content or None if not found
        """
        return self.file_manager.read_output(filename)
    
    def delete_output(self, filename: str) -> bool:
        """
        Delete a saved output file.
        
        Args:
            filename: Name of the file to delete
        
        Returns:
            True if deleted, False if not found
        """
        return self.file_manager.delete_output(filename)
    
    def clear_outputs(self) -> int:
        """
        Delete all saved output files.
        
        Returns:
            Number of files deleted
        """
        return self.file_manager.clear_outputs()
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information and capabilities.
        
        Returns:
            Dictionary with version, supported formats, AI status, etc.
        """
        return {
            'name': 'File Parser Agent',
            'version': '2.1',
            'supported_extensions': list(sorted(ParserManager.ALLOWED_EXTENSIONS.keys())),
            'supported_types': ParserManager.get_supported_types(),
            'output_formats': ['json', 'markdown'],
            'max_file_size_mb': ParserManager.MAX_FILE_SIZE / (1024 * 1024),
            'ai_vision': {
                'available': self.ai_vision.is_available(),
                'model': self.ai_vision.model if self.ai_vision.is_available() else None
            }
        }


# =============================================================================
# Claude Tool-Use Integration
# =============================================================================

# Tool definitions for Claude API tool-use
TOOL_DEFINITIONS = [
    {
        "name": "parse_document",
        "description": "Parse a document file (PDF, Word, Excel, PowerPoint) and extract structured content. Returns parsed data with text, tables, metadata, and visual element information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to parse"
                },
                "file_content": {
                    "type": "string",
                    "description": "Base64-encoded file content (alternative to file_path)"
                },
                "filename": {
                    "type": "string",
                    "description": "Original filename with extension (required if using file_content)"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "json",
                    "description": "Output format for the parsed content"
                },
                "enable_ai_vision": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable AI-powered image analysis for PowerPoint files"
                }
            }
        }
    },
    {
        "name": "analyze_image",
        "description": "Analyze an image using AI vision to generate a description. Supports general images, charts, and diagrams.",
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
                    "enum": ["general", "chart", "diagram"],
                    "default": "general",
                    "description": "Type of analysis to perform"
                },
                "context": {
                    "type": "string",
                    "description": "Optional context about where the image appears"
                }
            },
            "required": ["image_content", "image_format"]
        }
    },
    {
        "name": "list_outputs",
        "description": "List all previously parsed output files saved in the outputs directory.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "read_output",
        "description": "Read the content of a saved output file.",
        "input_schema": {
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
        "description": "Delete a saved output file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the output file to delete"
                }
            },
            "required": ["filename"]
        }
    }
]


def handle_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a tool call from Claude.
    
    Args:
        tool_name: Name of the tool to call
        tool_input: Tool input parameters
    
    Returns:
        Tool result dictionary
    """
    agent = FileParserAgent()
    
    if tool_name == "parse_document":
        # Check for file path or content
        if tool_input.get('file_path'):
            return agent.parse_file(
                tool_input['file_path'],
                output_format=tool_input.get('output_format', 'json'),
                enable_ai_vision=tool_input.get('enable_ai_vision', False)
            )
        elif tool_input.get('file_content') and tool_input.get('filename'):
            return agent.parse_base64(
                tool_input['file_content'],
                tool_input['filename'],
                output_format=tool_input.get('output_format', 'json'),
                enable_ai_vision=tool_input.get('enable_ai_vision', False)
            )
        else:
            return {'success': False, 'error': 'Provide either file_path or (file_content and filename)'}
    
    elif tool_name == "analyze_image":
        image_data = base64.b64decode(tool_input['image_content'])
        return agent.analyze_image(
            image_data,
            tool_input['image_format'],
            analysis_type=tool_input.get('analysis_type', 'general'),
            context=tool_input.get('context', '')
        )
    
    elif tool_name == "list_outputs":
        return {'outputs': agent.list_outputs()}
    
    elif tool_name == "read_output":
        content = agent.read_output(tool_input['filename'])
        if content:
            return {'success': True, 'content': content}
        else:
            return {'success': False, 'error': 'File not found'}
    
    elif tool_name == "delete_output":
        success = agent.delete_output(tool_input['filename'])
        return {'success': success}
    
    else:
        return {'success': False, 'error': f'Unknown tool: {tool_name}'}


# =============================================================================
# Convenience Functions
# =============================================================================

def parse(filepath: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to parse a file.
    
    Args:
        filepath: Path to the file
        **kwargs: Additional arguments passed to parse_file()
    
    Returns:
        Parsing result dictionary
    """
    agent = FileParserAgent()
    return agent.parse_file(filepath, **kwargs)


def parse_to_json(filepath: str, enable_ai_vision: bool = False) -> str:
    """
    Parse a file and return JSON string.
    
    Args:
        filepath: Path to the file
        enable_ai_vision: Enable AI image analysis
    
    Returns:
        JSON string of parsed content
    """
    result = parse(filepath, output_format='json', enable_ai_vision=enable_ai_vision)
    if result['success']:
        return result['formatted']
    else:
        raise ValueError(result.get('error', 'Unknown error'))


def parse_to_markdown(filepath: str, enable_ai_vision: bool = False) -> str:
    """
    Parse a file and return Markdown string.
    
    Args:
        filepath: Path to the file
        enable_ai_vision: Enable AI image analysis
    
    Returns:
        Markdown string of parsed content
    """
    result = parse(filepath, output_format='markdown', enable_ai_vision=enable_ai_vision)
    if result['success']:
        return result['formatted']
    else:
        raise ValueError(result.get('error', 'Unknown error'))
