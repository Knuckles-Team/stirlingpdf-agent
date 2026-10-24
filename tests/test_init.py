from fastmcp import FastMCP

from agent_connector_sdk.connector import build_server


def test_mcp_instance_creation():
    """Test that the MCP instance can be created successfully."""
    _, mcp = build_server("stirlingpdf_agent", command_args=[])
    assert isinstance(mcp, FastMCP)
    assert "stirling pdf" in mcp.name.lower()
