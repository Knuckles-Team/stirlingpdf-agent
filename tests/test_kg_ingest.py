"""Epistemic-graph typed-node ingestion -- Wire-First coverage for stirlingpdf-agent.

Exercises the real ``ingest_entities`` / ``ingest_actions`` / ``ingest_operation`` seam
against a fake ``agent_connector_sdk.ingest`` transport (no engine required), driven
through ``KnowledgeIngest.submit_blocking`` since every call site here runs on a worker
thread, not the engine's own event loop. The real SDK request builder still runs, so a
malformed change set is still caught by the SDK's own contract, not re-derived here.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import asyncio
import threading
from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest

from stirlingpdf_agent.kg_ingest import (
    ingest_actions,
    ingest_entities,
    ingest_operation,
)


class _FakeTransport:
    """Records every submitted request; no epistemic-graph engine required."""

    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def source_status(self, _connector: str, _stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: Any) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
        )

    async def store_blob(self, _data: bytes) -> str:
        raise AssertionError("stirlingpdf-agent typed-node ingestion carries no media")


@pytest.fixture
def ingest():
    """A ``KnowledgeIngest`` bound to a real background loop (for ``submit_blocking``)."""
    transport = _FakeTransport()
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    service = KnowledgeIngest(transport, loop=loop)
    yield service, transport
    loop.call_soon_threadsafe(loop.stop)
    thread.join(timeout=5)
    loop.close()


def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = ingest_entities(
        [
            {"id": "a", "node_type": "PdfOperation", "name": "op"},
            {"id": "b", "node_type": "PdfTool"},
        ],
        [{"source": "a", "target": "b", "relationship": "usedTool"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    request = transport.requests[0]
    record_ids = {record.record_id for record in request.records}
    assert record_ids == {"a", "b"}
    a_record = next(r for r in request.records if r.record_id == "a")
    assert a_record.payload["name"] == "op"
    assert request.relationships[0].relation_reference.endswith(
        "resources/PdfOperation/relations/usedTool"
    )


def test_ingest_actions_maps_pdf_tools(ingest):
    service, transport = ingest
    res = ingest_actions(
        ["add_watermark", {"name": "merge_pdfs"}, "ocr_pdf"],
        ingest=service,
    )
    assert res == {"nodes": 3, "edges": 0}
    request = transport.requests[0]
    tool = next(
        r for r in request.records if r.record_id == "stirlingpdf:tool:add-watermark"
    )
    assert tool.payload["actionName"] == "add_watermark"
    assert tool.payload["category"] == "general"
    ocr = next(
        r for r in request.records if r.record_id == "stirlingpdf:tool:ocr-pdf"
    )
    assert ocr.payload["category"] == "misc"
    merge = next(
        r for r in request.records if r.record_id == "stirlingpdf:tool:merge-pdfs"
    )
    assert merge.payload["externalToolId"] == "merge_pdfs"


def test_ingest_operation_wires_provenance_and_watermark(ingest):
    service, transport = ingest
    res = ingest_operation(
        "add_watermark",
        operation_id="stirlingpdf:op:add-watermark:1",
        params={"watermarkText": "DRAFT", "opacity": "0.3"},
        input_asset_id="media:in",
        output_asset_id="media:out",
        size_bytes=2048,
        ingest=service,
    )
    assert res is not None
    assert res["nodes"] == 3
    request = transport.requests[0]
    op = next(
        r
        for r in request.records
        if r.record_id == "stirlingpdf:op:add-watermark:1"
    )
    assert op.payload["actionName"] == "add_watermark"
    assert op.payload["status"] == "success"
    assert op.payload["sizeBytes"] == 2048
    assert any(
        r.record_id == "stirlingpdf:tool:add-watermark" for r in request.records
    )
    watermark = [r for r in request.records if r.payload.get("watermarkText")]
    assert watermark and watermark[0].payload["watermarkText"] == "DRAFT"
    edge_types = sorted(
        rel.relation_reference.rsplit("/", 1)[-1] for rel in request.relationships
    )
    assert edge_types == [
        "appliedWatermark",
        "derivedFrom",
        "hasInput",
        "produced",
        "usedTool",
    ]


def test_ingest_actions_and_operation_empty_is_noop(ingest):
    service, transport = ingest
    assert ingest_actions([], ingest=service) is None
    assert ingest_operation("", ingest=service) is None
    assert transport.requests == []


def test_retired_structural_alias_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="node_type"):
        ingest_entities([{"id": "a", "type": "PdfTool"}], ingest=service)


def test_empty_native_ingest_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        ingest_entities([], ingest=service)
