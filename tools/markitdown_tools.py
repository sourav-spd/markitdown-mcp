"""markitdown_tools.py - MarkItDown MCP tool handlers (3 tools)."""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Sequence
from io import BytesIO

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from tools.toolhandler import ToolHandler

logger = logging.getLogger("markitdown-mcp")


def _get_markitdown():
    from markitdown import MarkItDown
    enable_plugins = os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").strip().lower() in ("true", "1", "yes")
    return MarkItDown(enable_plugins=enable_plugins)


class ConvertToMarkdownToolHandler(ToolHandler):
    def __init__(self) -> None:
        super().__init__("convert_to_markdown")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=(
                "Convert a resource described by an http:, https:, file: or data: URI to Markdown. "
                "Supports PDF, PowerPoint, Word, Excel, images (with OCR), audio (with transcription), "
                "HTML, CSV, JSON, XML, ZIP files, YouTube URLs, EPubs, and more."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "uri": {
                        "type": "string",
                        "description": "URI of the resource to convert. Supported schemes: http:, https:, file:, data:.",
                    }
                },
                "required": ["uri"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        self.validate_required_args(args, ["uri"])
        uri = args["uri"].strip()
        try:
            result = _get_markitdown().convert_uri(uri)
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "uri": uri,
                "title": getattr(result, "title", None),
                "markdown": result.markdown,
            }, indent=2))]
        except Exception as exc:
            logger.exception("convert_to_markdown failed: %s", exc)
            return [TextContent(type="text", text=json.dumps({
                "success": False, "uri": uri, "error": str(exc)
            }, indent=2))]


class ConvertLocalFileToolHandler(ToolHandler):
    def __init__(self) -> None:
        super().__init__("convert_local_file")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=(
                "Convert a local file to Markdown. Supports PDF, PowerPoint, Word, Excel, images, "
                "audio files, HTML, CSV, JSON, XML, ZIP files, EPubs, and more."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the local file to convert. Example: 'C:/Users/me/report.pdf'",
                    }
                },
                "required": ["file_path"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        self.validate_required_args(args, ["file_path"])
        file_path = args["file_path"].strip()
        if not os.path.exists(file_path):
            return [TextContent(type="text", text=json.dumps({
                "success": False, "file_path": file_path, "error": f"File not found: {file_path}"
            }, indent=2))]
        try:
            result = _get_markitdown().convert_local(file_path)
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "file_path": file_path,
                "title": getattr(result, "title", None),
                "markdown": result.markdown,
            }, indent=2))]
        except Exception as exc:
            logger.exception("convert_local_file failed: %s", exc)
            return [TextContent(type="text", text=json.dumps({
                "success": False, "file_path": file_path, "error": str(exc)
            }, indent=2))]


class ConvertStreamToolHandler(ToolHandler):
    def __init__(self) -> None:
        super().__init__("convert_stream")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=(
                "Convert content from a string to Markdown. "
                "Useful for converting in-memory data or clipboard content."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The string content to convert to Markdown.",
                    },
                    "file_extension": {
                        "type": "string",
                        "description": "Optional file extension hint (e.g. '.html', '.json'). Auto-detected if omitted.",
                    },
                },
                "required": ["content"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        self.validate_required_args(args, ["content"])
        content = args["content"]
        file_extension = args.get("file_extension")
        try:
            stream = BytesIO(content.encode("utf-8") if isinstance(content, str) else content)
            result = _get_markitdown().convert_stream(stream, file_extension=file_extension)
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "file_extension": file_extension,
                "title": getattr(result, "title", None),
                "markdown": result.markdown,
            }, indent=2))]
        except Exception as exc:
            logger.exception("convert_stream failed: %s", exc)
            return [TextContent(type="text", text=json.dumps({
                "success": False, "file_extension": file_extension, "error": str(exc)
            }, indent=2))]
