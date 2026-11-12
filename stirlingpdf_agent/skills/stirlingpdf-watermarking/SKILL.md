---
name: stirlingpdf-watermarking
skill_type: skill
description: >-
  Stamp text (or image) watermarks onto a PDF via the stirlingpdf-agent MCP
  server's typed watermark tool. Use when the agent must brand, mark DRAFT/CONFIDENTIAL,
  or overlay repeating text on a PDF using a self-hosted Stirling PDF instance.
  Do NOT use for password protection / redaction (that is document security), for
  merge/split/convert/OCR (use stirlingpdf-document-operations), or for pushing
  results into the knowledge graph (use stirlingpdf-knowledge-graph).
license: MIT
tags: [stirlingpdf, pdf, watermark, rest-api, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# Stirling PDF Watermarking

Apply a watermark to a PDF through the **`stirlingpdf-agent`** MCP server. This is the
one fully-typed, first-class operation the client implements (`add_watermark` →
`POST /api/v1/general/add-watermark`); it returns the watermarked PDF bytes and, when a
knowledge-graph engine is reachable, natively records the operation (see Related).

## When to use
- Overlay repeating **text** (e.g. `DRAFT`, `CONFIDENTIAL`, a name) across every page.
- Brand a PDF before sharing, with controllable opacity / rotation / spacing.

## When NOT to use
- Password-protect, redact, or sanitize a PDF → document-security operations via
  `stirlingpdf-document-operations` (`stirlingpdf_add_password`, `stirlingpdf_sanitize_pdf`).
- Merge / split / rotate / convert / compress / OCR → `stirlingpdf-document-operations`.
- Persisting the result into the KG → `stirlingpdf-knowledge-graph`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`stirlingpdf-agent`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `STIRLINGPDF_URL` | ✅ | Base URL of the Stirling PDF instance (default `http://localhost:8080`) |
| `STIRLINGPDF_API_KEY` | optional | Sent as `X-API-KEY` (alias `STIRLINGPDF_TOKEN`) |
| `STIRLINGPDF_SSL_VERIFY` | optional | TLS verification toggle |


## Tools
| Tool | Purpose |
|------|---------|
| `stirlingpdf_add_watermark` | Stamp a watermark onto the PDF given as `file_base64` or `filepath` |
| `stirlingpdf_get_status` | Read the server status and version before a batch |

### Key parameters (`stirlingpdf_add_watermark`)
- `file_base64` or `filepath` - exactly one; the input PDF as base64 bytes, or a path on the server.
- `watermarkType` - `text` (or `image`).
- `watermarkText` - the text to render.
- `opacity` (`0.0`-`1.0`), `rotation` (degrees), `fontSize`, `alphabet` (`roman`),
  `widthSpacer`, `heightSpacer` - all optional strings with sensible defaults.

## Recipes
Stamp a semi-transparent DRAFT watermark on uploaded bytes:
```json
{"file_base64":"<base64 pdf>","watermarkType":"text","watermarkText":"DRAFT","opacity":"0.3","rotation":"45","fontSize":"30"}
```

## Gotchas
- All Stirling watermark params are **strings** (`"0.3"`, `"45"`), not numbers.
- `filepath` is resolved on the **server** filesystem; use `file_base64` when the caller holds the file.
- The response `data` is base64-encoded PDF bytes; decode before writing to disk.
- Watermarking is destructive to the visual layer only — it does not encrypt; use
  document-security for protection.

## Related
- `stirlingpdf-document-operations` — every non-watermark Stirling action.
- `stirlingpdf-knowledge-graph` — the operation is auto-ingested as a `:PdfOperation`
  with `:appliedWatermark` → `:Watermark` and `:derivedFrom` provenance when an engine
  is reachable.
- `stirlingpdf-agent-docs` — full Stirling PDF reference documentation.
