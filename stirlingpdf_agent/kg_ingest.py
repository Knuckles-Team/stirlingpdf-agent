"""Native epistemic-graph ingestion for Stirling PDF operations (typed nodes + docs).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The stirlingpdf-agent natively pushes
its data into the ONE epistemic-graph engine from its own code, in every modality that
applies to a PDF toolbox:

* **typed nodes** — the available Stirling actions become ``:PdfTool`` nodes and each
  executed operation becomes a ``:PdfOperation`` node (+ ``:usedTool`` / ``:produced`` /
  ``:derivedFrom`` provenance edges), via :func:`ingest_entities`.
* **documents** — text worth semantic search (e.g. an operation summary, extracted text)
  becomes ``:Document`` nodes carrying the text + ``source_uri``, via :func:`ingest_documents`.
* **blobs** — the raw PDF bytes (input and output artifacts) are stored as ``:Blob`` +
  ``:MediaAsset`` via :func:`stirlingpdf_agent.kg_media.ingest_pdf_bytes`.

This module is a thin mapper. It prefers the shared write primitive
``agent_utilities.knowledge_graph.memory.native_ingest`` when that is importable; otherwise
it falls back to a self-contained txn against the lightweight engine client
(``GraphComputeEngine()._client``). Either way it is dependency-/engine-guarded: with no KG
stack or no reachable engine every entry point **no-ops** (returns ``None``), so the connector
runs with zero KG infrastructure. Node ids follow ``stirlingpdf:<class>:<externalId>`` and
each ``type`` matches a class federated by ``stirlingpdf_agent.ontology``.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

logger = logging.getLogger("stirlingpdf_agent.kg")

_SOURCE = "stirlingpdf-agent"
_DOMAIN = "stirlingpdf"
_DEFAULT_GRAPH = "__commons__"


def _primitive() -> Any | None:
    """Return the shared native_ingest module, or ``None`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.memory import native_ingest

        return native_ingest
    except Exception as e:  # noqa: BLE001 — primitive not yet in installed agent_utilities
        logger.debug("native_ingest primitive unavailable: %s", e)
        return None


def _client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        graph = getattr(engine, "graph_name", None) or _DEFAULT_GRAPH
        return client, graph
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed OWL nodes (+ edges) into epistemic-graph.

    ``entities``: ``[{"id":..., "type":<owl:Class>, ...props}]``.
    ``relationships``: ``[{"source":id, "target":id, "type":<link>}]``.
    Returns ``{"nodes":n, "edges":m}`` or ``None`` (no engine / failure; never raises).
    ``client``/``graph`` may be injected (tests); otherwise resolved on demand.
    """
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None

    prim = _primitive()
    if prim is not None and client is None:
        return prim.ingest_entities(
            entities, relationships, source=source, domain=domain
        )

    if client is None:
        client, graph = _client()
    if client is None:
        return None
    graph = graph or _DEFAULT_GRAPH

    try:
        txn = client.txn.begin(graph=graph)
        for ent in entities:
            props = {k: v for k, v in ent.items() if k != "id" and v is not None}
            props.setdefault("source", source)
            props.setdefault("domain", domain)
            client.txn.add_node(txn, ent["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None

    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)

    logger.info("KG ingest: wrote %d nodes, %d edges", len(entities), edges)
    return {"nodes": len(entities), "edges": edges}


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    Returns ``{"nodes":n, "edges":0}`` or ``None``.
    """
    prim = _primitive()
    if prim is not None and client is None:
        return prim.ingest_documents(documents, source=source, domain=domain)

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    nodes: list[dict[str, Any]] = []
    for doc in documents or []:
        did = doc.get("id")
        text = doc.get("text") or doc.get("content")
        if not did or not text:
            continue
        node = {k: v for k, v in doc.items() if k != "content" and v is not None}
        node["id"] = did
        node["type"] = "Document"
        node["text"] = text
        node.setdefault("created_at", now)
        nodes.append(node)
    if not nodes:
        return None
    return ingest_entities(
        nodes, None, source=source, domain=domain, client=client, graph=graph
    )


def _slug(value: str) -> str:
    """Make a stable, id-safe slug from an action / endpoint name."""
    return re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")


# Rough endpoint-category classification used when mapping tools/operations. Stirling
# groups its REST surface into these families; the action name is a good proxy.
_CATEGORY_HINTS = (
    ("watermark", "general"),
    ("merge", "general"),
    ("split", "general"),
    ("rotate", "general"),
    ("password", "security"),
    ("sanitize", "security"),
    ("stamp", "security"),
    ("cert", "security"),
    ("sign", "security"),
    ("convert", "convert"),
    ("img", "convert"),
    ("image", "convert"),
    ("word", "convert"),
    ("html", "convert"),
    ("ocr", "misc"),
    ("compress", "misc"),
    ("repair", "misc"),
    ("metadata", "misc"),
    ("pipeline", "pipeline"),
)


def _category_for(action: str) -> str:
    low = (action or "").lower()
    for needle, cat in _CATEGORY_HINTS:
        if needle in low:
            return cat
    return "general"


def ingest_actions(
    actions: list[str] | list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map Stirling PDF action names → ``:PdfTool`` nodes and ingest them.

    ``actions`` is the ``list_actions`` result: a list of method-name strings (or dicts
    carrying a ``name``/``action``). Each becomes a durable ``:PdfTool`` node describing an
    available endpoint on this Stirling instance.
    """
    entities: list[dict[str, Any]] = []
    for item in actions or []:
        name = (
            item if isinstance(item, str) else (item.get("name") or item.get("action"))
        )
        if not name:
            continue
        entities.append(
            {
                "id": f"stirlingpdf:tool:{_slug(name)}",
                "type": "PdfTool",
                "name": name,
                "actionName": name,
                "category": _category_for(name),
                "externalToolId": name,
            }
        )
    return ingest_entities(entities, None, client=client, graph=graph)


def ingest_operation(
    action: str,
    *,
    operation_id: str | None = None,
    params: dict[str, Any] | None = None,
    input_asset_id: str | None = None,
    output_asset_id: str | None = None,
    status: str = "success",
    size_bytes: int | None = None,
    mime_type: str = "application/pdf",
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map one executed Stirling PDF operation → a ``:PdfOperation`` node + provenance.

    Links the operation to the ``:PdfTool`` it dispatched (``:usedTool``), to the produced
    output blob (``:produced``), to its input blob (``:hasInput``), and — when both blob ids
    are present — records the ``:derivedFrom`` provenance edge from output back to input.
    For add-watermark operations, also emits a ``:Watermark`` node (``:appliedWatermark``).
    ``input_asset_id`` / ``output_asset_id`` are the ``:MediaAsset`` ids returned by
    :func:`stirlingpdf_agent.kg_media.ingest_pdf_bytes`.
    """
    if not action:
        return None
    params = params or {}
    op_id = operation_id or f"stirlingpdf:op:{_slug(action)}:{int(time.time() * 1000)}"
    tool_id = f"stirlingpdf:tool:{_slug(action)}"

    op_node: dict[str, Any] = {
        "id": op_id,
        "type": "PdfOperation",
        "name": action,
        "actionName": action,
        "category": _category_for(action),
        "status": status,
        "mimeType": mime_type,
    }
    if size_bytes is not None:
        op_node["sizeBytes"] = size_bytes

    entities: list[dict[str, Any]] = [
        op_node,
        {
            "id": tool_id,
            "type": "PdfTool",
            "name": action,
            "actionName": action,
            "category": _category_for(action),
            "externalToolId": action,
        },
    ]
    relationships: list[dict[str, Any]] = [
        {"source": op_id, "target": tool_id, "type": "usedTool"},
    ]

    if input_asset_id:
        relationships.append(
            {"source": op_id, "target": input_asset_id, "type": "hasInput"}
        )
    if output_asset_id:
        relationships.append(
            {"source": op_id, "target": output_asset_id, "type": "produced"}
        )
    if input_asset_id and output_asset_id:
        relationships.append(
            {"source": output_asset_id, "target": input_asset_id, "type": "derivedFrom"}
        )

    if "watermark" in action.lower() and params.get("watermarkText"):
        wm_id = f"stirlingpdf:watermark:{_slug(str(params.get('watermarkText')))}:{_slug(action)}"
        entities.append(
            {
                "id": wm_id,
                "type": "Watermark",
                "name": params.get("watermarkText"),
                "watermarkText": params.get("watermarkText"),
                "watermarkType": params.get("watermarkType", "text"),
                "opacity": params.get("opacity"),
                "rotation": params.get("rotation"),
            }
        )
        relationships.append(
            {"source": op_id, "target": wm_id, "type": "appliedWatermark"}
        )

    return ingest_entities(entities, relationships, client=client, graph=graph)
