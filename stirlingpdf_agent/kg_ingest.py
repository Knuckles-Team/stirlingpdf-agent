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
  ``:AssetOccurrence`` via :func:`stirlingpdf_agent.kg_media.ingest_pdf_bytes`.

This module is a thin mapper over the required shared write primitive
``agent_utilities.knowledge_graph.memory.native_ingest``. Engine failures are explicit and
partial writes are never acknowledged. Node ids follow
``stirlingpdf:<class>:<externalId>`` and each ``node_type`` matches a class federated by
``stirlingpdf_agent.ontology``.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_documents as _native_ingest_documents,
)
from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)

logger = logging.getLogger("stirlingpdf_agent.kg")

_SOURCE = "stirlingpdf-agent"
_DOMAIN = "stirlingpdf"
def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write typed OWL nodes (+ edges) into epistemic-graph.

    Nodes use ``node_type`` and relationships use ``relationship``.
    """
    return _native_ingest_entities(
        entities,
        relationships,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
    )


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    The native primitive performs validation, enrichment stamping, and commit.
    """
    return _native_ingest_documents(
        documents,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
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
                "node_type": "PdfTool",
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
    ``input_asset_id`` / ``output_asset_id`` are the ``:AssetOccurrence`` ids returned by
    :func:`stirlingpdf_agent.kg_media.ingest_pdf_bytes`.
    """
    if not action:
        return None
    params = params or {}
    op_id = operation_id or f"stirlingpdf:op:{_slug(action)}:{int(time.time() * 1000)}"
    tool_id = f"stirlingpdf:tool:{_slug(action)}"

    op_node: dict[str, Any] = {
        "id": op_id,
        "node_type": "PdfOperation",
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
            "node_type": "PdfTool",
            "name": action,
            "actionName": action,
            "category": _category_for(action),
            "externalToolId": action,
        },
    ]
    relationships: list[dict[str, Any]] = [
        {"source": op_id, "target": tool_id, "relationship": "usedTool"},
    ]

    if input_asset_id:
        relationships.append(
            {"source": op_id, "target": input_asset_id, "relationship": "hasInput"}
        )
    if output_asset_id:
        relationships.append(
            {"source": op_id, "target": output_asset_id, "relationship": "produced"}
        )
    if input_asset_id and output_asset_id:
        relationships.append(
            {"source": output_asset_id, "target": input_asset_id, "relationship": "derivedFrom"}
        )

    if "watermark" in action.lower() and params.get("watermarkText"):
        wm_id = f"stirlingpdf:watermark:{_slug(str(params.get('watermarkText')))}:{_slug(action)}"
        entities.append(
            {
                "id": wm_id,
                "node_type": "Watermark",
                "name": params.get("watermarkText"),
                "watermarkText": params.get("watermarkText"),
                "watermarkType": params.get("watermarkType", "text"),
                "opacity": params.get("opacity"),
                "rotation": params.get("rotation"),
            }
        )
        relationships.append(
            {"source": op_id, "target": wm_id, "relationship": "appliedWatermark"}
        )

    return ingest_entities(entities, relationships, client=client, graph=graph)
