#!/usr/bin/env python3
"""
File Parser Agent - Flask Web Application

A web interface for parsing documents and converting them to JSON or Markdown.
Supports PDF, Word, Excel, and PowerPoint files up to 50MB.
"""

import os
from flask import (
    Flask, 
    render_template, 
    request, 
    jsonify, 
    send_from_directory,
    abort
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from core.parser_manager import ParserManager
from core.output_formatter import OutputFormatter
from core.file_manager import FileManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.getenv('OUTPUT_FOLDER', 'outputs')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize file manager
file_manager = FileManager(
    upload_dir=app.config['UPLOAD_FOLDER'],
    output_dir=app.config['OUTPUT_FOLDER']
)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and parsing.
    
    Expects:
        - file: The uploaded file (multipart/form-data)
        - format: Output format ('json' or 'markdown')
        - ai_vision: Enable AI vision for PowerPoint ('true' or 'false')
    
    Returns:
        JSON response with parsed data or error message
    """
    # Check if file was included
    if 'file' not in request.files:
        return jsonify({
            'success': False, 
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        return jsonify({
            'success': False, 
            'error': 'No file selected'
        }), 400
    
    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({
            'success': False, 
            'error': f'Unsupported file type. Allowed: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
        }), 400
    
    # Get options
    output_format = request.form.get('format', 'json').lower()
    if output_format not in ('json', 'markdown'):
        output_format = 'json'
    
    enable_ai_vision = request.form.get('ai_vision', 'false').lower() == 'true'
    
    # Secure the filename and save
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Save uploaded file
        file.save(filepath)
        
        # Parse the file
        parsed_data = ParserManager.parse(filepath, enable_ai_vision=enable_ai_vision)
        
        # Check for parsing errors
        if 'error' in parsed_data and not any(key in parsed_data for key in ['pages', 'paragraphs', 'sheets', 'slides']):
            return jsonify({
                'success': False,
                'error': parsed_data['error']
            }), 400
        
        # Format the output
        if output_format == 'markdown':
            formatted_content = OutputFormatter.to_markdown(parsed_data)
        else:
            formatted_content = OutputFormatter.to_json(parsed_data)
        
        # Save output file
        output_filename = file_manager.save_output(formatted_content, filename, output_format)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'original_filename': filename,
            'format': output_format,
            'parsed_data': parsed_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Processing error: {str(e)}'
        }), 500
    
    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass


@app.route('/download/<filename>')
def download_file(filename: str):
    """
    Download a parsed output file.
    
    Args:
        filename: Name of the output file to download
    
    Returns:
        File download response
    """
    # Sanitize filename to prevent path traversal
    safe_filename = secure_filename(filename)
    
    # Check if file exists
    filepath = file_manager.get_output_path(safe_filename)
    if not filepath:
        abort(404)
    
    return send_from_directory(
        app.config['OUTPUT_FOLDER'], 
        safe_filename, 
        as_attachment=True
    )


@app.route('/view/<filename>')
def view_file(filename: str):
    """
    View a parsed output file in browser.
    
    Args:
        filename: Name of the output file to view
    
    Returns:
        File content with appropriate content type
    """
    safe_filename = secure_filename(filename)
    content = file_manager.read_output(safe_filename)
    
    if content is None:
        abort(404)
    
    # Determine content type
    if safe_filename.endswith('.json'):
        return app.response_class(content, mimetype='application/json')
    elif safe_filename.endswith('.md'):
        return app.response_class(content, mimetype='text/markdown')
    else:
        return app.response_class(content, mimetype='text/plain')


@app.route('/list-outputs')
def list_outputs():
    """
    List all parsed output files.
    
    Returns:
        JSON array of output file metadata
    """
    outputs = file_manager.list_outputs()
    return jsonify(outputs)


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename: str):
    """
    Delete a parsed output file.
    
    Args:
        filename: Name of the file to delete
    
    Returns:
        JSON response indicating success or failure
    """
    safe_filename = secure_filename(filename)
    success = file_manager.delete_output(safe_filename)
    
    return jsonify({
        'success': success,
        'filename': safe_filename
    })


@app.route('/clear-all', methods=['POST'])
def clear_all():
    """
    Delete all parsed output files.
    
    Returns:
        JSON response with count of deleted files
    """
    count = file_manager.clear_outputs()
    
    return jsonify({
        'success': True,
        'deleted': count
    })


@app.route('/api/info')
def api_info():
    """
    Get API information and supported file types.
    
    Returns:
        JSON with API version and capabilities
    """
    return jsonify({
        'name': 'File Parser Agent',
        'version': '2.0',
        'supported_extensions': list(sorted(ALLOWED_EXTENSIONS)),
        'supported_types': ParserManager.get_supported_types(),
        'output_formats': ['json', 'markdown'],
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024),
        'ai_vision_available': bool(os.getenv('ANTHROPIC_API_KEY'))
    })


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    max_mb = app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {max_mb:.0f}MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Run the application
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    port = int(os.getenv('SERVER_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    FILE PARSER AGENT                         ║
║                      Web Interface                           ║
╠══════════════════════════════════════════════════════════════╣
║  Server:  http://{host}:{port:<5}                              ║
║  Debug:   {str(debug):<5}                                          ║
║  Max Size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB                                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)
