#!/usr/bin/env python3
"""
Test suite for File Parser Agent - Phase 1
Tests all parsers, formatters, and file management.
"""

import os
import sys
import json
import tempfile
import unittest
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.parser_manager import ParserManager
from core.output_formatter import OutputFormatter
from core.file_manager import FileManager
from parsers.pdf_parser import PDFParser
from parsers.word_parser import WordParser
from parsers.excel_parser import ExcelParser
from parsers.pptx_parser import PowerPointParser


class TestParserManager(unittest.TestCase):
    """Test ParserManager validation and routing."""
    
    def test_supported_extensions(self):
        """Test that all expected extensions are supported."""
        extensions = ParserManager.get_supported_extensions()
        expected = ['.doc', '.docx', '.pdf', '.ppt', '.pptx', '.xls', '.xlsx']
        self.assertEqual(extensions, expected)
    
    def test_supported_types(self):
        """Test that all expected file types are supported."""
        types = ParserManager.get_supported_types()
        expected = ['excel', 'pdf', 'powerpoint', 'word']
        self.assertEqual(types, expected)
    
    def test_file_type_detection(self):
        """Test file type detection by extension."""
        self.assertEqual(ParserManager.get_file_type('test.pdf'), 'pdf')
        self.assertEqual(ParserManager.get_file_type('test.docx'), 'word')
        self.assertEqual(ParserManager.get_file_type('test.xlsx'), 'excel')
        self.assertEqual(ParserManager.get_file_type('test.pptx'), 'powerpoint')
        self.assertIsNone(ParserManager.get_file_type('test.txt'))
    
    def test_validation_nonexistent_file(self):
        """Test validation rejects nonexistent files."""
        is_valid, message = ParserManager.validate_file('/nonexistent/file.pdf')
        self.assertFalse(is_valid)
        self.assertIn('not found', message.lower())
    
    def test_validation_unsupported_extension(self):
        """Test validation rejects unsupported extensions."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'test content')
            temp_path = f.name
        
        try:
            is_valid, message = ParserManager.validate_file(temp_path)
            self.assertFalse(is_valid)
            self.assertIn('unsupported', message.lower())
        finally:
            os.unlink(temp_path)
    
    def test_parse_nonexistent_file(self):
        """Test parsing returns error for nonexistent file."""
        result = ParserManager.parse('/nonexistent/file.pdf')
        self.assertIn('error', result)
        self.assertIn('not found', result['error'].lower())


class TestOutputFormatter(unittest.TestCase):
    """Test output formatting to JSON and Markdown."""
    
    def setUp(self):
        """Set up test data."""
        self.pdf_data = {
            'filename': 'test.pdf',
            'file_type': 'pdf',
            'parsed_at': '2026-02-04T12:00:00',
            'total_pages': 2,
            'metadata': {
                'title': 'Test Document',
                'author': 'Test Author'
            },
            'pages': [
                {'page_number': 1, 'text': 'Page 1 content', 'char_count': 14},
                {'page_number': 2, 'text': 'Page 2 content', 'char_count': 14}
            ]
        }
    
    def test_to_json_valid(self):
        """Test JSON output is valid JSON."""
        json_str = OutputFormatter.to_json(self.pdf_data)
        parsed = json.loads(json_str)
        self.assertEqual(parsed['filename'], 'test.pdf')
        self.assertEqual(parsed['total_pages'], 2)
    
    def test_to_json_pretty(self):
        """Test pretty-printed JSON has indentation."""
        json_pretty = OutputFormatter.to_json(self.pdf_data, pretty=True)
        json_compact = OutputFormatter.to_json(self.pdf_data, pretty=False)
        self.assertGreater(len(json_pretty), len(json_compact))
        self.assertIn('\n', json_pretty)
    
    def test_to_markdown_header(self):
        """Test Markdown output has proper header."""
        md = OutputFormatter.to_markdown(self.pdf_data)
        self.assertIn('# test.pdf', md)
        self.assertIn('**File Type:** pdf', md)
    
    def test_to_markdown_pages(self):
        """Test Markdown includes page content."""
        md = OutputFormatter.to_markdown(self.pdf_data)
        self.assertIn('## Page 1', md)
        self.assertIn('Page 1 content', md)
    
    def test_table_formatting(self):
        """Test table formatting in Markdown."""
        table_data = [
            ['Header1', 'Header2'],
            ['Value1', 'Value2'],
            ['Value3', 'Value4']
        ]
        lines = OutputFormatter._format_table_markdown(table_data)
        self.assertIn('| Header1 | Header2 |', lines[0])
        self.assertIn('---', lines[1])


class TestFileManager(unittest.TestCase):
    """Test file management operations."""
    
    def setUp(self):
        """Set up temporary directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.upload_dir = os.path.join(self.temp_dir, 'uploads')
        self.output_dir = os.path.join(self.temp_dir, 'outputs')
        self.file_manager = FileManager(self.upload_dir, self.output_dir)
    
    def tearDown(self):
        """Clean up temporary directories."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_directories_created(self):
        """Test that directories are created on init."""
        self.assertTrue(os.path.exists(self.upload_dir))
        self.assertTrue(os.path.exists(self.output_dir))
    
    def test_save_output(self):
        """Test saving output file."""
        content = '{"test": "data"}'
        filename = self.file_manager.save_output(content, 'test.pdf', 'json')
        
        self.assertIn('test', filename)
        self.assertTrue(filename.endswith('.json'))
        
        filepath = os.path.join(self.output_dir, filename)
        self.assertTrue(os.path.exists(filepath))
    
    def test_list_outputs(self):
        """Test listing output files."""
        # Create some files
        self.file_manager.save_output('test1', 'file1.pdf', 'json')
        self.file_manager.save_output('test2', 'file2.docx', 'md')
        
        outputs = self.file_manager.list_outputs()
        self.assertEqual(len(outputs), 2)
        
        # Check structure
        for output in outputs:
            self.assertIn('filename', output)
            self.assertIn('size', output)
            self.assertIn('modified', output)
    
    def test_read_output(self):
        """Test reading output file content."""
        content = '{"key": "value"}'
        filename = self.file_manager.save_output(content, 'test.pdf', 'json')
        
        read_content = self.file_manager.read_output(filename)
        self.assertEqual(read_content, content)
    
    def test_delete_output(self):
        """Test deleting output file."""
        filename = self.file_manager.save_output('test', 'test.pdf', 'json')
        
        self.assertTrue(self.file_manager.delete_output(filename))
        self.assertIsNone(self.file_manager.read_output(filename))
    
    def test_clear_outputs(self):
        """Test clearing all output files."""
        self.file_manager.save_output('test1', 'file1.pdf', 'json')
        self.file_manager.save_output('test2', 'file2.pdf', 'json')
        
        count = self.file_manager.clear_outputs()
        self.assertEqual(count, 2)
        self.assertEqual(len(self.file_manager.list_outputs()), 0)
    
    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks."""
        # Attempt to read file outside output directory
        content = self.file_manager.read_output('../../../etc/passwd')
        # Should return None, not the file content
        self.assertIsNone(content)


class TestParsers(unittest.TestCase):
    """Test individual parser can_handle methods."""
    
    def test_pdf_parser_can_handle(self):
        """Test PDF parser handles .pdf files."""
        self.assertTrue(PDFParser.can_handle('test.pdf'))
        self.assertTrue(PDFParser.can_handle('TEST.PDF'))
        self.assertFalse(PDFParser.can_handle('test.docx'))
    
    def test_word_parser_can_handle(self):
        """Test Word parser handles .docx and .doc files."""
        self.assertTrue(WordParser.can_handle('test.docx'))
        self.assertTrue(WordParser.can_handle('test.doc'))
        self.assertFalse(WordParser.can_handle('test.pdf'))
    
    def test_excel_parser_can_handle(self):
        """Test Excel parser handles .xlsx and .xls files."""
        self.assertTrue(ExcelParser.can_handle('test.xlsx'))
        self.assertTrue(ExcelParser.can_handle('test.xls'))
        self.assertFalse(ExcelParser.can_handle('test.pdf'))
    
    def test_pptx_parser_can_handle(self):
        """Test PowerPoint parser handles .pptx and .ppt files."""
        self.assertTrue(PowerPointParser.can_handle('test.pptx'))
        self.assertTrue(PowerPointParser.can_handle('test.ppt'))
        self.assertFalse(PowerPointParser.can_handle('test.pdf'))


def run_integration_test():
    """
    Run integration test with real files if available.
    Place test files in tests/sample_files/ directory.
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST")
    print("="*60)
    
    sample_dir = os.path.join(PROJECT_ROOT, 'tests', 'sample_files')
    
    if not os.path.exists(sample_dir):
        print(f"Sample directory not found: {sample_dir}")
        print("Create the directory and add test files to run integration tests.")
        return
    
    # Find test files
    test_files = []
    for filename in os.listdir(sample_dir):
        filepath = os.path.join(sample_dir, filename)
        if os.path.isfile(filepath):
            ext = os.path.splitext(filename)[1].lower()
            if ext in ParserManager.ALLOWED_EXTENSIONS:
                test_files.append(filepath)
    
    if not test_files:
        print("No test files found in sample_files directory.")
        print(f"Add files with extensions: {', '.join(ParserManager.get_supported_extensions())}")
        return
    
    # Parse each file
    for filepath in test_files:
        filename = os.path.basename(filepath)
        print(f"\n{'─'*60}")
        print(f"Testing: {filename}")
        print(f"{'─'*60}")
        
        result = ParserManager.parse(filepath)
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            file_type = result.get('file_type', 'unknown')
            print(f"  ✓ Parsed as: {file_type}")
            
            # Show summary based on file type
            if file_type == 'pdf':
                print(f"  ✓ Pages: {result.get('total_pages', 0)}")
            elif file_type == 'word':
                print(f"  ✓ Paragraphs: {result.get('total_paragraphs', 0)}")
                print(f"  ✓ Tables: {result.get('total_tables', 0)}")
            elif file_type == 'excel':
                sheets = result.get('metadata', {}).get('sheet_names', [])
                print(f"  ✓ Sheets: {len(sheets)}")
            elif file_type == 'powerpoint':
                print(f"  ✓ Slides: {result.get('metadata', {}).get('total_slides', 0)}")
            
            # Test output formatting
            json_output = OutputFormatter.to_json(result)
            md_output = OutputFormatter.to_markdown(result)
            
            print(f"  ✓ JSON output: {len(json_output)} chars")
            print(f"  ✓ Markdown output: {len(md_output)} chars")
    
    print(f"\n{'='*60}")
    print("Integration test complete!")
    print("="*60)


if __name__ == '__main__':
    # Run unit tests
    print("Running unit tests...")
    unittest.main(exit=False, verbosity=2)
    
    # Run integration test
    run_integration_test()
