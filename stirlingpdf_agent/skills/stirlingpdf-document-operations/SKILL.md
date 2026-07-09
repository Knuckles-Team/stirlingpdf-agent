---
name: stirlingpdf-document-operations
skill_type: skill
description: >-
  Run any Stirling PDF operation — merge, split, rotate, convert, compress, OCR,
  metadata, and document-security actions (password / sanitize / stamp) — through
  the stirlingpdf-agent MCP server's dynamic dispatch tool. Use when the agent
  must transform, convert, or secure a PDF on a self-hosted Stirling instance and
  first needs to discover which actions the instance exposes. Do NOT use for the
  dedicated watermark flow (use stirlingpdf-watermarking) or for ingesting results
  into the knowledge graph (use stirlingpdf-knowledge-graph).
license: MIT
tags: [stirlingpdf, pdf, convert, ocr, security, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# Stirling PDF Document Operations

Drive the full Stirling PDF REST surface through the **`stirlingpdf-agent`** MCP server's
**dynamic dispatch** tool. `pdf_action` resolves any action the client exposes by name,
so new Stirling endpoints are reachable without a code change — always discover with
`list_actions` first, then dispatch.

## When to use
- Transform PDFs: `merge`, `split`, `rotate`, `compress`, `repair`.
- Convert to/from PDF: image ↔ PDF, Office ↔ PDF, HTML ↔ PDF.
- Extract / OCR: `ocr`, text/metadata extraction.
- Secure a document: `add_password`, `remove_password`, `sanitize`, `add_stamp`.

## When NOT to use
- Applying a watermark → `stirlingpdf-watermarking` (the first-class typed flow).
- Persisting operations/artifacts into the KG → `stirlingpdf-knowledge-graph`.
- Reading Stirling's own docs → `stirlingpdf-agent-docs`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`stirlingpdf-agent`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `STIRLINGPDF_URL` | ✅ | Base URL of the Stirling PDF instance |
| `STIRLINGPDF_API_KEY` | optional | Sent as `X-API-KEY` (alias `STIRLINGPDF_TOKEN`) |
| `STIRLINGPDF_SSL_VERIFY` | optional | TLS verification toggle |

Input files are resolved on the **server** filesystem (`filepath`).

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `pdf_action` | `list_actions` | Enumerate every available action on this instance |
| `pdf_action` | `<action>` | Dispatch that action with `params_json` |

`pdf_action` takes `action` + a `params_json` **JSON string**; unknown actions return a
did-you-mean error listing the real ones, so `list_actions` is the safe first call.

## Recipes (`params_json`)
Discover the surface (call `action="list_actions"`):
```json
{}
```
Dispatch a discovered action (shape depends on the action's parameters):
```json
{"filepath":"/data/input.pdf"}
```
Watermark example, to show the dispatch shape (prefer the watermark skill):
```json
{"filepath":"/data/input.pdf","watermarkType":"text","watermarkText":"CONFIDENTIAL"}
```

## Gotchas
- **Always** `list_actions` before dispatching — the exact action set is instance- and
  build-dependent; only `add_watermark` is guaranteed by the typed client.
- `params_json` is a **string** of JSON; per-action parameter names/casing follow
  Stirling's REST fields (often camelCase strings).
- File inputs are server-side paths; the response `data` is base64 PDF bytes.
- `list_actions`, `help`, and `actions` are discovery aliases — they never mutate.

## Related
- `stirlingpdf-watermarking` — the dedicated, typed watermark operation.
- `stirlingpdf-knowledge-graph` — record dispatched operations + their input/output
  PDFs and `:derivedFrom` provenance in the knowledge graph.
- `stirlingpdf-agent-docs` — full Stirling PDF reference documentation.
