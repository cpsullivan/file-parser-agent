#!/usr/bin/env python3
"""
Test script for MCP Server functionality.

Tests the MCP server handlers without running the full server.
"""

import asyncio
import os
import sys
import json
import base64

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


async def run_tests():
    """Run all MCP handler tests."""
    print("=" * 60)
    print("MCP SERVER HANDLER TESTS")
    print("=" * 60)
    
    # Import handlers
    from mcp_server import (
        handle_parse_document,
        handle_analyze_image,
        handle_format_output,
        handle_save_output,
        handle_list_outputs,
        handle_read_output,
        handle_delete_output,
        handle_get_info,
        MCP_AVAILABLE,
        TOOLS
    )
    
    print(f"\nMCP library available: {MCP_AVAILABLE}")
    print(f"Tools defined: {len(TOOLS)}")
    for tool in TOOLS:
        print(f"  - {tool['name']}")
    
    passed = 0
    failed = 0
    
    # Test 1: get_info
    print("\n1. Testing get_info...")
    try:
        result = await handle_get_info({})
        if result.get('success'):
            print(f"   ✓ Version: {result.get('version')}")
            print(f"   ✓ Supported types: {result.get('supported_types')}")
            print(f"   ✓ AI Vision available: {result.get('ai_vision', {}).get('available')}")
            passed += 1
        else:
            print(f"   ✗ Error: {result.get('error')}")
            failed += 1
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        failed += 1
    
    # Test 2: parse_document with file_path
    print("\n2. Testing parse_document (file_path)...")
    try:
        result = await handle_parse_document({
            'file_path': os.path.join(PROJECT_ROOT, 'tests/sample_files/sample.pdf'),
            'output_format': 'json'
        })
        if result.get('success'):
            data = result.get('data', {})
            print(f"   ✓ Parsed PDF: {data.get('total_pages')} pages")
            passed += 1
        else:
            print(f"   ✗ Error: {result.get('error')}")
            failed += 1
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        failed += 1
    
    # Test 3: parse_document with base64
    print("\n3. Testing parse_document (base64)...")
    try:
        with open(os.path.join(PROJECT_ROOT, 'tests/sample_files/sample.docx'), 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
        
        result = await handle_parse_document({
            'file_content': content,
            'filename': 'sample.docx',
            'output_format': 'markdown'
        })
        if result.get('success'):
            print(f"   ✓ Parsed Word from base64")
            print(f"   ✓ Format: {result.get('format')}")
            passed += 1
        else:
            print(f"   ✗ Error: {result.get('error')}")
            failed += 1
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        failed += 1
    
    # Test 4: format_output
    print("\n4. Testing format_output...")
    try:
        test_data = {
            'filename': 'test.pdf',
            'file_type': 'pdf',
            'parsed_at': '2026-02-04T12:00:00',
            'total_pages': 1,
            'pages': [{'page_number': 1, 'text': 'Test content', 'char_count': 12}]
        }
        result = await handle_format_output({
            'parsed_data': test_data,
            'format': 'markdown'
        })
        if result.get('success'):
            print(f"   ✓ Formatted to markdown: {len(result.get('formatted', ''))} chars")
            passed += 1
        else:
            print(f"   ✗ Error: {result.get('error')}")
            failed += 1
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        failed += 1
    
    # Test 5: save_output
    print("\n5. Testing save_output...")
    saved_filename = None
    try:
        result = await handle_save_output({
            'content': json.dumps(test_data, indent=2),
            'original_filename': 'mcp_test.pdf',
            'format': 'json'
        })
        if result.get('success'):
            saved_filename = result.get('saved_as')
            print(f"   ✓ Saved as: {saved_filename}")
            passed += 1
        else:
            print(f"   ✗ Error: {result.get('error')}")
            failed += 1
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        failed += 1
    
    # Test 6: list_outputs
    print("\n6. Testing list_outputs...")
    try:
        result = await handle_list_outputs({})
        if result.get('success'):
            print(f"   ✓ Found {result.get('count')} output file(s)")
            passed += 1
        else:
            print(f"   ✗ Error: {result.get('error')}")
            failed += 1
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        failed += 1
    
    # Test 7: read_output
    if saved_filename:
        print("\n7. Testing read_output...")
        try:
            result = await handle_read_output({'filename': saved_filename})
            if result.get('success'):
                content = result.get('content', '')
                print(f"   ✓ Read file: {len(content)} chars")
                passed += 1
            else:
                print(f"   ✗ Error: {result.get('error')}")
                failed += 1
        except Exception as e:
            print(f"   ✗ Exception: {e}")
            failed += 1
        
        # Test 8: delete_output
        print("\n8. Testing delete_output...")
        try:
            result = await handle_delete_output({'filename': saved_filename})
            if result.get('success'):
                print(f"   ✓ Deleted: {saved_filename}")
                passed += 1
            else:
                print(f"   ✗ Error: {result.get('error')}")
                failed += 1
        except Exception as e:
            print(f"   ✗ Exception: {e}")
            failed += 1
    else:
        print("\n7-8. Skipping read/delete tests (no saved file)")
        failed += 2
    
    # Test 9: analyze_image
    print("\n9. Testing analyze_image...")
    try:
        from PIL import Image
        from io import BytesIO
        
        img = Image.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        result = await handle_analyze_image({
            'image_content': image_data,
            'image_format': 'png',
            'analysis_type': 'general'
        })
        if result.get('success'):
            if result.get('enabled'):
                desc = result.get('description', '')
                print(f"   ✓ AI analysis: {desc[:50]}...")
            else:
                print(f"   ✓ AI not available (expected without API key)")
            passed += 1
        else:
            print(f"   ✗ Error: {result.get('error')}")
            failed += 1
    except ImportError:
        print("   ⚠ Pillow not available, skipping")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        failed += 1
    
    # Test 10: error handling
    print("\n10. Testing error handling...")
    try:
        result = await handle_parse_document({
            'file_path': '/nonexistent/file.pdf'
        })
        if not result.get('success'):
            print(f"   ✓ Correctly returned error for missing file")
            passed += 1
        else:
            print(f"   ✗ Should have returned error")
            failed += 1
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def test_mcp_import():
    """Test MCP library import."""
    print("\n" + "=" * 60)
    print("MCP LIBRARY CHECK")
    print("=" * 60)
    
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
        print("✓ MCP library imported successfully")
        return True
    except ImportError as e:
        print(f"⚠ MCP library not available: {e}")
        print("  Install with: pip install mcp")
        return False


def main():
    """Run all MCP tests."""
    mcp_available = test_mcp_import()
    
    # Run handler tests
    success = asyncio.run(run_tests())
    
    if not mcp_available:
        print("\n⚠️  Note: MCP library not fully installed.")
        print("   Handlers work, but server may not run.")
        print("   Install with: pip install mcp")
    
    if success:
        print("\n✓ All MCP handler tests passed!")
    else:
        print("\n✗ Some tests failed")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
