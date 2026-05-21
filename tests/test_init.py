from fastmcp import FastMCP

from stirlingpdf_agent.mcp_server import get_mcp_instance


def test_mcp_instance_creation():
    """Test that the MCP instance can be created successfully."""
    mcp, args, middlewares, registered_tags = get_mcp_instance()
    assert isinstance(mcp, FastMCP)
    assert "stirling pdf" in mcp.name.lower()


def test_import_stirlingpdf_agent():
    """Test that the package can be imported."""
    import stirlingpdf_agent

    assert stirlingpdf_agent.__version__ is not None  # type: ignore[attr-defined]
