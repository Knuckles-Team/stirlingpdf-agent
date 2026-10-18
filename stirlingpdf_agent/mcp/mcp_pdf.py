"""Canonical MCP tools for PDF operations."""


from agent_connector_sdk.mcp.concurrency import run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from stirlingpdf_agent.auth import get_client


def register_pdf_tools(mcp: FastMCP):
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
        from agent_connector_sdk.mcp.action_dispatch import public_actions

        from stirlingpdf_agent.kg_ingest import ingest_actions

        actions = await run_blocking(public_actions, client)
        result = await run_blocking(ingest_actions, list(actions))
        return {"listed": len(actions), "ingested": result}
