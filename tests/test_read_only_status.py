"""The read-only status operation (CONN-STIRLINGPDF-AGENT-R001)."""

import asyncio
from unittest.mock import MagicMock

import pytest
import requests
from agent_connector_sdk.exceptions import AuthError

from stirlingpdf_agent.api_client import StirlingPdfApi

pytestmark = pytest.mark.spec("CONN-STIRLINGPDF-AGENT-R001")


def _response(status: int, body: dict) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status
    response.json.return_value = body
    if status >= 400:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=response
        )
    return response


@pytest.mark.usefixtures("mock_env")
def test_status_tool_is_listed_read_only(monkeypatch):
    monkeypatch.setattr("sys.argv", ["stirlingpdf-mcp"])
    from stirlingpdf_agent.mcp_server import get_mcp_instance

    mcp, *_ = get_mcp_instance()
    tools = {tool.name: tool for tool in asyncio.run(mcp.list_tools())}
    annotations = tools["stirlingpdf_get_status"].annotations
    assert annotations.read_only_hint is True
    assert annotations.destructive_hint is False


def test_status_calls_the_status_route_with_the_api_key():
    client = StirlingPdfApi(base_url="http://pdf.test", token="key")
    client._session.get = MagicMock(
        return_value=_response(200, {"status": "UP", "version": "3.1.0"})
    )
    result = client.get_status()
    assert result.data == {"status": "UP", "version": "3.1.0"}
    call = client._session.get.call_args
    assert call.kwargs["url"] == "http://pdf.test/api/v1/info/status"
    assert call.kwargs["headers"]["X-API-KEY"] == "key"


def test_status_maps_401_to_an_authentication_error():
    client = StirlingPdfApi(base_url="http://pdf.test", token="key")
    client._session.get = MagicMock(return_value=_response(401, {}))
    with pytest.raises(AuthError):
        client.get_status()
