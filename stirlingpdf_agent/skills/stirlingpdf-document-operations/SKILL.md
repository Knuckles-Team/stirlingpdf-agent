---
name: stirlingpdf-document-operations
skill_type: skill
description: >-
  Transform and secure PDFs through the stirlingpdf-agent MCP server's typed
  tools - rotate, compress, split, merge, add or remove a password, and sanitize.
  Use when the agent must change a PDF on a self-hosted Stirling instance and the
  file travels with the call as base64 or as a workspace path. Do NOT use for the
  watermark flow (use stirlingpdf-watermarking), for server health
  (stirlingpdf-agent-docs) or for ingesting results into the knowledge graph (use
  stirlingpdf-knowledge-graph).
license: MIT
tags: [stirlingpdf, pdf, compress, merge, security, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Stirling PDF Document Operations

One typed tool per Stirling PDF operation on the **`stirlingpdf-agent`** MCP server.

## File bytes
Each tool takes the PDF as exactly one of:
- `file_base64` - the PDF bytes, base64 encoded, with an optional `filename`. No shared filesystem is needed.
- `filepath` - a path the server process can read.

`stirlingpdf_merge_pdfs` takes `files_base64`, a list of at least two base64 PDFs.
The result's `data` field is the output file, base64 encoded (a ZIP for `stirlingpdf_split_pdf`).
Inputs and outputs are capped at `STIRLINGPDF_MAX_FILE_BYTES` (default 25 MiB). Larger documents
belong in an object store and are handled by the store connector, not passed through a tool call.

## Tools
| Tool | Purpose |
|------|---------|
| `stirlingpdf_rotate_pdf` | Rotate every page by a multiple of 90 degrees (`angle`). |
| `stirlingpdf_compress_pdf` | Compress at `optimize_level` 1 to 9. |
| `stirlingpdf_split_pdf` | Split after the listed pages (`page_numbers`, for example `1,3,7-9`); returns a ZIP. |
| `stirlingpdf_merge_pdfs` | Merge base64 PDFs in order or by `sort_type`. |
| `stirlingpdf_add_password` | Encrypt with `password` and an optional `owner_password`. |
| `stirlingpdf_remove_password` | Remove the password from an encrypted PDF. |
| `stirlingpdf_sanitize_pdf` | Strip JavaScript, embedded files, metadata or links. |

## Recipes
Rotate a PDF a quarter turn: `stirlingpdf_rotate_pdf` with `angle=90` and `file_base64=<bytes>`.

Compress a workspace file: `stirlingpdf_compress_pdf` with `filepath=/data/report.pdf`, `optimize_level=6`.

## Gotchas
- Pass exactly one of `file_base64` and `filepath`; both or neither is refused.
- Operations need the API key when the instance enforces security (`STIRLINGPDF_API_KEY`).
- Encryption and sanitizing change the document; keep the original until the output is verified.

## Related
- `stirlingpdf-watermarking` - the watermark operation.
- `stirlingpdf-knowledge-graph` - record operations in the graph.
