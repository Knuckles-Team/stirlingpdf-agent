import os
from unittest.mock import MagicMock, patch

import pytest
import requests
from scion_sdk.exceptions import (
    AuthError,
    LoginRequiredError,
    MissingParameterError,
    ParameterError,
    UnauthorizedError,
)

import stirlingpdf_agent
from stirlingpdf_agent.api_client import StirlingPdfApi
from stirlingpdf_agent.auth import get_client
from stirlingpdf_agent.stirlingpdf_agent_models import AddWatermarkModel

# ==========================================
# 1. Package __init__.py Tests
# ==========================================


def test_getattr_attribute_error():
    with pytest.raises(
        AttributeError, match="has no attribute 'nonexistent_attribute_abc'"
    ):
        _ = stirlingpdf_agent.nonexistent_attribute_abc


# ==========================================
# 2. Main __main__.py Tests
# ==========================================




# ==========================================
# 3. Model stirlingpdf_agent_models.py Tests
# ==========================================


def test_models_properties():
    model = AddWatermarkModel(watermarkType="text", watermarkText="DRAFT")
    params = model.api_parameters
    assert params["watermarkType"] == "text"
    assert params["watermarkText"] == "DRAFT"

    # Test BaseModelWrapper properties
    from stirlingpdf_agent.stirlingpdf_agent_models import BaseModelWrapper

    wrapper = BaseModelWrapper()
    assert wrapper.api_parameters == {}


# ==========================================
# 4. API Client Base tests (api_client_base.py)
# ==========================================


def test_api_client_base_missing_url():
    with pytest.raises(MissingParameterError, match="base_url is required"):
        StirlingPdfApi(base_url=None)


def test_api_client_base_applies_tls_profile():
    profile = MagicMock()
    profile.configure_requests_session.side_effect = lambda session: session
    client = StirlingPdfApi(
        base_url="https://service.invalid",
        tls_profile=profile,
    )
    assert client.tls_profile is profile
    profile.configure_requests_session.assert_called_once()


def test_api_client_base_with_token():
    client = StirlingPdfApi(base_url="http://example.com", token="my-token")
    assert client.headers["X-API-KEY"] == "my-token"


# ==========================================
# 5. Watermark Client tests (api_client_watermark.py)
# ==========================================


def test_add_watermark_login_required():
    client = StirlingPdfApi(base_url="http://example.com", token=None)
    client.headers = {}
    with pytest.raises(LoginRequiredError):
        client.add_watermark(
            "dummy.pdf", watermarkType="text", watermarkText="CONFIDENTIAL"
        )


def test_add_watermark_success(tmp_path):
    """
    Test add watermark REST API client call.

    CONCEPT:SP-OS.scaling.stirlingpdf
    """
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy pdf content")

    client = StirlingPdfApi(base_url="http://example.com", token="my-token")

    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp._content = b"watermarked pdf bytes"

    with patch.object(client._session, "post", return_value=mock_resp) as mock_post:
        res = client.add_watermark(
            str(pdf_file),
            watermarkType="text",
            watermarkText="CONFIDENTIAL",
        )
        assert res.data == b"watermarked pdf bytes"
        mock_post.assert_called_once()


def test_add_watermark_validation_error():
    client = StirlingPdfApi(base_url="http://example.com", token="my-token")
    with pytest.raises(ParameterError):
        client.add_watermark("dummy.pdf", watermarkText="CONFIDENTIAL")


def test_add_watermark_http_error(tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy pdf content")

    client = StirlingPdfApi(base_url="http://example.com", token="my-token")

    # 401 Unauthorized -> AuthError
    mock_resp_401 = requests.Response()
    mock_resp_401.status_code = 401
    with patch.object(client._session, "post", return_value=mock_resp_401):
        with pytest.raises(AuthError):
            client.add_watermark(
                str(pdf_file), watermarkType="text", watermarkText="CONFIDENTIAL"
            )

    # 403 Forbidden -> UnauthorizedError
    mock_resp_403 = requests.Response()
    mock_resp_403.status_code = 403
    with patch.object(client._session, "post", return_value=mock_resp_403):
        with pytest.raises(UnauthorizedError):
            client.add_watermark(
                str(pdf_file), watermarkType="text", watermarkText="CONFIDENTIAL"
            )

    # 500 Server Error -> HTTPError
    mock_resp_500 = requests.Response()
    mock_resp_500.status_code = 500
    with patch.object(client._session, "post", return_value=mock_resp_500):
        with pytest.raises(requests.exceptions.HTTPError):
            client.add_watermark(
                str(pdf_file), watermarkType="text", watermarkText="CONFIDENTIAL"
            )


def test_add_watermark_general_exception(tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy pdf content")

    client = StirlingPdfApi(base_url="http://example.com", token="my-token")
    with patch.object(
        client._session, "post", side_effect=Exception("API connection failed")
    ):
        with pytest.raises(Exception, match="API connection failed"):
            client.add_watermark(
                str(pdf_file), watermarkType="text", watermarkText="CONFIDENTIAL"
            )


# ==========================================
# 6. Auth module tests (auth.py)
# ==========================================


def test_auth_get_client():
    import stirlingpdf_agent.auth as auth_mod

    auth_mod._client = None
    with patch.dict(
        os.environ,
        {
            "STIRLINGPDF_URL": "http://test-url",
            "STIRLINGPDF_API_KEY": "test-key",
        },
    ):
        profile = MagicMock()
        client = get_client(profile)
        assert client.base_url == "http://test-url"
        assert client.api_key == "test-key"
        assert client.tls_profile is profile


def test_auth_get_client_auth_error():
    import stirlingpdf_agent.auth as auth_mod

    auth_mod._client = None
    with (
        patch.dict(os.environ, {"STIRLINGPDF_URL": "https://service.invalid"}),
        patch(
            "stirlingpdf_agent.auth.StirlingPdfApi",
            side_effect=AuthError("Mock auth error"),
        ),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            get_client()
        assert "AUTHENTICATION ERROR" in str(exc_info.value)


# ==========================================
# 7. MCP Server tests (mcp_server.py)
# ==========================================


# ==========================================
# 8. Agent Server agent_server.py Tests
# ==========================================
