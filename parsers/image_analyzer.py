"""Image Analyzer - AI-powered image description using Claude Vision"""

import base64
import os
import io
from typing import Optional, Dict
import anthropic
from PIL import Image

def compress_image_if_needed(image_bytes: bytes, max_size_bytes: int = 4_500_000) -> tuple[bytes, bool]:
    """
    Compress image if it exceeds the size limit (default 4.5MB to stay under 5MB API limit)

    Returns:
        tuple: (compressed_image_bytes, was_compressed)
    """
    if len(image_bytes) <= max_size_bytes:
        return image_bytes, False

    # Load image
    img = Image.open(io.BytesIO(image_bytes))

    # Calculate resize ratio to reduce file size
    # Start with 70% of original size and adjust if needed
    scale = 0.7
    quality = 85

    for attempt in range(3):  # Try up to 3 times
        # Resize image
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()
        if img.mode == 'RGBA':
            resized.save(output, format='PNG', optimize=True)
        else:
            resized.save(output, format='JPEG', quality=quality, optimize=True)

        compressed_bytes = output.getvalue()

        if len(compressed_bytes) <= max_size_bytes:
            return compressed_bytes, True

        # Reduce quality/scale for next attempt
        scale *= 0.8
        quality -= 10

    # If still too large, return best effort
    return compressed_bytes, True

def get_image_description(image_bytes: bytes, image_format: str, context: str = "") -> Dict[str, any]:
    """
    Generate a detailed description of an image using Claude Vision API

    Args:
        image_bytes: Raw image data
        image_format: Image format (png, jpg, etc.)
        context: Optional context about where the image appears (e.g., "Slide 1 title slide")

    Returns:
        dict: Contains description, confidence, and metadata
    """
    # Get API key from environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        return {
            'description': '[AI vision disabled - ANTHROPIC_API_KEY not set]',
            'enabled': False,
            'note': 'Set ANTHROPIC_API_KEY environment variable to enable AI image descriptions'
        }

    try:
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=api_key)

        # Compress image if needed (API limit is 5MB)
        original_size = len(image_bytes)
        image_bytes, was_compressed = compress_image_if_needed(image_bytes)

        # Convert image to base64
        image_base64 = base64.standard_b64encode(image_bytes).decode('utf-8')

        # Determine media type
        media_type_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        media_type = media_type_map.get(image_format.lower(), 'image/png')

        # Construct prompt based on context
        if context:
            prompt = f"""Analyze this image from {context} in a business presentation.

Provide a detailed description that includes:
1. What the image shows (objects, people, text, graphics)
2. The style and type (photo, diagram, chart, icon, logo, screenshot, etc.)
3. Key visual elements and their arrangement
4. Any text visible in the image
5. The apparent purpose or message of the image
6. How it relates to a business/professional presentation

Be concise but thorough. Focus on factual visual content."""
        else:
            prompt = """Describe this image in detail for someone who cannot see it.

Include:
1. What is shown in the image (objects, people, text, graphics)
2. The type and style of image (photo, diagram, icon, chart, etc.)
3. Layout and composition
4. Any visible text or labels
5. The apparent purpose or context

Be descriptive and specific."""

        # Call Claude Vision API
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        # Extract description
        description = message.content[0].text

        result = {
            'description': description,
            'enabled': True,
            'model': 'claude-3-5-sonnet',
            'confidence': 'high',  # Claude doesn't provide confidence scores, but quality is consistently high
            'tokens_used': message.usage.input_tokens + message.usage.output_tokens,
            'note': 'AI-generated description using Claude Vision'
        }

        if was_compressed:
            result['image_compressed'] = True
            result['original_size_bytes'] = original_size
            result['compressed_size_bytes'] = len(image_bytes)
            result['compression_note'] = f'Image compressed from {original_size/1024/1024:.1f}MB to {len(image_bytes)/1024/1024:.1f}MB for API'

        return result

    except anthropic.AuthenticationError:
        return {
            'description': '[AI vision authentication failed - check ANTHROPIC_API_KEY]',
            'enabled': False,
            'error': 'Authentication failed'
        }
    except anthropic.RateLimitError:
        return {
            'description': '[AI vision rate limit exceeded - try again later]',
            'enabled': False,
            'error': 'Rate limit exceeded'
        }
    except Exception as e:
        return {
            'description': f'[AI vision error: {str(e)[:100]}]',
            'enabled': False,
            'error': str(e)
        }


def analyze_chart_image(image_bytes: bytes, image_format: str, chart_type: str = "") -> Dict[str, any]:
    """
    Specialized analysis for chart images

    Args:
        image_bytes: Raw image data
        image_format: Image format
        chart_type: Type of chart if known (bar, line, pie, etc.)

    Returns:
        dict: Contains description with focus on data visualization
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        return {
            'description': '[AI vision disabled - ANTHROPIC_API_KEY not set]',
            'enabled': False
        }

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Compress image if needed
        original_size = len(image_bytes)
        image_bytes, was_compressed = compress_image_if_needed(image_bytes)

        image_base64 = base64.standard_b64encode(image_bytes).decode('utf-8')

        media_type_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }
        media_type = media_type_map.get(image_format.lower(), 'image/png')

        prompt = f"""Analyze this {chart_type + ' ' if chart_type else ''}chart/data visualization.

Provide:
1. Chart type (bar, line, pie, scatter, etc.)
2. What data is being shown (variables, categories)
3. Key trends or patterns visible
4. Axis labels and units if visible
5. Data ranges (highest/lowest values if readable)
6. Title or caption if present
7. Key insights or takeaways

Focus on the data story being told."""

        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=600,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        description = message.content[0].text

        result = {
            'description': description,
            'enabled': True,
            'model': 'claude-3-5-sonnet',
            'analysis_type': 'chart_specialized',
            'tokens_used': message.usage.input_tokens + message.usage.output_tokens
        }

        if was_compressed:
            result['image_compressed'] = True
            result['original_size_bytes'] = original_size
            result['compressed_size_bytes'] = len(image_bytes)

        return result

    except Exception as e:
        return {
            'description': f'[Chart analysis error: {str(e)[:100]}]',
            'enabled': False,
            'error': str(e)
        }
