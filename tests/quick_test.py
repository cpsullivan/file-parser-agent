#!/usr/bin/env python3
"""Quick integration test - parse all sample files and show results."""

import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.parser_manager import ParserManager
from core.output_formatter import OutputFormatter
from core.file_manager import FileManager


def main():
    sample_dir = os.path.join(PROJECT_ROOT, 'tests', 'sample_files')
    
    print("=" * 70)
    print("FILE PARSER AGENT - INTEGRATION TEST")
    print("=" * 70)
    
    # Test each file type
    test_files = [
        ('sample.pdf', 'PDF'),
        ('sample.docx', 'Word'),
        ('sample.xlsx', 'Excel'),
        ('sample.pptx', 'PowerPoint'),
    ]
    
    results = {}
    
    for filename, file_type in test_files:
        filepath = os.path.join(sample_dir, filename)
        
        print(f"\n{'─' * 70}")
        print(f"Testing {file_type}: {filename}")
        print(f"{'─' * 70}")
        
        if not os.path.exists(filepath):
            print(f"  ⚠ File not found: {filepath}")
            continue
        
        # Parse the file
        result = ParserManager.parse(filepath)
        results[file_type] = result
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
            continue
        
        print(f"  ✓ File Type: {result.get('file_type')}")
        print(f"  ✓ Parsed At: {result.get('parsed_at')}")
        
        # Show file-specific info
        if file_type == 'PDF':
            print(f"  ✓ Total Pages: {result.get('total_pages', 0)}")
            metadata = result.get('metadata', {})
            if metadata.get('title'):
                print(f"  ✓ Title: {metadata['title']}")
            
            # Show first page preview
            pages = result.get('pages', [])
            if pages:
                preview = pages[0].get('text', '')[:100]
                print(f"  ✓ Page 1 Preview: {preview}...")
        
        elif file_type == 'Word':
            print(f"  ✓ Paragraphs: {result.get('total_paragraphs', 0)}")
            print(f"  ✓ Tables: {result.get('total_tables', 0)}")
            print(f"  ✓ Images: {result.get('image_count', 0)}")
            
            # Show first paragraph
            paras = result.get('paragraphs', [])
            if paras:
                print(f"  ✓ First Para: {paras[0].get('text', '')[:60]}...")
        
        elif file_type == 'Excel':
            metadata = result.get('metadata', {})
            sheets = metadata.get('sheet_names', [])
            print(f"  ✓ Sheets: {len(sheets)} - {', '.join(sheets)}")
            
            # Show first sheet data preview
            sheet_data = result.get('sheets', [])
            if sheet_data and sheet_data[0].get('data'):
                first_row = sheet_data[0]['data'][0]
                print(f"  ✓ First Row: {first_row}")
        
        elif file_type == 'PowerPoint':
            metadata = result.get('metadata', {})
            print(f"  ✓ Total Slides: {metadata.get('total_slides', 0)}")
            
            # Show slide titles
            slides = result.get('slides', [])
            for slide in slides[:3]:
                title = slide.get('title', 'Untitled')
                print(f"    - Slide {slide['slide_number']}: {title}")
    
    # Test output formatting
    print(f"\n{'=' * 70}")
    print("OUTPUT FORMATTING TEST")
    print("=" * 70)
    
    if 'Word' in results:
        word_result = results['Word']
        
        # JSON output
        json_output = OutputFormatter.to_json(word_result)
        print(f"\n✓ JSON output length: {len(json_output)} characters")
        
        # Validate JSON
        try:
            json.loads(json_output)
            print("✓ JSON is valid")
        except json.JSONDecodeError as e:
            print(f"❌ JSON validation error: {e}")
        
        # Markdown output
        md_output = OutputFormatter.to_markdown(word_result)
        print(f"✓ Markdown output length: {len(md_output)} characters")
        
        # Show markdown preview
        md_lines = md_output.split('\n')[:10]
        print("\nMarkdown Preview:")
        print("-" * 40)
        for line in md_lines:
            print(f"  {line}")
        print("  ...")
    
    # Test file manager
    print(f"\n{'=' * 70}")
    print("FILE MANAGER TEST")
    print("=" * 70)
    
    fm = FileManager(
        upload_dir=os.path.join(PROJECT_ROOT, 'uploads'),
        output_dir=os.path.join(PROJECT_ROOT, 'outputs')
    )
    
    if 'Excel' in results:
        # Save output
        json_content = OutputFormatter.to_json(results['Excel'])
        saved_filename = fm.save_output(json_content, 'sample.xlsx', 'json')
        print(f"\n✓ Saved output: {saved_filename}")
        
        # List outputs
        outputs = fm.list_outputs()
        print(f"✓ Total outputs: {len(outputs)}")
        
        # Read back
        read_content = fm.read_output(saved_filename)
        if read_content:
            print(f"✓ Read back: {len(read_content)} characters")
        
        # Clean up
        fm.delete_output(saved_filename)
        print(f"✓ Deleted test output")
    
    print(f"\n{'=' * 70}")
    print("ALL TESTS COMPLETE ✓")
    print("=" * 70)


if __name__ == '__main__':
    main()
