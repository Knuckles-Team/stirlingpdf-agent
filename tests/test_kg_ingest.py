"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_actions`` / ``ingest_operation`` seam with
a fake engine client (no engine required), asserting the txn add_node/commit + edge calls and
the Stirling action → :PdfTool / operation → :PdfOperation mappings.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from stirlingpdf_agent.kg_ingest import (
    ingest_actions,
    ingest_entities,
    ingest_operation,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def commit(self, txn):
        self.committed = True
        return True


class _FakeEdges:
    def __init__(self):
        self.edges = []

    def add(self, src, dst, props):
        self.edges.append((src, dst, props))


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()
        self.edges = _FakeEdges()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "type": "PdfOperation", "name": "op"},
            {"id": "b", "type": "PdfTool"},
        ],
        [{"source": "a", "target": "b", "type": "usedTool"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "stirlingpdf-agent"
    assert c.txn.nodes["a"]["domain"] == "stirlingpdf"
    assert c.edges.edges == [("a", "b", {"type": "usedTool"})]


def test_ingest_actions_maps_pdf_tools():
    c = _FakeClient()
    res = ingest_actions(
        ["add_watermark", {"name": "merge_pdfs"}, "ocr_pdf"],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 3, "edges": 0}
    assert c.txn.nodes["stirlingpdf:tool:add-watermark"]["type"] == "PdfTool"
    assert (
        c.txn.nodes["stirlingpdf:tool:add-watermark"]["actionName"] == "add_watermark"
    )
    assert c.txn.nodes["stirlingpdf:tool:add-watermark"]["category"] == "general"
    assert c.txn.nodes["stirlingpdf:tool:ocr-pdf"]["category"] == "misc"
    assert c.txn.nodes["stirlingpdf:tool:merge-pdfs"]["externalToolId"] == "merge_pdfs"


def test_ingest_operation_wires_provenance_and_watermark():
    c = _FakeClient()
    res = ingest_operation(
        "add_watermark",
        operation_id="stirlingpdf:op:add-watermark:1",
        params={"watermarkText": "DRAFT", "opacity": "0.3"},
        input_asset_id="media:in",
        output_asset_id="media:out",
        size_bytes=2048,
        client=c,
        graph="__commons__",
    )
    # op + tool + watermark nodes
    assert res["nodes"] == 3
    op = c.txn.nodes["stirlingpdf:op:add-watermark:1"]
    assert op["type"] == "PdfOperation"
    assert op["actionName"] == "add_watermark"
    assert op["status"] == "success"
    assert op["sizeBytes"] == 2048
    assert c.txn.nodes["stirlingpdf:tool:add-watermark"]["type"] == "PdfTool"
    # a :Watermark node was emitted
    wm = [n for n in c.txn.nodes.values() if n.get("type") == "Watermark"]
    assert wm and wm[0]["watermarkText"] == "DRAFT"
    # provenance edges: usedTool, hasInput, produced, derivedFrom, appliedWatermark
    edge_types = sorted(p["type"] for _, _, p in c.edges.edges)
    assert edge_types == [
        "appliedWatermark",
        "derivedFrom",
        "hasInput",
        "produced",
        "usedTool",
    ]
    assert ("media:out", "media:in", {"type": "derivedFrom"}) in c.edges.edges


def test_ingest_noops_without_engine():
    # No injected client + no reachable engine -> clean no-op.
    assert ingest_entities([{"id": "a", "type": "PdfTool"}]) is None


def test_ingest_empty_is_noop():
    assert ingest_entities([], client=_FakeClient()) is None
    assert ingest_actions([], client=_FakeClient()) is None
    assert ingest_operation("", client=_FakeClient()) is None
