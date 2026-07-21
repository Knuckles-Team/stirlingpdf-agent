# Stirlingpdf Watermarking

Stamp text (or image) watermarks onto a PDF via the stirlingpdf-agent MCP server's dispatch tool. Use when the agent must brand, mark DRAFT/CONFIDENTIAL, or overlay repeating text on a PDF using a self-hosted Stirling PDF instance. Do NOT use for password protection / redaction (that is document security), for merge/split/convert/OCR (use stirlingpdf-document-operations), or for pushing results into the knowledge graph (use stirlingpdf-knowledge-graph).

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
  `stirlingpdf-document-operations` (`add_password`, `sanitize`, `add_stamp`).
- Merge / split / rotate / convert / compress / OCR → `stirlingpdf-document-operations`.
- Persisting the result into the KG → `stirlingpdf-knowledge-graph`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`stirlingpdf-agent`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `STIRLINGPDF_URL` | ✅ | Base URL of the Stirling PDF instance (default `[configured-endpoint]`) |
| `STIRLINGPDF_API_KEY` | optional | Sent as `X-API-KEY` |
| `TLS_PROFILE` / `TLS_PROFILES_REF` | optional | Named runtime trust profile and secret-backed catalog; verification is mandatory |

The input PDF must be a **path the MCP server process can read** (`filepath`).

## Tools & actions
Prefer the condensed dispatch tool; it takes an `action` name + a `params_json`
**JSON string** whose keys are forwarded to the client method.

| Tool | Action | Purpose |
|------|--------|---------|
| `pdf_action` | `add_watermark` | Stamp a watermark onto `filepath` |
| `pdf_action` | `list_actions` | Discover every available action on this instance |

### Key parameters (`add_watermark`)
- `filepath` — **required**, path to the input PDF on the server.
- `watermarkType` — `text` (or `image`).
- `watermarkText` — the text to render.
- `opacity` (`0.0`–`1.0`), `rotation` (degrees), `fontSize`, `alphabet` (`roman`),
  `widthSpacer`, `heightSpacer` — all optional strings with sensible defaults.

## Recipes (`params_json`)
Stamp a semi-transparent DRAFT watermark:
```json
{"filepath":"/data/report.pdf","watermarkType":"text","watermarkText":"DRAFT","opacity":"0.3","rotation":"45","fontSize":"30"}
```
Discover what this instance supports first:
```json
{}
```
(call `pdf_action` with `action="list_actions"` and the empty object above.)

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- All Stirling watermark params are **strings** (`"0.3"`, `"45"`), not numbers.
- `filepath` is resolved on the **server** filesystem, not the caller's.
- The response `data` is base64-encoded PDF bytes; decode before writing to disk.
- Watermarking is destructive to the visual layer only — it does not encrypt; use
  document-security for protection.

## Related
- `stirlingpdf-document-operations` — every non-watermark Stirling action.
- `stirlingpdf-knowledge-graph` — the operation is auto-ingested as a `:PdfOperation`
  with `:appliedWatermark` → `:Watermark` and `:derivedFrom` provenance when an engine
  is reachable.
- `stirlingpdf-agent-docs` — full Stirling PDF reference documentation.
