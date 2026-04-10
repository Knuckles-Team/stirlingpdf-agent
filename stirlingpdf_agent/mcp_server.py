#!/usr/bin/python
import warnings

# Filter RequestsDependencyWarning early to prevent log spam
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from requests.exceptions import RequestsDependencyWarning
        warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
    except ImportError:
        pass

# General urllib3/chardet mismatch warnings
warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
warnings.filterwarnings("ignore", message=".*urllib3.*or charset_normalizer.*")

from dotenv import load_dotenv, find_dotenv
from agent_utilities.base_utilities import to_boolean
import os
import sys
import logging
from typing import Optional, Any

from pydantic import Field
from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger
from agent_utilities.mcp_utilities import (
    create_mcp_server,
)
from stirlingpdf_agent.auth import get_client

__version__ = "0.1.29"
print(f"Stirling PDF Agent MCP v{__version__}", file=sys.stderr)

logger = get_logger(name="TokenMiddleware")
logger.setLevel(logging.DEBUG)


def register_prompts(mcp: FastMCP):
    @mcp.prompt(
        name="example_prompt", description="Example prompt for Stirling PDF Agent."
    )
    def example_prompt(query: str) -> str:
        """Example prompt."""
        return f"Please help with '{query}' using Stirling PDF Agent"


def register_pdf_tools(mcp: FastMCP):
    @mcp.tool(
        name="add_watermark",
        description="Add a watermark to a PDF file.",
        tags={"PDF"},
    )
    def add_watermark_tool(
        filepath: str = Field(
            ..., description="Path to the input PDF file to watermark."
        ),
        watermarkText: str = Field(..., description="The text of the watermark."),
        watermarkType: str = Field(
            default="text", description="Type of watermark (e.g. 'text')."
        ),
        alphabet: Optional[str] = Field(default="roman", description="Alphabet type."),
        fontSize: Optional[str] = Field(default="30", description="Font size."),
        rotation: Optional[str] = Field(default="0", description="Rotation angle."),
        opacity: Optional[str] = Field(
            default="0.5", description="Opacity (0.0 to 1.0)."
        ),
        widthSpacer: Optional[str] = Field(default="50", description="Width spacing."),
        heightSpacer: Optional[str] = Field(
            default="50", description="Height spacing."
        ),
    ) -> Any:
        """Add a watermark to a PDF file."""
        import base64

        api = get_client()
        kwargs = {
            "filepath": filepath,
            "watermarkType": watermarkType,
            "watermarkText": watermarkText,
            "alphabet": alphabet,
            "fontSize": fontSize,
            "rotation": rotation,
            "opacity": opacity,
            "widthSpacer": widthSpacer,
            "heightSpacer": heightSpacer,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        response = api.add_watermark(**kwargs)

        return base64.b64encode(response.data).decode("utf-8")


def get_mcp_instance() -> tuple[Any, Any, Any, Any]:
    """Initialize and return the MCP instance, args, and middlewares."""
    load_dotenv(find_dotenv())
    args, mcp, middlewares = create_mcp_server(
        name="Stirling PDF Agent MCP",
        version=__version__,
        instructions="Stirling PDF Agent MCP Server",
    )

    if to_boolean(os.getenv("PDFTOOL", "True")):
        register_pdf_tools(mcp)

    register_prompts(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)
    registered_tags = []
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