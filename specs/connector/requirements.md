# CONN-STIRLINGPDF-AGENT — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-STIRLINGPDF-AGENT-R001` | **Read-only status operation.** The connector must expose `stirlingpdf_get_status`. The tool must call `GET /api/v1/info/status` in `stirlingpdf_agent/api/api_client_watermark.py`. The tool must carry the read-only annotation. | `tests/test_read_only_status.py` must show: the tool is listed with the read-only annotation, calls the status route with the API key header, maps a 401 response to an authentication error, and succeeds with no API key configured. |
| `CONN-STIRLINGPDF-AGENT-R002` | **Fleet name.** `pyproject.toml` declares `stirlingpdf-mcp` as the single `agent_connector_sdk.connector` entry point. The content pack, the manifest `connector`, the fingerprints and the ingest binding all carry `stirlingpdf-mcp`. Proving test: `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name`. | Every connector name in the package is `stirlingpdf-mcp`. |
