"""Typed file-bytes operations: base64 or workspace-path input, bytes output."""

import base64
from unittest.mock import MagicMock

import pytest
import requests
from scion_sdk.exceptions import ParameterError

from stirlingpdf_agent.api_client import StirlingPdfApi

PDF = b"%PDF-1.4 sample"
B64 = base64.b64encode(PDF).decode()


def _client(content: bytes = b"out") -> StirlingPdfApi:
    client = StirlingPdfApi(base_url="http://pdf.test", token="key")
    response = requests.Response()
    response.status_code = 200
    response._content = content
    client._session.post = MagicMock(return_value=response)
    return client


@pytest.mark.parametrize(
    ("method", "kwargs", "route", "field"),
    [
        ("rotate_pdf", {"angle": 90}, "general/rotate-pdf", ("angle", "90")),
        (
            "compress_pdf",
            {"optimize_level": 7},
            "misc/compress-pdf",
            ("optimizeLevel", "7"),
        ),
        (
            "split_pdf",
            {"page_numbers": "1,3"},
            "general/split-pages",
            ("pageNumbers", "1,3"),
        ),
        (
            "add_password",
            {"password": "pw"},
            "security/add-password",
            ("password", "pw"),
        ),
        (
            "remove_password",
            {"password": "pw"},
            "security/remove-password",
            ("password", "pw"),
        ),
        (
            "sanitize_pdf",
            {"remove_links": True},
            "security/sanitize-pdf",
            ("removeLinks", "true"),
        ),
    ],
)
def test_single_file_operations_post_the_decoded_bytes(method, kwargs, route, field):
    client = _client(b"result")
    result = getattr(client, method)(file_base64=B64, filename="a.pdf", **kwargs)
    assert result.data == b"result"
    call = client._session.post.call_args.kwargs
    assert call["url"].endswith(f"/api/v1/{route}")
    assert call["data"][field[0]] == field[1]
    name, content, mime = call["files"][0][1]
    assert (name, content, mime) == ("a.pdf", PDF, "application/pdf")


def test_filepath_input_is_read_from_disk(tmp_path):
    path = tmp_path / "in.pdf"
    path.write_bytes(PDF)
    client = _client()
    client.rotate_pdf(angle=180, filepath=str(path))
    assert client._session.post.call_args.kwargs["files"][0][1][1] == PDF


def test_merge_sends_every_file_in_order():
    client = _client()
    client.merge_pdfs([B64, base64.b64encode(b"%PDF second").decode()])
    files = client._session.post.call_args.kwargs["files"]
    assert [item[1][1] for item in files] == [PDF, b"%PDF second"]


def test_merge_needs_two_files():
    with pytest.raises(ParameterError):
        _client().merge_pdfs([B64])


@pytest.mark.parametrize(
    "kwargs",
    [{}, {"filepath": "x", "file_base64": B64}, {"file_base64": "not base64!!"}],
)
def test_input_must_be_exactly_one_valid_source(kwargs):
    with pytest.raises(ParameterError):
        _client().rotate_pdf(angle=90, **kwargs)


def test_oversized_input_is_refused(monkeypatch):
    monkeypatch.setenv("STIRLINGPDF_MAX_FILE_BYTES", "4")
    with pytest.raises(ParameterError):
        _client().rotate_pdf(angle=90, file_base64=B64)
