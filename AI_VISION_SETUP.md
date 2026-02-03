# AI Vision Setup Guide

## Overview

The File Parser Agent now includes **AI-powered image description** using Claude Vision API. This feature automatically generates detailed descriptions of images found in PowerPoint presentations.

---

## 🔑 Get Your API Key

### Option 1: Anthropic Console (Recommended)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy your API key (starts with `sk-ant-...`)

### Option 2: Use Existing Key

If you already have an Anthropic API key for Claude, you can use the same key.

---

## ⚙️ Configure the API Key

### Windows (Command Prompt)

```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Windows (PowerShell)

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

### Permanent Setup (Windows)

1. Open System Properties → Environment Variables
2. Add a new User variable:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Value**: Your API key
3. Restart your terminal/IDE

### Linux/Mac

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

---

## 🚀 Start the Application

```bash
python app.py
```

The application will automatically detect if the API key is set and enable AI vision.

---

## 📸 How It Works

### Automatic Image Analysis

When you upload a PowerPoint file, the parser will:

1. **Detect all images** on each slide
2. **Extract image metadata** (dimensions, format, size)
3. **Send to Claude Vision API** for analysis
4. **Generate detailed descriptions** of what's in each image
5. **Include in parsed output** (JSON or Markdown)

### What You Get

**Before AI Vision:**
```json
{
  "image_number": 1,
  "description": "[AI description would be generated here]",
  "note": "AI vision analysis recommended"
}
```

**After AI Vision:**
```json
{
  "image_number": 1,
  "image_format": "png",
  "image_width": 1920,
  "image_height": 1080,
  "description": "A professional bar chart showing quarterly revenue growth from Q1 to Q4 2025. The chart displays four blue bars increasing in height from left to right, representing revenue values of $2M, $3.5M, $4.2M, and $5M respectively. The chart has a white background with a title 'Quarterly Revenue 2025' at the top. Grid lines help show the scale, and each bar is labeled with its exact value.",
  "ai_analysis": {
    "model": "claude-3-5-sonnet-20241022",
    "confidence": "high",
    "tokens_used": 245
  }
}
```

---

## 💰 Pricing

### Claude Vision API Costs

- **Model**: Claude 3.5 Sonnet (Vision)
- **Input**: ~$3.00 per million input tokens
- **Output**: ~$15.00 per million output tokens

### Estimated Costs per Image

- Average image: 200-500 input tokens
- Average description: 100-200 output tokens
- **Cost per image**: ~$0.003-0.005 (less than 1 cent)

### Example Scenarios

| Presentation | Images | Estimated Cost |
|--------------|--------|----------------|
| 10 slides, 5 images | 5 | $0.02 |
| 20 slides, 15 images | 15 | $0.06 |
| 50 slides, 30 images | 30 | $0.12 |

**Very affordable for typical presentations!**

---

## 🎯 Testing AI Vision

### Test 1: Simple Image

Upload a PowerPoint with a logo or icon:

```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@presentation.pptx" \
  -F "format=json"
```

Check the output for image descriptions.

### Test 2: Chart Image

Upload a PowerPoint with embedded Excel charts (as images):

The parser will detect them and describe:
- Chart type
- Data shown
- Trends and patterns
- Key insights

### Test 3: Complex Graphics

Upload slides with:
- Diagrams
- Screenshots
- Photos
- Infographics

Claude Vision will describe the visual content in detail.

---

## 🔧 Configuration Options

### Disable AI Vision Temporarily

```bash
set ENABLE_AI_VISION=false
python app.py
```

This will skip AI analysis and use placeholder descriptions.

### Check Status

When the server starts, you'll see:

```
AI Vision: ENABLED (API key detected)
```

or

```
AI Vision: DISABLED (Set ANTHROPIC_API_KEY to enable)
```

---

## 🎨 What Claude Vision Can Describe

### Excellent Results

- ✅ Charts and graphs
- ✅ Diagrams and flowcharts
- ✅ Screenshots of applications
- ✅ Photos of people, places, products
- ✅ Logos and branding elements
- ✅ Infographics
- ✅ Tables (visual)
- ✅ Icons and symbols

### Specialized Analysis

For **charts**, Claude Vision provides:
- Chart type identification
- Axis labels and units
- Data ranges and values
- Trends and patterns
- Key insights

For **diagrams**, Claude Vision describes:
- Structure and layout
- Components and connections
- Text labels
- Hierarchies and flows

---

## 🚨 Troubleshooting

### Error: "AI vision disabled - ANTHROPIC_API_KEY not set"

**Solution:** Set the environment variable before starting the app.

### Error: "Authentication failed"

**Solution:** Check that your API key is correct and starts with `sk-ant-`.

### Error: "Rate limit exceeded"

**Solution:** Wait a few minutes or upgrade your Anthropic plan.

### Images not being described

1. Check that images are actually in the PowerPoint (not shapes/drawings)
2. Verify API key is set
3. Check server logs for errors

---

## 📊 Output Format

### JSON Output with AI Vision

```json
{
  "slides": [
    {
      "slide_number": 1,
      "title": "Quarterly Results",
      "shapes": [
        {
          "content_type": "image",
          "image_number": 1,
          "image_format": "png",
          "image_width": 1920,
          "image_height": 1080,
          "description": "Professional bar chart showing Q1-Q4 revenue...",
          "ai_analysis": {
            "enabled": true,
            "model": "claude-3-5-sonnet-20241022",
            "confidence": "high",
            "tokens_used": 245
          }
        }
      ]
    }
  ]
}
```

### Markdown Output with AI Vision

```markdown
## Slide 1: Quarterly Results

### Images

**Image 1** (png, 1920x1080)
Professional bar chart showing quarterly revenue growth...
```

---

## 🔐 Security Notes

- API keys are stored as environment variables only
- Never commit API keys to git
- Keys are not logged or saved by the application
- Each request is authenticated individually

---

## 📚 Additional Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Vision Guide](https://docs.anthropic.com/claude/docs/vision)
- [API Pricing](https://www.anthropic.com/pricing)

---

## ✅ Quick Start Checklist

- [ ] Get Anthropic API key
- [ ] Set `ANTHROPIC_API_KEY` environment variable
- [ ] Start application (`python app.py`)
- [ ] Verify "AI Vision: ENABLED" message
- [ ] Upload a PowerPoint with images
- [ ] Check parsed output for AI descriptions

---

**Ready to go!** Your File Parser Agent now has AI-powered image understanding. 🎉
