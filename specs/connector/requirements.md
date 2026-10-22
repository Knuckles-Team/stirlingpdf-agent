# CONN-STIRLINGPDF-AGENT — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-STIRLINGPDF-AGENT-R001` | **Read-only status operation.** The connector must expose `stirlingpdf_get_status`. The tool must call `GET /api/v1/info/status` in `stirlingpdf_agent/api/api_client_watermark.py`. The tool must carry the read-only annotation. | `tests/test_read_only_status.py` must show: the tool is listed with the read-only annotation, calls the status route with the API key header, maps a 401 response to an authentication error, and succeeds with no API key configured. |
