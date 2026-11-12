"""
Stirling PDF Agent MCP Server.

Provides tools to manipulate and edit PDF files (watermark, rotate, compress, split,
merge, password and sanitize operations).
"""

from stirlingpdf_agent.mcp import register_pdf_tools

# SDK discovery registers the register_<tag>_tools functions bound in this module.
__all__ = ["register_pdf_tools"]
