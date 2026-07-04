"""Native epistemic-graph blob ingestion — Wire-First coverage.

Exercises the real ``ingest_pdf_bytes`` / ``ingest_pdf_file`` seam with a fake ``MediaStore``
(no engine required), asserting the store_media call and metadata propagation.
CONCEPT:AU-KG.ingest.list-durable-media.
"""

from __future__ import annotations

from dataclasses import dataclass

from stirlingpdf_agent.kg_media import ingest_pdf_bytes, ingest_pdf_file


@dataclass
class _Stored:
    asset_id: str
    digest: str


class _FakeMediaStore:
    """Captures the store_media call the way the real MediaStore is invoked."""

    def __init__(self):
        self.calls = []

    def store_media(self, data, **kw):
        self.calls.append((data, kw))
        return _Stored(asset_id="stirlingpdf:asset:deadbeef", digest="deadbeef")


def test_ingest_pdf_bytes_stores_bytes_and_metadata():
    store = _FakeMediaStore()
    data = b"%PDF-1.7 fake-bytes"

    res = ingest_pdf_bytes(
        data,
        name="watermarked.pdf",
        action="add_watermark",
        role="output",
        media_store=store,
    )

    assert res is not None
    assert res["asset_id"] == "stirlingpdf:asset:deadbeef"
    assert res["digest"] == "deadbeef"
    assert res["media_type"] == "document"
    assert res["size_bytes"] == len(data)

    assert len(store.calls) == 1
    sent, kw = store.calls[0]
    assert sent == data
    assert kw["source"] == "stirlingpdf-agent"
    assert kw["mime_type"] == "application/pdf"
    assert kw["media_type"] == "document"
    assert kw["name"] == "watermarked.pdf"
    assert kw["extra"]["role"] == "output"
    assert kw["extra"]["action"] == "add_watermark"


def test_ingest_pdf_file_reads_and_stores(tmp_path):
    f = tmp_path / "input.pdf"
    f.write_bytes(b"%PDF-1.7 on-disk")
    store = _FakeMediaStore()

    res = ingest_pdf_file(
        str(f), action="add_watermark", role="input", media_store=store
    )

    assert res is not None
    assert res["size_bytes"] == f.stat().st_size
    sent, kw = store.calls[0]
    assert sent == f.read_bytes()
    assert kw["name"] == "input.pdf"
    assert kw["extra"]["role"] == "input"


def test_ingest_pdf_bytes_noops_without_engine():
    """No injected store + no reachable engine -> clean no-op (never raises)."""
    assert ingest_pdf_bytes(b"%PDF-1.7") is None


def test_ingest_pdf_bytes_noops_on_empty():
    assert ingest_pdf_bytes(b"", media_store=_FakeMediaStore()) is None


def test_ingest_pdf_file_noops_on_missing_file():
    assert ingest_pdf_file("/no/such/file.pdf", media_store=_FakeMediaStore()) is None
