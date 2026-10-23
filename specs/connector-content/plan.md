# CONN-STIRLINGPDF-AGENT-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `stirlingpdf-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `stirlingpdf_agent` from it.
