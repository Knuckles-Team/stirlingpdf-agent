"""Native epistemic-graph blob ingestion for Stirling PDF artifacts.

CONCEPT:AU-KG.ingest.list-durable-media. Stirling PDF operations consume and produce raw
PDF bytes. When a live epistemic-graph engine is reachable, those bytes are stored as a
content-addressed **blob** with a ``:AssetOccurrence`` graph node (carrying the operation
metadata) in ONE cross-modal ACID commit, via the agent-utilities ``MediaStore`` (or the
shared ``native_ingest.media_store`` when that primitive is present). This makes the actual
PDF — not just a filesystem path — durable, deduped, and queryable in the knowledge graph,
so ``stirlingpdf_agent.kg_ingest.ingest_operation`` can wire ``:derivedFrom`` provenance
between the input and output PDFs.

Entirely best-effort and dependency-guarded: with no agent-utilities KG stack or no live
engine, every entry point **no-ops** (returns ``None``), so the connector keeps working
with zero KG infrastructure.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("stirlingpdf_agent.kg.media")

_SOURCE = "stirlingpdf-agent"


def _media_store() -> Any | None:
    """Build a ``MediaStore`` over a live engine, or ``None`` when unavailable."""
    # Prefer the shared primitive when it is importable.
    try:
        from agent_utilities.knowledge_graph.memory import native_ingest

        store = native_ingest.media_store()
        if store is not None:
            return store
    except Exception as e:  # noqa: BLE001 — primitive not yet installed
        logger.debug("Operation failed: error_type=%s", type(e).__name__)

    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
        from agent_utilities.knowledge_graph.memory.media_store import MediaStore
    except Exception as e:  # noqa: BLE001 — agent-utilities KG stack absent
        logger.debug("Operation failed: error_type=%s", type(e).__name__)
        return None
    try:
        engine = GraphComputeEngine()
        if getattr(engine, "_client", None) is None:
            logger.debug("KG media ingest: no live engine client")
            return None
        return MediaStore(engine)
    except Exception as e:  # noqa: BLE001 — no reachable engine
        logger.debug("Operation failed: error_type=%s", type(e).__name__)
        return None


def ingest_pdf_bytes(
    data: bytes | None,
    *,
    name: str = "document.pdf",
    action: str = "",
    role: str = "output",
    mime_type: str = "application/pdf",
    extra: dict[str, Any] | None = None,
    source: str = _SOURCE,
    media_store: Any | None = None,
) -> dict[str, Any] | None:
    """Store raw PDF ``data`` as a blob + ``:AssetOccurrence`` in the knowledge graph.

    ``role`` records whether this artifact was the operation's ``input`` or ``output``;
    ``action`` records the Stirling action that touched it. Returns
    ``{asset_id, digest, size_bytes, media_type}`` on success, or ``None`` when there is no
    engine or no bytes (never raises). ``media_store`` may be injected (tests).
    """
    if not data:
        return None
    store = media_store if media_store is not None else _media_store()
    if store is None:
        return None

    meta: dict[str, Any] = {"role": role}
    if action:
        meta["action"] = action
    if extra:
        meta.update({k: v for k, v in extra.items() if v is not None})

    try:
        stored = store.store_media(
            data,
            media_type="document",
            mime_type=mime_type,
            source=source,
            name=name,
            extra=meta,
        )
    except Exception as e:  # noqa: BLE001 — engine/store failure is non-fatal
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return None
    if stored is None:
        return None

    logger.info(
        "KG media ingest: stored %s (%s bytes) as asset %s digest %s",
        name,
        len(data),
        stored.asset_id,
        stored.digest[:16],
    )
    return {
        "asset_id": stored.asset_id,
        "digest": stored.digest,
        "size_bytes": len(data),
        "media_type": "document",
    }


def ingest_pdf_file(
    file_path: str | None,
    *,
    action: str = "",
    role: str = "input",
    extra: dict[str, Any] | None = None,
    source: str = _SOURCE,
    media_store: Any | None = None,
) -> dict[str, Any] | None:
    """Read a PDF file from disk and store it via :func:`ingest_pdf_bytes`."""
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as fh:
            data = fh.read()
    except OSError as e:
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return None
    return ingest_pdf_bytes(
        data,
        name=os.path.basename(file_path),
        action=action,
        role=role,
        extra=extra,
        source=source,
        media_store=media_store,
    )
