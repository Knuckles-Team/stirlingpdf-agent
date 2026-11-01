# CONN-STIRLINGPDF-AGENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-STIRLINGPDF-AGENT-R001` | `tests/test_read_only_status.py::test_status_tool_is_listed_read_only` | `tests/test_read_only_status.py` must show: the tool is listed with the read-only annotation, calls the status route with the API key header, maps a 401 response to an authentication error, and succeeds with no API key configured. |
| T-002 | `CONN-STIRLINGPDF-AGENT-R002` | `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name` | Every connector name in the package is `stirlingpdf-mcp`. |

## Negative and boundary cases

Each proving test above includes the refusal or error case that its row names. A vendor outage or an unauthorised call must return the SDK typed error.

## Quality and release proof

Run `uv run pytest tests` and `pre-commit run --all-files` from the repository root. A planned test is added by the code change that lands the row.
