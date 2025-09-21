#!/usr/bin/env python3
"""
Main entry point for the pdf-lite-mcp server.
A simplified Python MCP server for reading PDF files, optimized for Amazon Q CLI.
"""

import asyncio
import sys
import json
import logging
import os
import time
from typing import Any, Dict, List

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ServerCapabilities,
        ToolsCapability,
    )
except ImportError:
    print("Error: mcp package is required. Install with: uv add mcp>=1.1.0", file=sys.stderr)
    sys.exit(1)

from pydantic import ValidationError

# Try relative imports first, fallback to absolute imports
try:
    from .models import ReadPdfRequest, ReadPdfResponse, McpResponse, PdfSourceResult, PdfResultData
    from .pdf_reader import PdfProcessor
    from .utils import format_error_for_amazon_q
except ImportError:
    # Fallback for when running as standalone script
    from models import ReadPdfRequest, ReadPdfResponse, McpResponse, PdfSourceResult, PdfResultData
    from pdf_reader import PdfProcessor
    from utils import format_error_for_amazon_q


# Configure logging
def setup_logging():
    """Setup logging configuration."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize the PDF processor
pdf_processor = PdfProcessor()

# Create the MCP server
server = Server("pdf-lite-mcp")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """
    List available tools.

    Returns:
        List of available tools
    """
    return [
        Tool(
            name="read_pdf",
            description=(
                "Read content from PDF files (local paths or URLs). "
                "Extract full text, specific pages, metadata, and page count. "
                "Optimized for Amazon Q CLI with clean, structured output."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sources": {
                        "type": "array",
                        "description": "PDF sources to process",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Relative path to local PDF file"
                                },
                                "url": {
                                    "type": "string",
                                    "description": "URL of PDF file"
                                },
                                "pages": {
                                    "type": "array",
                                    "description": "Specific pages to extract (1-based)",
                                    "items": {
                                        "type": "integer",
                                        "minimum": 1
                                    }
                                }
                            },
                            "oneOf": [
                                {"required": ["path"]},
                                {"required": ["url"]}
                            ]
                        },
                        "minItems": 1
                    },
                    "include_full_text": {
                        "type": "boolean",
                        "description": "Include full text if no specific pages requested",
                        "default": False
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include PDF metadata",
                        "default": True
                    },
                    "include_page_count": {
                        "type": "boolean",
                        "description": "Include total page count",
                        "default": True
                    }
                },
                "required": ["sources"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Handle tool calls.

    Args:
        name: Name of the tool to call
        arguments: Tool arguments

    Returns:
        Tool result
    """
    start_time = time.time()
    logger.info(f"Tool call received: {name}")

    if name != "read_pdf":
        logger.error(f"Unknown tool requested: {name}")
        raise ValueError(f"Unknown tool: {name}")

    try:
        # Validate and parse arguments
        request = ReadPdfRequest.parse_obj(arguments)
        logger.debug(f"Processing {len(request.sources)} PDF source(s)")

        # Process the request
        response = await pdf_processor.process_request(request)

        # Log results summary with performance metrics
        processing_time = time.time() - start_time
        successful = sum(1 for result in response.results if result.success)
        total = len(response.results)
        logger.info(f"PDF processing completed: {successful}/{total} successful in {processing_time:.2f}s")

        # Format response for Amazon Q CLI
        result_text = _format_response_for_amazon_q(response)

        return [TextContent(type="text", text=result_text)]

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        error_msg = _format_validation_error_for_amazon_q(e)
        return [TextContent(type="text", text=error_msg)]

    except Exception as e:
        logger.error(f"Unexpected error during PDF processing: {e}", exc_info=True)
        error_msg = format_error_for_amazon_q(e, "PDF processing")
        return [TextContent(type="text", text=f"❌ Error: {error_msg}")]


def _format_response_for_amazon_q(response: ReadPdfResponse) -> str:
    """
    Format response in a way that's optimized for Amazon Q CLI.

    Args:
        response: The PDF processing response

    Returns:
        Formatted response string
    """
    if not response.results:
        return "⚠️ No results to display"

    # For single source, provide clean output
    if len(response.results) == 1:
        result = response.results[0]
        return _format_single_result_for_amazon_q(result)

    # For multiple sources, provide structured output
    output_parts = [f"📄 Processed {len(response.results)} PDF sources:"]

    for i, result in enumerate(response.results, 1):
        output_parts.append(f"\n--- Source {i}: {result.source} ---")
        if result.success:
            output_parts.append("✅ Success")
            if result.data:
                output_parts.append(_format_result_data(result.data, compact=True))
        else:
            output_parts.append(f"❌ Failed: {result.error}")

    return "\n".join(output_parts)


def _format_single_result_for_amazon_q(result: PdfSourceResult) -> str:
    """
    Format a single result for Amazon Q CLI.

    Args:
        result: Single PDF processing result

    Returns:
        Formatted result string
    """
    if not result.success:
        return f"❌ Failed to process {result.source}: {result.error}"

    if not result.data:
        return f"⚠️ No data extracted from {result.source}"

    output_parts = [f"📄 {result.source}"]
    output_parts.append(_format_result_data(result.data, compact=False))

    return "\n".join(output_parts)


def _format_result_data(data: PdfResultData, compact: bool = False) -> str:
    """
    Format result data for display.

    Args:
        data: PDF result data
        compact: Whether to use compact formatting

    Returns:
        Formatted data string
    """
    parts = []

    # Page count
    if data.num_pages:
        parts.append(f"📊 Pages: {data.num_pages}")

    # Metadata
    if data.metadata and not compact:
        metadata_items = []
        for key, value in data.metadata.items():
            if value and key.lower() in ['title', 'author', 'subject', 'creator']:
                metadata_items.append(f"{key}: {value}")

        if metadata_items:
            parts.append("📝 " + " | ".join(metadata_items))

    # Warnings
    if data.warnings:
        for warning in data.warnings:
            parts.append(f"⚠️ {warning}")

    # Text content
    if data.full_text:
        if compact:
            preview = data.full_text[:100] + "..." if len(data.full_text) > 100 else data.full_text
            parts.append(f"📖 Text: {preview}")
        else:
            parts.append(f"📖 Full Text:\n{data.full_text}")

    elif data.page_texts:
        if compact:
            parts.append(f"📄 Extracted {len(data.page_texts)} pages")
        else:
            for page_text in data.page_texts:
                parts.append(f"📄 Page {page_text.page}:\n{page_text.text}")

    return "\n".join(parts) if parts else "No content extracted"


def _format_validation_error_for_amazon_q(error: ValidationError) -> str:
    """
    Format validation errors for Amazon Q CLI.

    Args:
        error: Pydantic validation error

    Returns:
        Formatted error message
    """
    error_parts = ["🔍 Invalid arguments:"]

    for err in error.errors():
        location = " → ".join(str(loc) for loc in err["loc"])
        message = err["msg"]
        error_parts.append(f"  • {location}: {message}")

    return "\n".join(error_parts)


async def main():
    """Main entry point for async execution."""
    print("Starting pdf-lite-mcp server...", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pdf-lite-mcp",
                server_version="1.0.1",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability()
                )
            )
        )


def main_cli():
    """CLI entry point for package scripts."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down pdf-lite-mcp server...", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main_cli()