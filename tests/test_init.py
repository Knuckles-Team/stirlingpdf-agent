from fastmcp import FastMCP

from scion_sdk.connector import build_server
from scion_sdk.connector_identity import connector_name


def test_mcp_instance_creation():
    """Test that the MCP instance can be created successfully."""
    _, mcp = build_server("stirlingpdf_agent", command_args=[])
    assert isinstance(mcp, FastMCP)
    assert mcp.name == connector_name("stirlingpdf_agent")
