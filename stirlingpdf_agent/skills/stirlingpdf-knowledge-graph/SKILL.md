---
name: stirlingpdf-knowledge-graph
skill_type: skill
description: >-
  Natively ingest Stirling PDF activity into the epistemic-graph knowledge graph —
  available actions as :PdfTool nodes, executed operations as :PdfOperation nodes,
  and the raw input/output PDF bytes as :Blob / :MediaAsset with :derivedFrom
  provenance — via the stirlingpdf-agent MCP server. Use when the agent must make
  PDF operations durable, deduped, and queryable. Do NOT use to actually transform
  a PDF (use stirlingpdf-watermarking or stirlingpdf-document-operations).
license: MIT
tags: [stirlingpdf, pdf, knowledge-graph, ingestion, provenance, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# Stirling PDF → Knowledge Graph

Push Stirling PDF activity into the ONE epistemic-graph engine as typed OWL nodes with
document provenance. Ingestion is **native and default-on**: every successful
`add_watermark` automatically records its `:PdfOperation` plus the input/output PDF blobs
and their `:derivedFrom` link when an engine is reachable. This skill covers the explicit
tool for discovering + ingesting the instance's tool catalog, and the model it writes.

## When to use
- Register a Stirling instance's available actions as durable `:PdfTool` nodes.
- Make PDF operations + their artifacts queryable (which PDF derived from which, what
  watermark was applied, which tool ran).
- Feed a KG-backed audit / provenance trail of document processing.

## When NOT to use
- Actually watermarking or transforming a PDF → `stirlingpdf-watermarking` /
  `stirlingpdf-document-operations` (those auto-ingest; this skill is the KG seam).
- Generic graph queries unrelated to Stirling → the graph-os query tools.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`stirlingpdf-agent`** MCP server, plus a
reachable epistemic-graph engine (`GraphComputeEngine`). With **no** engine, every
ingestion entry point **no-ops** cleanly — nothing fails.

| Variable | Required | Notes |
|----------|----------|-------|
| `STIRLINGPDF_URL` | ✅ | Base URL of the Stirling PDF instance |
| `STIRLINGPDF_API_KEY` | optional | Sent as `X-API-KEY` |

## Tools & actions
| Tool | Purpose |
|------|---------|
| `stirlingpdf_ingest_tools` | Discover available actions (`list_actions`) and ingest them as `:PdfTool` nodes |
| `pdf_action` (`add_watermark`) | Auto-ingests a `:PdfOperation` + input/output blobs on success |

`stirlingpdf_ingest_tools` takes no parameters; it returns `{"listed": N, "ingested": {...}}`.

## Ontology it writes (domain `stirlingpdf`)
- `:PdfTool` — an available Stirling action (`stirlingpdf:tool:<slug>`).
- `:PdfOperation` — one executed action (`stirlingpdf:op:<action>:<ts>`), `:usedTool` →
  `:PdfTool`, `:produced` → output `:MediaAsset`, `:hasInput` → input `:MediaAsset`.
- `:Watermark` — for watermark ops, linked via `:appliedWatermark`.
- Output `:MediaAsset` → `:derivedFrom` → input `:MediaAsset` (document provenance).
- Raw PDF bytes reuse the shared `:Blob` / `:MediaAsset` classes; extracted text reuses
  `:Document`.

## Recipes
Ingest the instance tool catalog (call `stirlingpdf_ingest_tools`, no params):
```json
{}
```
Then just run watermark/document operations normally — provenance is recorded
automatically. Node ids are stable: `stirlingpdf:<class>:<externalId>`.

## Gotchas
- Ingestion is **best-effort**: no engine ⇒ clean no-op (`{"ingested": null}`), never an
  error — a watermark call never fails because the KG is down.
- Blobs are content-addressed + deduped by digest; re-ingesting identical bytes is cheap.
- `type` on every node matches a class in `stirlingpdf_agent/ontology/stirlingpdf.ttl`;
  don't invent types.
- The engine client is the lightweight `GraphComputeEngine()._client`, not the heavy
  in-process ingestion engine.

## Related
- `stirlingpdf-watermarking`, `stirlingpdf-document-operations` — the operations that
  feed this graph.
- `stirlingpdf-agent-docs` — Stirling PDF reference documentation.
