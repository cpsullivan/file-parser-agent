"""Test which Claude vision models are available"""
import os
import base64
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# Create a tiny 1x1 PNG image
test_img = base64.b64encode(
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00'
    b'\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
).decode()

models_to_test = [
    'claude-3-5-sonnet-20240620',
    'claude-3-5-sonnet-20241022',
    'claude-3-opus-20240229',
]

print("Testing vision models...\n")

for model in models_to_test:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': 'image/png',
                            'data': test_img
                        }
                    },
                    {
                        'type': 'text',
                        'text': 'What color is this?'
                    }
                ]
            }]
        )
        print(f"[OK] {model} - WORKS")
    except anthropic.NotFoundError:
        print(f"[NO] {model} - 404 Not Found")
    except Exception as e:
        print(f"[??] {model} - Error: {str(e)[:80]}")
