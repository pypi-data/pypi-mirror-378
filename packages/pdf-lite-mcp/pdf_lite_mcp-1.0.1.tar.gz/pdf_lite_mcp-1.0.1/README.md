# pdf-lite-mcp

<!-- Badges -->
<p align="center">
  <a href="https://github.com/tsaol/pdf-lite-mcp/actions/workflows/ci.yml">
    <img src="https://github.com/tsaol/pdf-lite-mcp/actions/workflows/ci.yml/badge.svg" alt="CI/CD Pipeline">
  </a>
  <a href="https://github.com/tsaol/pdf-lite-mcp/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://github.com/tsaol/pdf-lite-mcp/releases">
    <img src="https://img.shields.io/github/v/release/tsaol/pdf-lite-mcp" alt="Latest Release">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  </a>
  <a href="https://github.com/tsaol/pdf-lite-mcp/issues">
    <img src="https://img.shields.io/github/issues/tsaol/pdf-lite-mcp" alt="GitHub Issues">
  </a>
  <a href="https://github.com/tsaol/pdf-lite-mcp/stargazers">
    <img src="https://img.shields.io/github/stars/tsaol/pdf-lite-mcp" alt="GitHub Stars">
  </a>
</p>

<!-- Project Description -->
<p align="center">
  A <strong>simplified Python MCP server</strong> for reading PDF files, specifically optimized for <strong>Amazon Q CLI</strong> usage.
</p>

<p align="center">
  Built as a streamlined alternative to complex PDF processing tools, focusing on clean output and reliable performance.
</p>

## Features

- Read PDFs from local files or URLs
- Extract specific pages or full content
- Metadata extraction (title, author, page count)
- Batch processing support
- Security-focused with path validation

## Installation

### From PyPI (recommended)
```bash
# Install using uvx (no need to clone repository)
uvx pdf-lite-mcp

# Or install globally
pip install pdf-lite-mcp
```

### From source
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/tsaol/pdf-lite-mcp.git
cd pdf-lite-mcp
uv sync
```

## Amazon Q CLI Configuration

### Using PyPI package (recommended)
```json
{
  "mcpServers": {
    "pdf-lite": {
      "command": "uvx",
      "args": ["pdf-lite-mcp"],
      "disabled": false,
      "autoApprove": ["read_pdf"]
    }
  }
}
```

### Using local development version
```json
{
  "mcpServers": {
    "pdf-lite": {
      "command": "uv",
      "args": ["run", "python", "src/main.py"],
      "cwd": "/path/to/pdf-lite-mcp",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

### Using Git URL
```json
{
  "mcpServers": {
    "pdf-lite": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/tsaol/pdf-lite-mcp.git", "pdf-lite-mcp"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Usage

### Basic PDF Reading
```json
{
  "tool_name": "read_pdf",
  "arguments": {
    "sources": [{"path": "./document.pdf"}],
    "include_full_text": true
  }
}
```

### Specific Pages
```json
{
  "tool_name": "read_pdf",
  "arguments": {
    "sources": [{"path": "./report.pdf", "pages": [1, 3, 5]}]
  }
}
```

### Multiple PDFs
```json
{
  "tool_name": "read_pdf",
  "arguments": {
    "sources": [
      {"path": "./doc1.pdf"},
      {"url": "https://example.com/doc2.pdf"}
    ]
  }
}
```

## Testing

```bash
# Basic tests
uv run python tests/simple_test.py

# Server tests
uv run python tests/test_server.py

# PDF processing tests (requires network)
uv run python tests/test_with_pdf.py
```

## License

MIT License - see [LICENSE](LICENSE) file for details.