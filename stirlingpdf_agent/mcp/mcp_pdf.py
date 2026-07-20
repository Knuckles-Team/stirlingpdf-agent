"""Canonical MCP tools for PDF operations."""

from typing import Any

from agent_utilities.mcp.action_dispatch import dispatch_async, parse_json_object
from agent_utilities.mcp.concurrency import run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from stirlingpdf_agent.auth import get_client


def _coerce_pdf_result(res: Any) -> dict:
    """Normalize a Stirling PDF API result into a JSON-safe dict."""
    if hasattr(res, "model_dump") and callable(res.model_dump):
        res_dict = res.model_dump()
        if isinstance(res_dict, dict):
            if "data" in res_dict and isinstance(res_dict["data"], bytes):
                import base64

                res_dict["data"] = base64.b64encode(res_dict["data"]).decode("utf-8")
            if "response" in res_dict:
                res_dict.pop("response", None)
            return res_dict

    return {"status": "success", "result": str(res)}


def register_pdf_tools(mcp: FastMCP):
    @mcp.tool(tags={"PDF"}, name="pdf_action")
    async def pdf_action(
        action: str = Field(
            description="The action/method name to execute on Stirling PDF API (e.g. add_watermark). Use action='list_actions' to discover all available actions."
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
        try:
            kwargs = parse_json_object(params_json)
        except ValueError:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        return await dispatch_async(
            client,
            action,
            kwargs,
            service="stirlingpdf-agent",
            result_coercer=_coerce_pdf_result,
            ctx=ctx,
        )

    @mcp.tool(tags={"PDF", "kg"}, name="stirlingpdf_ingest_tools")
    async def stirlingpdf_ingest_tools(
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Ingest available actions as governed :PdfTool nodes.

        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        if ctx:
            await ctx.info("Discovering + ingesting Stirling PDF tools...")
        from agent_utilities.mcp.action_dispatch import public_actions

        from stirlingpdf_agent.kg_ingest import ingest_actions

        actions = await run_blocking(public_actions, client)
        result = await run_blocking(ingest_actions, list(actions))
        return {"listed": len(actions), "ingested": result}
