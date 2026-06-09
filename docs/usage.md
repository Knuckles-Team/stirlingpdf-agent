# Usage — MCP / API / CLI

`stirlingpdf-agent` exposes the same capability several ways: as an **MCP tool** an
agent calls, as a **Python API** (`StirlingPdfApi`) you import, and as **CLI** console
scripts. The agent-package pattern is described in [Architecture](overview.md).

## As an MCP server

Once [deployed](deployment.md), the server registers an action-routed PDF tool. It is
enabled by `PDFTOOL=True` (the default) and operates against the connected Stirling
PDF service.

| Tool | Purpose |
|---|---|
| `pdf_action` | Dispatch any supported Stirling PDF operation by name (for example, `add_watermark`) with a JSON parameter payload |

The `pdf_action` tool takes an `action` (the method to invoke on `StirlingPdfApi`) and
`params` (a JSON string of arguments). Example agent prompts that map onto it:

- *"Add a 'DRAFT' watermark to `report.pdf`"* → `pdf_action` with
  `action="add_watermark"` and `params={"filepath": "report.pdf", "watermarkText": "DRAFT"}`
- *"Stamp this contract as 'CONFIDENTIAL'"* → `pdf_action` with `action="add_watermark"`

## As a Python API

`StirlingPdfApi` is a `requests`-based REST client over the Stirling PDF `/api/v1`
surface. Construct it directly, or use `get_client()` to build one from the
environment.

```python
from stirlingpdf_agent.api_client import StirlingPdfApi

api = StirlingPdfApi(
    base_url="http://your-stirlingpdf:8080",
    token="your_token",
    verify=True,
)

# Operate on a PDF (returns a Response carrying the resulting bytes)
result = api.add_watermark("report.pdf", watermarkText="DRAFT")
with open("report-watermarked.pdf", "wb") as f:
    f.write(result.data)
```

Build a client straight from the environment:

```python
from stirlingpdf_agent.auth import get_client

api = get_client()        # reads STIRLINGPDF_* from the environment / .env
result = api.add_watermark("report.pdf", watermarkText="DRAFT")
```

`get_client()` reads `STIRLINGPDF_URL`, `STIRLINGPDF_API_KEY` (or `STIRLINGPDF_TOKEN`),
and `STIRLINGPDF_AGENT_VERIFY` from the environment, and returns a singleton client.

## As a CLI

Two console scripts are installed:

```bash
# The MCP server (see Deployment for transports)
stirlingpdf-mcp --transport streamable-http --host 0.0.0.0 --port 8000

# The A2A agent server (drives the MCP tools via a Pydantic-AI agent)
stirlingpdf-agent --provider openai --model-id gpt-4o --api-key sk-...
```

Both read the same `STIRLINGPDF_*` connection variables. The agent server additionally
honours `MCP_URL` to reach a running MCP server, plus `PROVIDER` / `MODEL_ID` for the
model backend. See [Deployment](deployment.md) for the full environment table and the
combined Compose stack.
