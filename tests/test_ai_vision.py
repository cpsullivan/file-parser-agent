#!/usr/bin/env python3
"""
Test script for AI Vision functionality.

Tests the AIVision module and its integration with the PowerPoint parser.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.ai_vision import AIVision
from core.parser_manager import ParserManager


def test_ai_vision_initialization():
    """Test AIVision initialization."""
    print("=" * 60)
    print("AI VISION INITIALIZATION TEST")
    print("=" * 60)
    
    vision = AIVision()
    
    print(f"API Key configured: {bool(vision.api_key)}")
    print(f"AI Vision enabled: {vision.enabled}")
    print(f"AI Vision available: {vision.is_available()}")
    print(f"Model: {vision.model}")
    
    if not vision.api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not set in environment")
        print("   To enable AI Vision, set the environment variable:")
        print("   export ANTHROPIC_API_KEY=your-api-key")
    
    return vision


def test_fallback_descriptions():
    """Test fallback descriptions when AI is not available."""
    print("\n" + "=" * 60)
    print("FALLBACK DESCRIPTION TEST")
    print("=" * 60)
    
    vision = AIVision()
    
    # Force disable for testing fallbacks
    original_enabled = vision.enabled
    vision.enabled = False
    
    test_cases = ['general', 'chart', 'diagram', 'screenshot']
    
    for analysis_type in test_cases:
        result = vision.analyze_image(b'fake_image_data', 'png', analysis_type)
        print(f"\n{analysis_type}:")
        print(f"  enabled: {result.get('enabled')}")
        print(f"  description: {result.get('description')}")
    
    vision.enabled = original_enabled


def test_pptx_parsing_with_ai():
    """Test PowerPoint parsing with AI Vision enabled."""
    print("\n" + "=" * 60)
    print("POWERPOINT PARSING TEST (with AI Vision)")
    print("=" * 60)
    
    sample_file = os.path.join(PROJECT_ROOT, 'tests', 'sample_files', 'sample.pptx')
    
    if not os.path.exists(sample_file):
        print(f"⚠️  Sample file not found: {sample_file}")
        return
    
    # Parse with AI Vision enabled
    print("\nParsing with AI Vision ENABLED:")
    result = ParserManager.parse(sample_file, enable_ai_vision=True)
    
    print(f"  ai_vision_enabled: {result.get('ai_vision_enabled')}")
    print(f"  ai_vision_available: {result.get('ai_vision_available')}")
    
    if result.get('ai_analysis_summary'):
        summary = result['ai_analysis_summary']
        print(f"  images_total: {summary.get('images_total', 0)}")
        print(f"  images_analyzed: {summary.get('images_analyzed', 0)}")
    
    # Check slides for AI analysis
    slides = result.get('slides', [])
    for slide in slides:
        images = [s for s in slide.get('shapes', []) if s.get('content_type') == 'image']
        if images:
            print(f"\n  Slide {slide['slide_number']} - {len(images)} image(s):")
            for img in images:
                if img.get('ai_analysis'):
                    analysis = img['ai_analysis']
                    if analysis.get('description'):
                        desc = analysis['description'][:100] + '...' if len(analysis.get('description', '')) > 100 else analysis.get('description', '')
                        print(f"    ✓ AI Description: {desc}")
                    elif analysis.get('error'):
                        print(f"    ✗ AI Error: {analysis['error']}")
                else:
                    print(f"    - No AI analysis (format: {img.get('image_format')})")
    
    # Parse without AI Vision for comparison
    print("\nParsing with AI Vision DISABLED:")
    result_no_ai = ParserManager.parse(sample_file, enable_ai_vision=False)
    print(f"  ai_vision_enabled: {result_no_ai.get('ai_vision_enabled')}")
    print(f"  ai_vision_available: {result_no_ai.get('ai_vision_available')}")


def test_image_compression():
    """Test image compression functionality."""
    print("\n" + "=" * 60)
    print("IMAGE COMPRESSION TEST")
    print("=" * 60)
    
    try:
        from PIL import Image
        from io import BytesIO
        
        # Create a test image
        img = Image.new('RGB', (3000, 3000), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        large_image = buffer.getvalue()
        
        print(f"Original image size: {len(large_image) / 1024:.1f} KB")
        
        vision = AIVision()
        compressed, new_format, was_compressed = vision._compress_image(large_image)
        
        print(f"Compressed image size: {len(compressed) / 1024:.1f} KB")
        print(f"New format: {new_format}")
        print(f"Was compressed: {was_compressed}")
        
        # Check it's under the limit
        if len(compressed) <= vision.MAX_IMAGE_SIZE:
            print("✓ Compressed image is under size limit")
        else:
            print("✗ Compressed image exceeds size limit")
            
    except ImportError:
        print("⚠️  Pillow not installed, skipping compression test")


def test_media_type_mapping():
    """Test media type mapping."""
    print("\n" + "=" * 60)
    print("MEDIA TYPE MAPPING TEST")
    print("=" * 60)
    
    vision = AIVision()
    
    test_cases = [
        ('png', 'image/png'),
        ('jpg', 'image/jpeg'),
        ('jpeg', 'image/jpeg'),
        ('gif', 'image/gif'),
        ('webp', 'image/webp'),
    ]
    
    all_passed = True
    for format_in, expected in test_cases:
        result = vision._get_media_type(format_in)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"  {status} {format_in} -> {result} (expected: {expected})")
    
    print(f"\n{'All tests passed!' if all_passed else 'Some tests failed!'}")


def main():
    """Run all AI Vision tests."""
    print("\n" + "=" * 60)
    print("FILE PARSER AGENT - AI VISION TESTS")
    print("=" * 60)
    
    # Test initialization
    vision = test_ai_vision_initialization()
    
    # Test fallback descriptions
    test_fallback_descriptions()
    
    # Test media type mapping
    test_media_type_mapping()
    
    # Test compression
    test_image_compression()
    
    # Test PowerPoint parsing
    test_pptx_parsing_with_ai()
    
    print("\n" + "=" * 60)
    print("AI VISION TESTS COMPLETE")
    print("=" * 60)
    
    if vision.is_available():
        print("✓ AI Vision is fully operational")
    else:
        print("⚠️  AI Vision running in fallback mode")
        print("   Set ANTHROPIC_API_KEY to enable image analysis")


if __name__ == '__main__':
    main()
