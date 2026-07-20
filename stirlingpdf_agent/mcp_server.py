"""
Stirling PDF Agent MCP Server.

Provides tools to manipulate and edit PDF files (e.g. adding watermarks).
"""

import logging
import sys
from typing import Any

from agent_utilities.core.config import load_config
from agent_utilities.mcp.server_factory import create_mcp_server
from agent_utilities.mcp.verbose_tools import register_tool_surface
from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger

from stirlingpdf_agent.api_client import StirlingPdfApi
from stirlingpdf_agent.auth import get_client
from stirlingpdf_agent.mcp import register_pdf_tools

__version__ = "1.0.1"

logger = get_logger(name="StirlingPdfMCP")
logger.setLevel(logging.INFO)


def register_prompts(mcp: FastMCP):
    @mcp.prompt(
        name="example_prompt", description="Example prompt for Stirling PDF Agent."
    )
    def example_prompt(query: str) -> str:
        """Example prompt."""
        return f"Please help with '{query}' using Stirling PDF Agent"


def get_mcp_instance() -> tuple[Any, Any, Any, list[str]]:
    """Initialize and return the MCP instance, args, and middlewares."""
    load_config()
    args, mcp, middlewares = create_mcp_server(
        name="Stirling PDF Agent MCP",
        version=__version__,
        instructions="Stirling PDF Agent MCP Server",
    )

    registered_tags = register_tool_surface(
        mcp,
        client_cls=StirlingPdfApi,
        get_client=get_client,
        service="stirlingpdf-agent",
        registrars=[register_pdf_tools],
    )

    register_prompts(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)
    return mcp, args, middlewares, registered_tags


def mcp_server() -> None:
    mcp, args, middlewares, registered_tags = get_mcp_instance()
    print(f"{'stirlingpdf-agent'} MCP v{__version__}", file=sys.stderr)
    print("\nStarting MCP Server", file=sys.stderr)
    print(f"  Transport: {args.transport.upper()}", file=sys.stderr)
    print(f"  Auth: {args.auth_type}", file=sys.stderr)
    print(f"  Dynamic Tags Loaded: {len(set(registered_tags))}", file=sys.stderr)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error("Invalid transport", extra={"transport": args.transport})
        sys.exit(1)


if __name__ == "__main__":
    mcp_server()
