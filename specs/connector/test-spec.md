# CONN-STIRLINGPDF-AGENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |
|---|---|---|---|---|---|
| T-001 | FR-001 | Unit | Mocked HTTP | the tool is listed with the read-only annotation, calls the status route with the API key header, maps a 401 response to an authentication error, and succeeds with no API key configured. | `tests/test_read_only_status.py` |

## Negative and boundary cases

The tests cover the error path that each row names.

## Quality and release proof

Run `pytest -q`. The served proof is the fleet acceptance check through the gateway.
| T-002 | `CONN-STIRLINGPDF-AGENT-R002` | `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name` | Every connector name in the package is `stirlingpdf-mcp`. |
