#!/usr/bin/env python3
"""
File Parser Agent - Command Line Interface

Parse documents from the command line and output JSON or Markdown.

Usage:
    python cli.py document.pdf
    python cli.py report.docx --format markdown
    python cli.py presentation.pptx --ai-vision --output result.json
    python cli.py --interactive
    python cli.py --list
"""

import argparse
import sys
import os
import json

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core.parser_manager import ParserManager
from core.output_formatter import OutputFormatter
from core.file_manager import FileManager
from core.ai_vision import AIVision


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='File Parser Agent - Parse documents to JSON or Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf                    Parse PDF to JSON (stdout)
  %(prog)s report.docx -f markdown         Parse Word doc to Markdown
  %(prog)s data.xlsx -o output.json        Parse Excel and save to file
  %(prog)s slides.pptx --ai-vision         Parse PowerPoint with AI image analysis
  %(prog)s -i                              Interactive mode
  %(prog)s --list                          List saved outputs
  %(prog)s --info                          Show system information

Supported formats: PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT
        """
    )
    
    # Positional argument for file
    parser.add_argument(
        'file',
        nargs='?',
        help='File to parse'
    )
    
    # Output format
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'markdown', 'md'],
        default='json',
        help='Output format (default: json)'
    )
    
    # Output file
    parser.add_argument(
        '-o', '--output',
        help='Save output to file instead of stdout'
    )
    
    # AI Vision
    parser.add_argument(
        '--ai-vision',
        action='store_true',
        help='Enable AI image analysis for PowerPoint files'
    )
    
    # Save to outputs directory
    parser.add_argument(
        '-s', '--save',
        action='store_true',
        help='Save output to the outputs directory'
    )
    
    # Interactive mode
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Start interactive mode'
    )
    
    # List outputs
    parser.add_argument(
        '--list',
        action='store_true',
        help='List previously parsed files'
    )
    
    # Clear outputs
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all saved outputs'
    )
    
    # System info
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show system information'
    )
    
    # Verbose
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    # Pretty print (for JSON)
    parser.add_argument(
        '--no-pretty',
        action='store_true',
        help='Disable pretty-printing for JSON output'
    )
    
    return parser.parse_args()


def show_info():
    """Display system information."""
    print("=" * 50)
    print("FILE PARSER AGENT - System Information")
    print("=" * 50)
    
    # Version and supported formats
    print(f"\nVersion: 2.1")
    print(f"Supported extensions: {', '.join(sorted(ParserManager.ALLOWED_EXTENSIONS.keys()))}")
    print(f"Supported types: {', '.join(ParserManager.get_supported_types())}")
    print(f"Max file size: {ParserManager.MAX_FILE_SIZE / (1024*1024):.0f} MB")
    
    # AI Vision status
    print("\nAI Vision:")
    vision = AIVision()
    print(f"  Available: {vision.is_available()}")
    print(f"  API Key: {'Configured' if vision.api_key else 'Not set'}")
    print(f"  Model: {vision.model}")
    
    # Outputs directory
    file_manager = FileManager()
    outputs = file_manager.list_outputs()
    print(f"\nOutputs directory: {os.path.abspath(file_manager.output_dir)}")
    print(f"  Saved files: {len(outputs)}")
    
    print()


def list_outputs():
    """List all saved output files."""
    file_manager = FileManager()
    outputs = file_manager.list_outputs()
    
    if not outputs:
        print("No saved output files.")
        return
    
    print(f"\n{'Filename':<45} {'Size':<10} {'Modified'}")
    print("-" * 70)
    
    for f in outputs:
        size = f['size']
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size/1024/1024:.1f} MB"
        
        # Truncate filename if too long
        filename = f['filename']
        if len(filename) > 44:
            filename = filename[:41] + "..."
        
        print(f"{filename:<45} {size_str:<10} {f['modified'][:19]}")
    
    print(f"\nTotal: {len(outputs)} file(s)")


def clear_outputs():
    """Clear all saved output files."""
    file_manager = FileManager()
    
    # Confirm
    outputs = file_manager.list_outputs()
    if not outputs:
        print("No files to clear.")
        return
    
    confirm = input(f"Delete {len(outputs)} file(s)? [y/N]: ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    count = file_manager.clear_outputs()
    print(f"Deleted {count} file(s).")


def parse_file(filepath, output_format, enable_ai_vision=False, pretty=True):
    """Parse a file and return formatted output."""
    # Validate file
    valid, message = ParserManager.validate_file(filepath)
    if not valid:
        return None, message
    
    # Parse
    result = ParserManager.parse(filepath, enable_ai_vision=enable_ai_vision)
    
    # Check for errors
    if 'error' in result and not any(k in result for k in ['pages', 'paragraphs', 'sheets', 'slides']):
        return None, result['error']
    
    # Format output
    if output_format in ('markdown', 'md'):
        output = OutputFormatter.to_markdown(result)
    else:
        output = OutputFormatter.to_json(result, pretty=pretty)
    
    return output, result


def interactive_mode():
    """Run interactive CLI mode."""
    print("\n" + "=" * 50)
    print("FILE PARSER AGENT - Interactive Mode")
    print("=" * 50)
    print("\nCommands:")
    print("  parse <file> [--json|--markdown] [--ai]  Parse a file")
    print("  list                                      List saved outputs")
    print("  read <filename>                           Read a saved output")
    print("  delete <filename>                         Delete a saved output")
    print("  clear                                     Clear all outputs")
    print("  info                                      Show system info")
    print("  help                                      Show this help")
    print("  quit                                      Exit")
    print()
    
    file_manager = FileManager()
    
    while True:
        try:
            cmd = input("parser> ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split()
            command = parts[0].lower()
            args = parts[1:]
            
            if command in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            
            elif command == 'help':
                print("\nCommands: parse, list, read, delete, clear, info, quit")
            
            elif command == 'info':
                show_info()
            
            elif command == 'list':
                list_outputs()
            
            elif command == 'clear':
                clear_outputs()
            
            elif command == 'parse' and args:
                filepath = args[0]
                output_format = 'json'
                enable_ai = False
                
                for arg in args[1:]:
                    if arg in ('--markdown', '--md', '-m'):
                        output_format = 'markdown'
                    elif arg in ('--json', '-j'):
                        output_format = 'json'
                    elif arg in ('--ai', '--ai-vision'):
                        enable_ai = True
                
                if not os.path.exists(filepath):
                    print(f"File not found: {filepath}")
                    continue
                
                print(f"Parsing {filepath}...")
                output, result = parse_file(filepath, output_format, enable_ai)
                
                if output:
                    # Save to outputs
                    filename = file_manager.save_output(
                        output, 
                        os.path.basename(filepath), 
                        output_format
                    )
                    print(f"Saved to: {filename}")
                    
                    # Show preview
                    if output_format == 'json' and isinstance(result, dict):
                        file_type = result.get('file_type', 'unknown')
                        if file_type == 'pdf':
                            print(f"  Pages: {result.get('total_pages', 0)}")
                        elif file_type == 'word':
                            print(f"  Paragraphs: {result.get('total_paragraphs', 0)}")
                            print(f"  Tables: {result.get('total_tables', 0)}")
                        elif file_type == 'excel':
                            sheets = result.get('metadata', {}).get('sheet_names', [])
                            print(f"  Sheets: {len(sheets)}")
                        elif file_type == 'powerpoint':
                            print(f"  Slides: {result.get('metadata', {}).get('total_slides', 0)}")
                            if result.get('ai_vision_enabled'):
                                summary = result.get('ai_analysis_summary', {})
                                print(f"  AI Vision: {summary.get('images_analyzed', 0)}/{summary.get('images_total', 0)} images")
                else:
                    print(f"Error: {result}")
            
            elif command == 'read' and args:
                filename = args[0]
                content = file_manager.read_output(filename)
                if content:
                    print(content[:2000])
                    if len(content) > 2000:
                        print(f"\n... [{len(content) - 2000} more characters]")
                else:
                    print(f"File not found: {filename}")
            
            elif command == 'delete' and args:
                filename = args[0]
                if file_manager.delete_output(filename):
                    print(f"Deleted: {filename}")
                else:
                    print(f"File not found: {filename}")
            
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit.")
        
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Handle special modes
    if args.info:
        show_info()
        return 0
    
    if args.list:
        list_outputs()
        return 0
    
    if args.clear:
        clear_outputs()
        return 0
    
    if args.interactive:
        interactive_mode()
        return 0
    
    # Require file for parsing
    if not args.file:
        print("Error: No file specified.")
        print("Use -h for help or -i for interactive mode.")
        return 1
    
    # Check file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        return 1
    
    # Parse the file
    output_format = 'markdown' if args.format in ('markdown', 'md') else 'json'
    pretty = not args.no_pretty
    
    if args.verbose:
        print(f"Parsing: {args.file}", file=sys.stderr)
        print(f"Format: {output_format}", file=sys.stderr)
        print(f"AI Vision: {args.ai_vision}", file=sys.stderr)
    
    output, result = parse_file(args.file, output_format, args.ai_vision, pretty)
    
    if output is None:
        print(f"Error: {result}", file=sys.stderr)
        return 1
    
    # Output to file or stdout
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        if args.verbose:
            print(f"Saved to: {args.output}", file=sys.stderr)
    elif args.save:
        file_manager = FileManager()
        filename = file_manager.save_output(output, os.path.basename(args.file), output_format)
        print(f"Saved to outputs/{filename}", file=sys.stderr)
        # Also print to stdout
        print(output)
    else:
        print(output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
