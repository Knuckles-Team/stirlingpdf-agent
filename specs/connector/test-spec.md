# CONN-STIRLINGPDF-AGENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |
|---|---|---|---|---|---|
| T-001 | FR-001 | Unit | Mocked HTTP | the tool is listed with the read-only annotation, calls the status route with the API key header, and maps a 401 response to an authentication error. | `tests/test_read_only_status.py` |

## Negative and boundary cases

The tests cover the error path that each row names.

## Quality and release proof

Run `pytest -q`. The served proof is the fleet acceptance check through the gateway.
