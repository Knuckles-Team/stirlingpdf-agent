"""
Stirling PDF Agent MCP Server.

Provides tools to manipulate and edit PDF files (e.g. adding watermarks).
"""

from scion_sdk.connector_hooks import RegistrationContext

from stirlingpdf_agent.mcp import register_pdf_tools

# SDK discovery registers the register_<tag>_tools functions bound in this module.
__all__ = ["register_pdf_tools"]


def register_prompts(context: RegistrationContext):
    mcp = context.server

    @mcp.prompt(
        name="example_prompt", description="Example prompt for Stirling PDF Agent."
    )
    def example_prompt(query: str) -> str:
        """Example prompt."""
        return f"Please help with '{query}' using Stirling PDF Agent"
