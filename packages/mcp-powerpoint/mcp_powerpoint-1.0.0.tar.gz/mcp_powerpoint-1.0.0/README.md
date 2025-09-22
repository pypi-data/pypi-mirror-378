# PowerPoint MCP Tools

This project provides MCP (Model Context Protocol) tools for converting PowerPoint presentations to/from structured JSON format using Pydantic models.

## MCP Server Configuration

To use this project as an MCP server in external applications, add the following configuration to your `mcpServers` configuration:

### Method 1: From GitHub Repository (Recommended)

Install directly from GitHub - no local setup required:

```json
{
  "mcpServers": {
    "mcp-powerpoint": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/CannonJunior/mcp-powerpoint.git", "mcp-powerpoint", "--server", "powerpoint"],
      "env": {}
    },
    "mcp-shape-naming": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/CannonJunior/mcp-powerpoint.git", "mcp-powerpoint", "--server", "shape-naming"],
      "env": {}
    }
  }
}
```

### Method 2: From PyPI (When Published)

Once published to PyPI, you can use the simple form:

```json
{
  "mcpServers": {
    "mcp-powerpoint": {
      "command": "uvx",
      "args": ["mcp-powerpoint", "--server", "powerpoint"],
      "env": {}
    },
    "mcp-shape-naming": {
      "command": "uvx",
      "args": ["mcp-powerpoint", "--server", "shape-naming"],
      "env": {}
    }
  }
}
```

### Method 3: Local Development

For local development, you can use uv directly:

```json
{
  "mcpServers": {
    "mcp-powerpoint": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-powerpoint",
        "run",
        "-m",
        "mcp_powerpoint",
        "--server",
        "powerpoint"
      ],
      "env": {}
    },
    "mcp-shape-naming": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-powerpoint",
        "run",
        "-m",
        "mcp_powerpoint",
        "--server",
        "shape-naming"
      ],
      "env": {}
    }
  }
}
```

### Quick Start

1. **Install uvx**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Copy the configuration** from `mcp-config.json` to your MCP client settings
3. **For shape naming**: Install Ollama and pull a model: `ollama pull llama3.2`
4. **That's it!** - uvx installs from GitHub automatically

**Test the installation**:
```bash
uvx --from git+https://github.com/CannonJunior/mcp-powerpoint.git mcp-powerpoint --help
```

### Prerequisites

- **UV/UVX**: Required for running the servers (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Ollama** (shape naming only): Install from https://ollama.ai and run `ollama pull llama3.2`
- **No Python setup required** - uvx manages everything in isolated environments!

### Testing the Configuration

To verify the MCP servers are working correctly:

1. Test from GitHub:
   ```bash
   # Test PowerPoint server
   uvx --from git+https://github.com/CannonJunior/mcp-powerpoint.git mcp-powerpoint --server powerpoint

   # Test shape naming server
   uvx --from git+https://github.com/CannonJunior/mcp-powerpoint.git mcp-powerpoint --server shape-naming
   ```

2. For local development:
   ```bash
   cd /path/to/mcp-powerpoint
   uv run -m mcp_powerpoint --server powerpoint
   # In another terminal:
   uv run -m mcp_powerpoint --server shape-naming
   ```

2. Check that they respond to MCP protocol messages and expose the expected tools:
   - PowerPoint server: `pptx_to_json`, `json_to_pptx`
   - Shape naming server: `analyze_shape_content`, `generate_descriptive_names_for_presentation`

## Features

- **Complete PowerPoint Analysis**: Extracts all text, shapes, images, tables, positioning, and formatting
- **Intelligent Shape Naming**: Uses Ollama LLM to generate descriptive names based on content
- **Pydantic Models**: Type-safe data structures for PowerPoint objects
- **Roundtrip Conversion**: Original PPTX → JSON → New PPTX with high fidelity
- **Multiple Client Modes**: Basic demo, extract, refine, rename, and populate workflows
- **MCP Integration**: Works with any MCP-compatible client

## Files

### Core Components
- `powerpoint_models.py` - Comprehensive Pydantic models for PowerPoint structure
- `powerpoint_server.py` - MCP server providing PowerPoint conversion tools
- `shape_naming_server.py` - MCP server for generating descriptive shape names using Ollama
- `client.py` - Basic demo client showing PowerPoint and Shape Naming integration
- `client_modes.py` - Advanced multi-mode client for specialized workflows

### PowerPoint Conversion Tools

#### `pptx_to_json(file_path: str) -> str`
Converts a PowerPoint file to structured JSON format.
- Extracts all slides, shapes, text content, formatting, images, and tables
- Preserves positioning, sizing, fonts, colors, and other properties
- Returns comprehensive JSON representation

#### `json_to_pptx(json_data: str, output_path: str) -> str`
Creates a PowerPoint file from JSON data.
- Reconstructs slides, shapes, text, images, and tables
- Applies formatting, positioning, and styling
- Generates a new .pptx file

### Shape Naming Tools (via Ollama)

#### `analyze_shape_content(shape_name: str, shape_text: str, shape_type: str) -> str`
Analyzes individual shape content and generates descriptive names.
- Uses Ollama LLM to analyze text content
- Generates programmatic names (lowercase with underscores)
- Examples: "Rectangle 5" → "company_header", "TextBox 42" → "project_title"

#### `generate_descriptive_names_for_presentation(json_data: str) -> str`
Processes entire presentations to rename all shapes.
- Batch processes all shapes in a presentation
- Handles duplicate names with numbering
- Returns updated JSON with `descriptive_name` and `original_name` fields

#### `get_shape_suggestions(shape_text: str, context: str = "") -> str`
Provides multiple naming suggestions with rationales.
- Returns 3 different naming options
- Includes rationale for each suggestion
- Useful for manual shape naming decisions

#### `batch_rename_shapes(json_data: str, naming_rules: str = "") -> str`
Advanced batch renaming with custom rules.
- Supports rule-based renaming patterns
- Falls back to automatic naming for unmatched shapes
- Returns detailed rename operation results

## Usage

### 1. Python Client Options

#### Basic Demo Client
Run the basic client for a comprehensive demo of both PowerPoint and Shape Naming tools:
```bash
uv run client.py
```

This client will:
- Convert a PowerPoint to JSON
- Generate descriptive names for all shapes using Ollama
- Recreate the PowerPoint from JSON
- Save results to `presentation_with_descriptive_names.json`

#### Advanced Multi-Mode Client
The `client_modes.py` provides specialized modes for different workflows:

**Extract Mode** - Convert PowerPoint to JSON and recreate:
```bash
python client_modes.py extract -i input.pptx
python client_modes.py extract -i input.pptx --json output.json --pptx recreated.pptx
```

**Refine Mode** - Improve recreated PowerPoint presentations:
```bash
python client_modes.py refine -i recreated.pptx
```

**Rename Mode** - Generate descriptive shape names with document analysis:
```bash
python client_modes.py rename -i presentation.json --content-dir ./docs
```

**Populate Mode** - Create presentations from templates using document content:
```bash
python client_modes.py populate -i template.pptx --naming-json names.json --content-dir ./content
```

### 2. Direct MCP Server Usage

#### Start the PowerPoint MCP Server
```python
python powerpoint_server.py
```

#### Start the Shape Naming MCP Server  
```python
python shape_naming_server.py
```

### 3. MCP Tool Integration
```python
# Convert PowerPoint to JSON
json_result = await client.call_tool("powerpoint_pptx_to_json", {
    "file_path": "presentation.pptx"
})

# Convert JSON back to PowerPoint
pptx_result = await client.call_tool("powerpoint_json_to_pptx", {
    "json_data": json_string,
    "output_path": "output.pptx"
})

# Generate descriptive names for all shapes
naming_result = await client.call_tool("shape_naming_generate_descriptive_names_for_presentation", {
    "json_data": json_string
})

# Analyze individual shape content
shape_name = await client.call_tool("shape_naming_analyze_shape_content", {
    "shape_name": "Rectangle 5",
    "shape_text": "General Atomics – Integrated Intelligence, Inc.",
    "shape_type": "AUTO_SHAPE"
})
```

## Data Structure

The JSON structure captures:
- **Presentation**: Dimensions, properties, metadata
- **Slides**: Individual slide content and properties
- **Shapes**: All shape types (text boxes, auto shapes, images, tables)
- **Text**: Formatted text with fonts, colors, styling
- **Images**: Base64-encoded image data with cropping info
- **Tables**: Complete table structure with cell content
- **Positioning**: Exact coordinates and dimensions
- **Formatting**: Colors, fonts, line styles, fills

## Test Results

Successfully tested with `MDA-250083-BNB-20250904.v1.RFI.pptx`:
- Original file: 132,823 bytes
- JSON representation: 158,917 bytes
- Recreated file: 61,334 bytes
- ✅ Roundtrip conversion successful
- ✅ All text content preserved
- ✅ Font sizes correctly extracted (12pt, 14pt) and applied
- ✅ Font colors extracted (`#000000`, `#FFFFFF`) and applied  
- ✅ Shape fill colors extracted (`#D6D6D6`, `#000000`) and applied
- ✅ Shape border colors extracted (`#000000`) and applied
- ✅ Shape positioning maintained
- ✅ Image data captured and restored

### Fixed Issues
- **Font Size Accuracy**: Fixed EMU to points conversion (was showing 177800, now correctly shows 12pt)
- **Font Color Extraction**: Properly handles RGBColor objects with hex output
- **Shape Fill Colors**: Extracts solid, gradient, and patterned fill colors correctly
- **Shape Border Colors**: Extracts line colors, widths, and dash styles with proper RGBColor handling
- **Color Application**: Applies fill and border colors during PowerPoint reconstruction

## Dependencies

- `python-pptx` - PowerPoint file manipulation
- `pydantic` - Data models and JSON serialization
- `fastmcp` - MCP server framework
- `pillow` - Image processing
- `base64` - Image encoding/decoding
- `ollama` - Local LLM integration for shape naming
- `uv` - Fast Python package manager (recommended)

## Architecture

The system uses a three-layer architecture:
1. **Pydantic Models** - Type-safe data structures
2. **Extraction Layer** - Converts PowerPoint objects to models
3. **Reconstruction Layer** - Rebuilds PowerPoint from models
4. **MCP Interface** - Exposes functionality as tools

This enables reliable, type-safe conversion between PowerPoint files and structured JSON data suitable for analysis, modification, or storage.