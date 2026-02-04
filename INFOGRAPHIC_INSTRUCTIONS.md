# File Parser Agent - Infographic Generation Instructions

## Overview

Generate a professional infographic visualizing the File Parser Agent system architecture and data flow. The source diagram shows a complex node-based flow chart that should be transformed into a clean, visually appealing infographic suitable for stakeholder presentations.

---

## Infographic Specifications

### Title
**"File Parser Agent - System Architecture"**

### Subtitle
"Transform business documents into structured data"

### Dimensions
- Recommended: 1920 x 1080 (landscape) or 1080 x 1920 (portrait)
- Alternative: 11" x 17" for print

### Color Scheme
Use a professional color palette with distinct colors for each component type:

| Component Type | Color | Hex Code |
|----------------|-------|----------|
| Core System | Blue | #3B82F6 |
| Input Formats | Green | #10B981 |
| Parsers | Cyan/Teal | #06B6D4 |
| AI Features | Purple | #8B5CF6 |
| Output Formats | Orange | #F59E0B |
| Integrations | Pink/Magenta | #EC4899 |
| Storage | Gray | #6B7280 |

---

## Key Elements to Visualize

### 1. Central Hub (Core System)
**Position:** Center-left of infographic

Visualize as a prominent central element:
- **"File Parser Agent"** - Main system name
- Tagline: "Document Processing Engine"
- Icon: Document with gear/cog symbol

### 2. Input Section (Left Side)
**Header:** "Supported Inputs"

Show 4 document types flowing INTO the central hub:

| Format | Icon | Label |
|--------|------|-------|
| PDF | PDF icon (red) | ".pdf" |
| Word | Word icon (blue) | ".docx / .doc" |
| Excel | Excel icon (green) | ".xlsx / .xls" |
| PowerPoint | PPT icon (orange) | ".pptx / .ppt" |

**Visual treatment:**
- Arrange as 4 cards/badges on the left
- Arrows flowing right toward central hub
- Include "50MB max" notation

### 3. Processing Layer (Center)
**Header:** "Extraction Engine"

Show the 4 parser modules:

```
┌─────────────────┐
│   PDF Parser    │ → Text, Pages, Metadata
├─────────────────┤
│   Word Parser   │ → Paragraphs, Tables, Embedded Objects
├─────────────────┤
│  Excel Parser   │ → Sheets, Cell Data, Formulas
├─────────────────┤
│  PPTX Parser    │ → Slides, Shapes, Notes, Images
└─────────────────┘
```

**Visual treatment:**
- Stack vertically or arrange in 2x2 grid
- Each parser shows what it extracts
- Use matching colors to input formats

### 4. AI Vision Module (Center-Top)
**Header:** "AI-Powered Analysis"

Highlight as a premium feature:
- **Claude Vision API** integration
- Icon: Eye or brain symbol
- Capabilities:
  - "Image Descriptions"
  - "Chart Analysis"
  - "Visual Content Understanding"

**Visual treatment:**
- Distinct purple/violet color
- Sparkle or AI-themed iconography
- Connect to PPTX Parser specifically

### 5. Output Section (Right Side)
**Header:** "Output Formats"

Show 4 output options flowing OUT from processing:

| Format | Icon | Use Case |
|--------|------|----------|
| JSON | { } brackets | "Structured Data" |
| Markdown | M↓ icon | "Documentation" |
| CSV | Table icon | "Spreadsheet Data" |
| TXT | Text icon | "Plain Text" |

**Visual treatment:**
- Arrange as 4 cards/badges on the right
- Arrows flowing right from processing layer
- Color-code by format type

### 6. Integration Methods (Bottom)
**Header:** "Access Methods"

Show 4 ways to use the system:

| Method | Icon | Description |
|--------|------|-------------|
| Web UI | Browser | "Drag & Drop Interface" |
| CLI | Terminal | "Command Line Tool" |
| Python API | Python logo | "Programmatic Access" |
| MCP Server | Claude icon | "Claude Desktop Integration" |

**Visual treatment:**
- Horizontal row at bottom
- Each as a rounded card with icon
- Equal spacing

### 7. Data Flow Arrows
Connect all sections with clear directional arrows:

```
[Inputs] → [Parsers] → [AI Vision] → [Formatters] → [Outputs]
                ↓
          [Integrations]
```

**Arrow style:**
- Gradient color matching source/destination
- Animated feel (use chevrons or dashed lines)
- Clear left-to-right flow

---

## Statistics to Include

Add a stats bar or callout boxes with these metrics:

| Stat | Value | Icon |
|------|-------|------|
| File Types | 7 | Document stack |
| Tools | 8 | Wrench |
| Output Formats | 4 | Export arrow |
| Max File Size | 50MB | File size |

---

## Callout Boxes

### Feature Highlight 1
**"AI Vision"**
- "Automatic image descriptions"
- "Chart data extraction"
- "Powered by Claude"

### Feature Highlight 2
**"Enterprise Ready"**
- "MCP Server integration"
- "REST API endpoints"
- "Python SDK"

### Feature Highlight 3
**"Structured Output"**
- "Preserves document hierarchy"
- "Extracts tables & metadata"
- "Multiple format options"

---

## Layout Recommendation

```
┌────────────────────────────────────────────────────────────────┐
│                    FILE PARSER AGENT                           │
│           Transform Documents into Structured Data             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   ┌─────────┐      ┌─────────────┐      ┌─────────┐           │
│   │  PDF    │      │             │      │  JSON   │           │
│   │  Word   │ ───► │   PARSER    │ ───► │  MD     │           │
│   │  Excel  │      │   ENGINE    │      │  CSV    │           │
│   │  PPTX   │      │             │      │  TXT    │           │
│   └─────────┘      └──────┬──────┘      └─────────┘           │
│                           │                                    │
│                    ┌──────▼──────┐                             │
│                    │  AI VISION  │                             │
│                    │   Claude    │                             │
│                    └─────────────┘                             │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│   🌐 Web UI    💻 CLI    🐍 Python API    🤖 MCP Server       │
└────────────────────────────────────────────────────────────────┘
```

---

## Style Guidelines

### Typography
- **Title:** Bold sans-serif, 48-72pt
- **Section Headers:** Semi-bold, 24-32pt
- **Body Text:** Regular, 14-18pt
- **Labels:** Medium, 12-14pt

### Icons
- Use consistent icon style (outlined or filled, not mixed)
- Recommended: Lucide, Heroicons, or Font Awesome
- Size: 24-48px for main icons, 16-20px for labels

### Spacing
- Generous whitespace between sections
- Consistent padding within cards (16-24px)
- Clear visual hierarchy

### Effects
- Subtle shadows on cards (2-4px blur)
- Rounded corners (8-12px radius)
- Optional: Subtle gradient backgrounds

---

## Do NOT Include

- Code snippets or technical implementation details
- File paths or system-specific information
- Version numbers or dates
- Developer-focused terminology
- Cluttered or overlapping elements

---

## Target Audience

This infographic is for:
- Business stakeholders evaluating the tool
- Technical managers understanding capabilities
- Potential users exploring integration options
- Documentation and marketing materials

---

## Deliverables

Generate:
1. **Primary infographic** - Full system architecture (landscape)
2. **Simplified version** - Key features only (square format for social)
3. **Icon set** - Individual icons for each component (optional)
