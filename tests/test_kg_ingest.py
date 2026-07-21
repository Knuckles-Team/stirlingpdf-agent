"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_actions`` / ``ingest_operation`` seam with
a fake engine client (no engine required), asserting the single-transaction node/edge staging and commit and
the Stirling action → :PdfTool / operation → :PdfOperation mappings.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.models.company_brain import ActorType
from agent_utilities.security.brain_context import ActorContext

from stirlingpdf_agent.kg_ingest import (
    ingest_actions,
    ingest_entities,
    ingest_operation,
)


@pytest.fixture(autouse=True)
def _verified_graph_session():
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.SYSTEM,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="__commons__",
        audience="epistemic-graph",
        policy_version="policy:synthetic",
    )
    with use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "PdfOperation", "name": "op"},
            {"id": "b", "node_type": "PdfTool"},
        ],
        [{"source": "a", "target": "b", "relationship": "usedTool"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) == 1
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "stirlingpdf-agent"
    assert c.nodes.values["a"]["domain"] == "stirlingpdf"
    assert c.changes.edges == [("a", "b", {"relationship": "usedTool"})]


def test_ingest_actions_maps_pdf_tools():
    c = _FakeClient()
    res = ingest_actions(
        ["add_watermark", {"name": "merge_pdfs"}, "ocr_pdf"],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 3, "edges": 0}
    assert c.nodes.values["stirlingpdf:tool:add-watermark"]["node_type"] == "PdfTool"
    assert (
        c.nodes.values["stirlingpdf:tool:add-watermark"]["actionName"]
        == "add_watermark"
    )
    assert c.nodes.values["stirlingpdf:tool:add-watermark"]["category"] == "general"
    assert c.nodes.values["stirlingpdf:tool:ocr-pdf"]["category"] == "misc"
    assert (
        c.nodes.values["stirlingpdf:tool:merge-pdfs"]["externalToolId"] == "merge_pdfs"
    )


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
    assert res is not None
    assert res["nodes"] == 3
    op = c.nodes.values["stirlingpdf:op:add-watermark:1"]
    assert op["node_type"] == "PdfOperation"
    assert op["actionName"] == "add_watermark"
    assert op["status"] == "success"
    assert op["sizeBytes"] == 2048
    assert c.nodes.values["stirlingpdf:tool:add-watermark"]["node_type"] == "PdfTool"
    # a :Watermark node was emitted
    wm = [n for n in c.nodes.values.values() if n.get("node_type") == "Watermark"]
    assert wm and wm[0]["watermarkText"] == "DRAFT"
    # provenance edges: usedTool, hasInput, produced, derivedFrom, appliedWatermark
    edge_types = sorted(p["relationship"] for _, _, p in c.changes.edges)
    assert edge_types == [
        "appliedWatermark",
        "derivedFrom",
        "hasInput",
        "produced",
        "usedTool",
    ]
    assert (
        "media:out",
        "media:in",
        {"relationship": "derivedFrom"},
    ) in c.changes.edges


def test_ingest_actions_and_operation_empty_is_noop():
    # Nothing to map -> a clean no-op before the strict native-ingest layer is reached.
    assert ingest_actions([], client=_FakeClient()) is None
    assert ingest_operation("", client=_FakeClient()) is None


def test_retired_structural_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "a", "type": "PdfTool"}], client=_FakeClient())


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
