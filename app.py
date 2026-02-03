"""
File Parser Agent - Web Application
Converts PDF, Word, Excel, and PowerPoint files to JSON or Markdown
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import parsers
from parsers.pdf_parser import parse_pdf
from parsers.word_parser import parse_word
from parsers.excel_parser import parse_excel
from parsers.pptx_parser import parse_pptx

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ENABLE_AI_VISION'] = os.environ.get('ENABLE_AI_VISION', 'true').lower() == 'true'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {
    'pdf': parse_pdf,
    'docx': parse_word,
    'doc': parse_word,
    'xlsx': parse_excel,
    'xls': parse_excel,
    'pptx': parse_pptx,
    'ppt': parse_pptx
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_parser(filename):
    """Get appropriate parser for file type"""
    ext = filename.rsplit('.', 1)[1].lower()
    return ALLOWED_EXTENSIONS.get(ext)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and parsing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    output_format = request.form.get('format', 'json')  # json or markdown

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not supported. Allowed: {", ".join(ALLOWED_EXTENSIONS.keys())}'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Parse file (with AI vision option for PowerPoint)
        parser = get_parser(filename)
        if filename.lower().endswith(('.pptx', '.ppt')):
            parsed_data = parser(filepath, enable_ai_vision=app.config['ENABLE_AI_VISION'])
        else:
            parsed_data = parser(filepath)

        # Generate output file
        output_filename = f"{Path(filename).stem}_{timestamp}.{output_format}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        if output_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        else:  # markdown
            markdown_content = convert_to_markdown(parsed_data)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'original_filename': filename,
            'format': output_format,
            'parsed_data': parsed_data
        })

    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download parsed file"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/list-outputs')
def list_outputs():
    """List all parsed output files"""
    files = []
    output_dir = app.config['OUTPUT_FOLDER']

    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if os.path.isfile(filepath):
            files.append({
                'filename': filename,
                'size': os.path.getsize(filepath),
                'created': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
            })

    return jsonify({'files': sorted(files, key=lambda x: x['created'], reverse=True)})

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a parsed file"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return jsonify({'success': True, 'message': f'Deleted {filename}'})
        except Exception as e:
            return jsonify({'error': f'Error deleting file: {str(e)}'}), 500
    return jsonify({'error': 'File not found'}), 404

@app.route('/clear-all', methods=['POST'])
def clear_all():
    """Clear all parsed files"""
    try:
        output_dir = app.config['OUTPUT_FOLDER']
        deleted_count = 0

        for filename in os.listdir(output_dir):
            filepath = os.path.join(output_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
                deleted_count += 1

        return jsonify({'success': True, 'deleted': deleted_count})
    except Exception as e:
        return jsonify({'error': f'Error clearing files: {str(e)}'}), 500

def convert_to_markdown(data):
    """Convert parsed data to Markdown format"""
    md = []

    # Add metadata
    md.append(f"# {data.get('filename', 'Parsed Document')}\n")
    md.append(f"**File Type:** {data.get('file_type', 'Unknown')}\n")
    md.append(f"**Parsed:** {data.get('parsed_at', '')}\n")
    md.append("\n---\n\n")

    # Add content based on file type
    if data.get('file_type') == 'pdf':
        md.append("## PDF Content\n\n")
        for page in data.get('pages', []):
            md.append(f"### Page {page['page_number']}\n\n")
            md.append(f"{page['text']}\n\n")

    elif data.get('file_type') == 'word':
        md.append("## Document Content\n\n")
        for para in data.get('paragraphs', []):
            md.append(f"{para}\n\n")

    elif data.get('file_type') == 'excel':
        md.append("## Spreadsheet Data\n\n")
        for sheet in data.get('sheets', []):
            md.append(f"### Sheet: {sheet['name']}\n\n")
            if sheet.get('data'):
                # Create markdown table
                md.append("| " + " | ".join(str(cell) for cell in sheet['data'][0]) + " |\n")
                md.append("| " + " | ".join("---" for _ in sheet['data'][0]) + " |\n")
                for row in sheet['data'][1:]:
                    md.append("| " + " | ".join(str(cell) for cell in row) + " |\n")
                md.append("\n")

    elif data.get('file_type') == 'powerpoint':
        md.append("## Presentation Slides\n\n")
        for slide in data.get('slides', []):
            md.append(f"### Slide {slide['slide_number']}\n\n")
            if slide.get('title'):
                md.append(f"**Title:** {slide['title']}\n\n")
            if slide.get('text'):
                md.append(f"{slide['text']}\n\n")

    return ''.join(md)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("File Parser Agent - Starting Server")
    print("="*50)
    print("\nAccess the application at: http://localhost:5000")
    print("\nSupported file types:")
    for ext in ALLOWED_EXTENSIONS.keys():
        print(f"  - .{ext}")

    # Check AI Vision status
    print("\n" + "-"*50)
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key and app.config['ENABLE_AI_VISION']:
        print("AI Vision: ENABLED (API key detected)")
        print("Images in PowerPoint files will be auto-described")
    else:
        print("AI Vision: DISABLED")
        if not api_key:
            print("Set ANTHROPIC_API_KEY environment variable to enable")
        print("See AI_VISION_SETUP.md for setup instructions")
    print("-"*50 + "\n")

    app.run(debug=True, port=5000, host='0.0.0.0')
