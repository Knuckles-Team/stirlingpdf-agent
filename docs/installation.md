# Installation

`stirlingpdf-agent` is a standard Python package and a prebuilt container image. Pick
the path that matches how you want to run it.

## Requirements

- **Python 3.11 – 3.14**.
- A reachable **Stirling PDF** service — see [Backing Platform](platform.md) to deploy
  one locally.

## From PyPI (recommended)

```bash
pip install stirlingpdf-agent
```

The base install includes the FastMCP MCP-server runtime (`agent-utilities[mcp]`), so
the `stirlingpdf-mcp` console script is ready immediately.

### Optional extras

Install an extra for additional capabilities:

| Extra | Install | Pulls in |
|---|---|---|
| `agent` | `pip install "stirlingpdf-agent[agent]"` | Pydantic-AI agent server + Logfire tracing (`agent-utilities[agent-runtime,logfire]`) |
| `all` | `pip install "stirlingpdf-agent[all]"` | The MCP runtime, the agent server, and Logfire tracing |
| `test` | `pip install "stirlingpdf-agent[test]"` | `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist` |

```bash
# Typical: run both the MCP server and the A2A agent
pip install "stirlingpdf-agent[all]"
```

## From source

```bash
git clone https://github.com/Knuckles-Team/stirlingpdf-agent.git
cd stirlingpdf-agent
pip install -e ".[all]"          # editable install with every extra
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[all]"
uv run stirlingpdf-mcp
```

## Prebuilt Docker image

A multi-stage runtime image is published on every release (entrypoint
`stirlingpdf-mcp`):

```bash
docker pull example/stirlingpdf-agent@sha256:<digest>

docker run --rm -i \
  -e STIRLINGPDF_URL=<configured-endpoint> \
  -e STIRLINGPDF_API_KEY=your_token \
  example/stirlingpdf-agent@sha256:<digest>        # stdio transport (default)
```

For an HTTP server with a published port and the agent server, see
[Deployment](deployment.md).

## Verify the install

```bash
stirlingpdf-mcp --help
python -c "import stirlingpdf_agent; print('stirlingpdf-agent import OK')"
```

## Next steps

- **[Deployment](deployment.md)** — run it as a long-lived MCP and agent server behind Caddy + DNS.
- **[Usage](usage.md)** — call the tools, the API, and the CLI.
- **[Configuration](deployment.md#configuration-environment)** — every environment variable.
