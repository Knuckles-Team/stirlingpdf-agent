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
"""
Stirling PDF Agent MCP Server.

Provides tools to manipulate and edit PDF files (e.g. adding watermarks).
"""

import logging
import os
import sys
from typing import Any

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import (
    create_mcp_server,
)
from dotenv import find_dotenv, load_dotenv
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from fastmcp.utilities.logging import get_logger
from pydantic import Field

from stirlingpdf_agent.auth import get_client

__version__ = "0.18.0"

logger = get_logger(name="StirlingPdfMCP")
logger.setLevel(logging.INFO)


def register_prompts(mcp: FastMCP):
    @mcp.prompt(
        name="example_prompt", description="Example prompt for Stirling PDF Agent."
    )
    def example_prompt(query: str) -> str:
        """Example prompt."""
        return f"Please help with '{query}' using Stirling PDF Agent"


def register_pdf_tools(mcp: FastMCP):
    @mcp.tool(tags={"PDF"}, name="pdf_action")
    async def pdf_action(
        action: str = Field(
            description="The action/method name to execute on Stirling PDF API (e.g. add_watermark)"
        ),
        params_json: str = Field(
            default="{}",
            description="JSON string of parameters to pass to the action (e.g. {'filepath': 'input.pdf', 'watermarkText': 'DRAFT'}).",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Execute any Stirling PDF API action dynamically."""
        if ctx:
            await ctx.info(f"Executing Stirling PDF action: {action}...")
        import json

        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Dynamic method lookup
        method = getattr(client, action, None)
        if method is None:
            raise ValueError(f"Unknown action '{action}' on StirlingPdfApi")

        res = method(**kwargs)

        if hasattr(res, "dict") and callable(res.dict):
            res_dict = res.dict()
            if isinstance(res_dict, dict):
                # If Response wraps binary data, encode it as base64 and remove requests.Response
                if "data" in res_dict and isinstance(res_dict["data"], bytes):
                    import base64

                    res_dict["data"] = base64.b64encode(res_dict["data"]).decode(
                        "utf-8"
                    )
                if "response" in res_dict:
                    res_dict.pop("response", None)
                return res_dict
        elif hasattr(res, "model_dump") and callable(res.model_dump):
            res_dict = res.model_dump()
            if isinstance(res_dict, dict):
                if "data" in res_dict and isinstance(res_dict["data"], bytes):
                    import base64

                    res_dict["data"] = base64.b64encode(res_dict["data"]).decode(
                        "utf-8"
                    )
                if "response" in res_dict:
                    res_dict.pop("response", None)
                return res_dict

        return {"status": "success", "result": str(res)}


def get_mcp_instance() -> tuple[Any, Any, Any, list[str]]:
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
    registered_tags: list[str] = []
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
