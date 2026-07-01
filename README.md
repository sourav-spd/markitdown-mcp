# MarkItDown MCP Server

A production-ready [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for converting documents and files to Markdown using [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

Provides **3 tools** for converting documents from URIs, local file paths, or raw string content — supporting a wide range of file formats.

Supports three transport modes: **stdio**, **SSE**, and **Streamable HTTP**.

---

## Folder Structure

```text
markitdown-tool/
|-- markitdown_server.py       # Main server entry point
|-- Dockerfile
|-- LICENSE
|-- mcp.example.json
|-- pyproject.toml
|-- README.md
`-- tools/
    |-- __init__.py
    |-- markitdown_tools.py
    `-- toolhandler.py
```

---

## Available Tools (3)

| Tool | Description |
|------|-------------|
| `convert_to_markdown` | Convert a resource from an http:, https:, file:, or data: URI to Markdown |
| `convert_local_file` | Convert a local file by absolute or relative path to Markdown |
| `convert_stream` | Convert raw string content to Markdown with optional file extension hint |

---

## Supported File Formats

| Format | Extensions |
|--------|-----------|
| PDF | `.pdf` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx`, `.xls` |
| Images (OCR) | `.png`, `.jpg`, `.gif` |
| Audio (transcription) | `.mp3`, `.wav`, `.m4a` |
| HTML | `.html` |
| CSV / JSON / XML | `.csv`, `.json`, `.xml` |
| ZIP | `.zip` |
| EPub | `.epub` |
| YouTube URLs | `https://youtube.com/...` |

---

## Tools Reference

### 1. convert_to_markdown

Convert a remote or local resource via URI.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `uri` | Yes | URI to convert. Schemes: `http:`, `https:`, `file:`, `data:` |

**Example:**
```json
{
  "uri": "https://example.com/report.pdf"
}
```

**Returns:**
```json
{
  "success": true,
  "uri": "https://example.com/report.pdf",
  "title": "Annual Report 2025",
  "markdown": "# Annual Report 2025\n\n..."
}
```

---

### 2. convert_local_file

Convert a file on the local filesystem.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `file_path` | Yes | Absolute or relative path to the file |

**Example:**
```json
{
  "file_path": "C:/Users/me/Documents/report.docx"
}
```

**Returns:**
```json
{
  "success": true,
  "file_path": "C:/Users/me/Documents/report.docx",
  "title": "Q4 Report",
  "markdown": "# Q4 Report\n\n..."
}
```

---

### 3. convert_stream

Convert raw string content to Markdown. Useful for in-memory or clipboard data.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | String content to convert |
| `file_extension` | No | Extension hint for format detection (e.g. `.html`, `.json`) |

**Example:**
```json
{
  "content": "<html><body><h1>Hello</h1><p>World</p></body></html>",
  "file_extension": ".html"
}
```

**Returns:**
```json
{
  "success": true,
  "file_extension": ".html",
  "title": null,
  "markdown": "# Hello\n\nWorld\n"
}
```

---

## Prerequisites

- Python 3.10+
- `ffmpeg` and `libmagic` (for audio/image support — installed automatically in Docker)

---

## Installation

```bash
# From the workspace root (where .venv lives)
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

cd markitdown-tool

# Core install
pip install -e .

# With all optional format support (recommended)
pip install -e ".[all]"
```

---

## Run

### stdio (default — for MCP desktop clients like Claude Desktop)

```bash
markitdown-mcp --mode stdio
```

### SSE

```bash
markitdown-mcp --mode sse --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET  /sse`
- `POST /messages/`
- `GET  /health`

### Streamable HTTP

```bash
markitdown-mcp --mode streamable-http --host 0.0.0.0 --port 8000
```

Endpoints:
- `POST /mcp`
- `GET  /health`
- `GET  /`

### Environment variables (alternative to CLI flags)

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT_TYPE` | `stdio` | `stdio` / `sse` / `streamable-http` |
| `APP_HOST` | `0.0.0.0` | Bind host |
| `APP_PORT` | `8000` | Bind port |
| `MARKITDOWN_ENABLE_PLUGINS` | `false` | Enable MarkItDown plugins (`true` / `false`) |

---

## Docker

```bash
# Build
docker build -t markitdown-mcp .

# Run (streamable-http, port 8000)
docker run -p 8000:8000 markitdown-mcp

# With local file access
docker run -v /path/to/docs:/workdir -p 8000:8000 markitdown-mcp

# With plugins enabled
docker run -e MARKITDOWN_ENABLE_PLUGINS=true -p 8000:8000 markitdown-mcp
```

---

## MCP Client Configuration

See `mcp.example.json` for a ready-to-use client config snippet.

**stdio (Claude Desktop / Cursor):**
```json
{
  "mcpServers": {
    "markitdown": {
      "command": "markitdown-mcp",
      "args": ["--mode", "stdio"],
      "env": {
        "MARKITDOWN_ENABLE_PLUGINS": "false"
      }
    }
  }
}
```

**Streamable HTTP (MCP Inspector / MCPmon):**
```
http://localhost:8000/mcp
```

**SSE:**
```
http://localhost:8000/sse
```

---

## Architecture

```text
MCP Client (Claude / Cursor / MCP Inspector)
    |
    | JSON-RPC 2.0
    v
Transport Layer (stdio | SSE | Streamable HTTP)   ← markitdown_server.py
    |
    v
ToolHandler Registry (3 tools)
    |
    v
MarkItDown Tool Handlers                          ← tools/markitdown_tools.py
    |
    v
MarkItDown Library (Microsoft)
    |
    v
File / URL / Stream
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'markitdown'`** — Run `pip install -e ".[all]"`.

**`ffmpeg not found`** — Install ffmpeg: `choco install ffmpeg` (Windows) or `apt-get install ffmpeg` (Linux).

**Port already in use** — Change `APP_PORT` env var or use `--port` flag.

**`convert_local_file` returns "File not found"** — Use an absolute path. In Docker, mount the directory with `-v`.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
