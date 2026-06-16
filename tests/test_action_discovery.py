"""Action-discovery behaviour for the pdf_action tool.

Verifies the shared agent-utilities action-dispatch helper is wired in:
``list_actions`` returns the available action names and an unknown action raises
a rich ValueError pointing at ``list_actions``.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from stirlingpdf_agent.mcp_server import get_mcp_instance


async def _get_pdf_action_tool():
    mcp, _, _, _ = get_mcp_instance()
    tools = await mcp.list_tools()
    tool = next((t for t in tools if t.name == "pdf_action"), None)
    assert tool is not None
    return tool


@pytest.mark.asyncio
async def test_list_actions_returns_action_names():
    tool = await _get_pdf_action_tool()

    client = MagicMock()
    client.add_watermark = MagicMock(return_value="ok")
    client.split_pdf = MagicMock(return_value="ok")
    ctx = MagicMock()
    ctx.info = AsyncMock()

    res = await tool.fn(
        action="list_actions", params_json="{}", client=client, ctx=ctx
    )

    assert isinstance(res, dict)
    assert res["service"] == "stirlingpdf-agent"
    assert "add_watermark" in res["actions"]
    assert "split_pdf" in res["actions"]


@pytest.mark.asyncio
async def test_unknown_action_raises_with_did_you_mean():
    tool = await _get_pdf_action_tool()

    client = MagicMock()
    client.add_watermark = MagicMock(return_value="ok")
    ctx = MagicMock()
    ctx.info = AsyncMock()

    with pytest.raises(ValueError) as excinfo:
        await tool.fn(
            action="add_watermarks_now", params_json="{}", client=client, ctx=ctx
        )

    assert "list_actions" in str(excinfo.value)
