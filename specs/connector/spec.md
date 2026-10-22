# CONN-STIRLINGPDF-AGENT — Read-only operations

Owner: stirlingpdf-agent. Cross-repo IDs: none.

## Purpose and user stories

A fleet operator must check the PDF server without a change to any document. The connector must expose one read-only operation for that check.

## Requirements and acceptance

- FR-001: The connector must expose `stirlingpdf_get_status`. The tool must call `GET /api/v1/info/status` in `stirlingpdf_agent/api/api_client_watermark.py`. The tool must carry the read-only annotation.
- SC-001: the tool is listed with the read-only annotation, calls the status route with the API key header, and maps a 401 response to an authentication error.

## Why a new spec

The `specs/` tree held only the template and the index.
No local spec owned this behavior, so this spec is the first capability spec.

## Scope and interfaces

The connector owns its operations and their MCP tool annotations.
The connector SDK owns tool registration, transport and the shared client contracts.
Code: ../../stirlingpdf_agent/api/api_client_watermark.py ../../tests/test_read_only_status.py

## Traceability

| Requirement | Design section | Test ID | Evidence |
|---|---|---|---|
| FR-001 | plan.md#architecture | T-001 | `tests/test_read_only_status.py` |

## Open questions

- None.
