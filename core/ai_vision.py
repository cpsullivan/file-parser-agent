"""
AI Vision Module - Image analysis using Claude API.

Provides intelligent image descriptions for PowerPoint presentations,
including general image analysis and specialized chart/diagram analysis.
"""

import os
import base64
from io import BytesIO
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIVision:
    """
    Claude Vision integration for image analysis.
    
    Features:
    - General image description
    - Specialized chart analysis
    - Diagram/flowchart analysis
    - Automatic image compression for API limits
    - Graceful degradation when API key not configured
    """
    
    # Maximum image size for API (5MB)
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024
    
    # Supported image formats
    SUPPORTED_FORMATS: list = ['png', 'jpg', 'jpeg', 'gif', 'webp']
    
    # Default model for vision
    DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
    
    def __init__(self):
        """Initialize AI Vision with API client."""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.enabled = bool(self.api_key)
        self.client = None
        self.model = os.getenv('VISION_MODEL', self.DEFAULT_MODEL)
        
        if self.enabled:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                self.enabled = False
            except Exception:
                self.enabled = False
    
    def is_available(self) -> bool:
        """Check if AI Vision is available."""
        return self.enabled and self.client is not None
    
    def analyze_image(
        self,
        image_data: bytes,
        image_format: str,
        analysis_type: str = 'general',
        context: str = ''
    ) -> Dict[str, Any]:
        """
        Analyze an image using Claude Vision.
        
        Args:
            image_data: Raw image bytes
            image_format: Image format (png, jpg, etc.)
            analysis_type: Type of analysis ('general', 'chart', 'diagram')
            context: Additional context about the image location
            
        Returns:
            Dictionary with analysis results:
            - enabled: Whether AI was used
            - description: The generated description
            - model: Model used for analysis
            - analysis_type: Type of analysis performed
            - tokens_used: Number of output tokens
            - error: Error message if failed
        """
        # Check if enabled
        if not self.is_available():
            return {
                'enabled': False,
                'error': 'AI Vision not available (API key not configured or anthropic package not installed)',
                'description': self._get_fallback_description(analysis_type)
            }
        
        # Validate format
        image_format = image_format.lower().lstrip('.')
        if image_format not in self.SUPPORTED_FORMATS:
            return {
                'enabled': False,
                'error': f'Unsupported image format: {image_format}',
                'description': f'Image ({image_format} format)'
            }
        
        # Compress if needed
        original_size = len(image_data)
        if original_size > self.MAX_IMAGE_SIZE:
            image_data, image_format, was_compressed = self._compress_image(image_data)
            if was_compressed:
                compressed_size = len(image_data)
        else:
            was_compressed = False
        
        # Build prompt
        prompt = self._build_prompt(analysis_type, context)
        
        try:
            # Encode image
            b64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Map format to media type
            media_type = self._get_media_type(image_format)
            
            # Call API
            response = self.client.messages.create(
                model=self.model,
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
                                    "data": b64_image
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
            
            # Extract response
            description = response.content[0].text
            
            result = {
                'enabled': True,
                'description': description,
                'model': self.model,
                'analysis_type': analysis_type,
                'tokens_used': response.usage.output_tokens
            }
            
            if was_compressed:
                result['note'] = f'Image compressed from {original_size/1024:.1f}KB to {len(image_data)/1024:.1f}KB'
            
            return result
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Handle specific error types
            if 'RateLimitError' in error_type:
                error_msg = 'Rate limited. Please try again later.'
            elif 'AuthenticationError' in error_type:
                error_msg = 'Invalid API key.'
            elif 'InvalidRequestError' in error_type:
                error_msg = f'Invalid request: {error_msg}'
            
            return {
                'enabled': True,
                'error': error_msg,
                'analysis_type': analysis_type,
                'description': self._get_fallback_description(analysis_type)
            }
    
    def _build_prompt(self, analysis_type: str, context: str) -> str:
        """
        Build appropriate prompt based on analysis type.
        
        Args:
            analysis_type: Type of analysis to perform
            context: Additional context
            
        Returns:
            Prompt string for the API
        """
        if analysis_type == 'chart':
            prompt = """Analyze this chart or data visualization. Provide a concise description including:

1. **Chart Type**: (bar, line, pie, scatter, etc.)
2. **Data Shown**: What data or metrics are being visualized
3. **Key Insights**: Main trends, patterns, or notable data points
4. **Axes/Labels**: Description of axes, units, and labels if visible
5. **Summary**: One sentence summary of what the chart communicates

Be specific and factual. If you can read specific values, include them."""

        elif analysis_type == 'diagram':
            prompt = """Analyze this diagram. Provide a concise description including:

1. **Diagram Type**: (flowchart, org chart, process diagram, architecture, etc.)
2. **Main Components**: Key elements or nodes in the diagram
3. **Relationships**: How components connect or relate to each other
4. **Flow/Direction**: The overall flow or hierarchy if applicable
5. **Text Labels**: Any important text labels or annotations

Focus on structure and relationships."""

        elif analysis_type == 'screenshot':
            prompt = """Analyze this screenshot. Provide a concise description including:

1. **Application/Context**: What application or interface is shown
2. **Main Elements**: Key UI elements, buttons, or sections visible
3. **Content**: Any text content or data displayed
4. **State**: Current state or what action is being shown
5. **Purpose**: What the screenshot appears to demonstrate

Transcribe any visible text accurately."""

        else:  # general
            prompt = """Describe this image concisely. Include:

1. **Image Type**: (photo, illustration, icon, logo, graphic, etc.)
2. **Main Subject**: What the image primarily shows
3. **Key Elements**: Important visual elements and their arrangement
4. **Text Content**: Any visible text (transcribe accurately)
5. **Purpose**: Apparent purpose in a presentation context

Be factual and specific. Keep the description under 150 words."""

        if context:
            prompt += f"\n\n**Context**: {context}"
        
        return prompt
    
    def _compress_image(self, image_data: bytes) -> Tuple[bytes, str, bool]:
        """
        Compress image to fit within API limits.
        
        Args:
            image_data: Original image bytes
            
        Returns:
            Tuple of (compressed_data, format, was_compressed)
        """
        try:
            from PIL import Image
            
            img = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed (for JPEG compression)
            if img.mode in ('RGBA', 'P', 'LA'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if very large
            max_dimension = 2000
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Compress with decreasing quality until under limit
            output = BytesIO()
            quality = 85
            
            while quality >= 20:
                output.seek(0)
                output.truncate()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                
                if output.tell() <= self.MAX_IMAGE_SIZE:
                    break
                    
                quality -= 10
            
            return output.getvalue(), 'jpeg', True
            
        except ImportError:
            # Pillow not installed, return original
            return image_data, 'png', False
        except Exception:
            # Compression failed, return original
            return image_data, 'png', False
    
    def _get_media_type(self, image_format: str) -> str:
        """
        Convert image format to MIME type.
        
        Args:
            image_format: Image format string
            
        Returns:
            MIME type string
        """
        format_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return format_map.get(image_format.lower(), 'image/png')
    
    def _get_fallback_description(self, analysis_type: str) -> str:
        """
        Get fallback description when AI is not available.
        
        Args:
            analysis_type: Type of analysis requested
            
        Returns:
            Fallback description string
        """
        fallbacks = {
            'chart': 'Chart or data visualization (AI analysis not available)',
            'diagram': 'Diagram or flowchart (AI analysis not available)',
            'screenshot': 'Screenshot (AI analysis not available)',
            'general': 'Image (AI analysis not available)'
        }
        return fallbacks.get(analysis_type, 'Image (AI analysis not available)')


# Convenience function for direct use
def analyze_image(
    image_data: bytes,
    image_format: str,
    analysis_type: str = 'general',
    context: str = ''
) -> Dict[str, Any]:
    """
    Analyze an image using AI Vision.
    
    This is a convenience function that creates an AIVision instance
    and calls analyze_image. For multiple analyses, create an AIVision
    instance directly to reuse the client connection.
    
    Args:
        image_data: Raw image bytes
        image_format: Image format (png, jpg, etc.)
        analysis_type: Type of analysis ('general', 'chart', 'diagram')
        context: Additional context about the image
        
    Returns:
        Analysis result dictionary
    """
    vision = AIVision()
    return vision.analyze_image(image_data, image_format, analysis_type, context)
