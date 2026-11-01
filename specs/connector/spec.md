# CONN-STIRLINGPDF-AGENT — Read-only operations

Owner: stirlingpdf-agent. Cross-repo IDs: none.

## Purpose and user stories

A fleet operator must check the PDF server without a change to any document. The connector must expose one read-only operation for that check.

## Why a new spec

The `specs/` tree held only the template and the index.
No local spec owned this behavior, so this spec is the first capability spec.

## Scope and interfaces

The connector owns its operations and their MCP tool annotations.
The connector SDK owns tool registration, transport and the shared client contracts.
Code: ../../stirlingpdf_agent/api/api_client_watermark.py ../../tests/test_read_only_status.py

## Open questions

- None.

## Delivery mapping

Component: stirlingpdf-agent connector

Code: ../../stirlingpdf_agent/__init__.py

## User Scenarios & Testing

### User Story 1 - Read-only status operation (Priority: P1)

The fleet operator and the engine rely on this behaviour of `stirlingpdf-agent`: The connector must expose `stirlingpdf_get_status`. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `stirlingpdf-agent` connector built from the default branch, **When** `tests/test_read_only_status.py::test_status_tool_is_listed_read_only` runs, **Then** `tests/test_read_only_status.py` must show: the tool is listed with the read-only annotation, calls the status route with the API key header, maps a 401 response to an authentication error, and succeeds with no API key configured.

### User Story 2 - Fleet name (Priority: P1)

The fleet operator and the engine rely on this behaviour of `stirlingpdf-agent`: `pyproject.toml` declares `stirlingpdf-mcp` as the single `scion_sdk.connector` entry point. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `stirlingpdf-agent` connector built from the default branch, **When** `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name` runs, **Then** every connector name in the package is `stirlingpdf-mcp`.

### Edge Cases

- The vendor service is unreachable or rejects the credential: the connector returns the SDK typed error and never a partial result.
- An argument outside the documented inputs is refused with the SDK typed refusal and causes no effect on the vendor service.

## Requirements

- **FR-001**: Read-only status operation. Rows: `CONN-STIRLINGPDF-AGENT-R001`.
- **FR-002**: Fleet name. Rows: `CONN-STIRLINGPDF-AGENT-R002`.

## Success Criteria

- **SC-001**: `tests/test_read_only_status.py` must show: the tool is listed with the read-only annotation, calls the status route with the API key header, maps a 401 response to an authentication error, and succeeds with no API key configured. Rows: `CONN-STIRLINGPDF-AGENT-R001`.
- **SC-002**: Every connector name in the package is `stirlingpdf-mcp`. Rows: `CONN-STIRLINGPDF-AGENT-R002`.

## Assumptions

- The `stirlingpdf-agent` package keeps the entry point and module layout named in the rows.
- The shared SDK supplies the transport, authentication, retry and certification helpers the rows reuse.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-STIRLINGPDF-AGENT-R001` | plan.md Production caller chain | T-001 | tests/test_read_only_status.py::test_status_tool_is_listed_read_only |
| FR-002 | `CONN-STIRLINGPDF-AGENT-R002` | plan.md Production caller chain | T-002 | tests/test_fleet_name.py::test_connector_name_is_the_fleet_name |
