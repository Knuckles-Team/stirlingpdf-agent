# stirlingpdf-agent

Stirling PDF **MCP Server + A2A Agent** for the agent-utilities ecosystem — a typed,
deterministic toolkit for performing PDF operations through a Stirling PDF service.

!!! info "Official documentation"
    This site is the canonical reference for `stirlingpdf-agent`, maintained alongside
    every release.

[![PyPI](https://img.shields.io/pypi/v/stirlingpdf-agent)](https://pypi.org/project/stirlingpdf-agent/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/stirlingpdf-agent)](https://github.com/Knuckles-Team/stirlingpdf-agent/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/stirlingpdf-agent)

## Overview

`stirlingpdf-agent` wraps the [Stirling PDF](https://www.stirlingpdf.com/) REST API
with typed MCP tools and an optional Pydantic-AI agent server. It provides:

- **`StirlingPdfApi`** — a `requests`-based REST client over the Stirling PDF
  `/api/v1` surface, configured from the environment via `get_client()`.
- **An action-routed MCP tool** — a single `pdf_action` dispatcher that invokes any
  supported operation (for example, `add_watermark`) on the connected Stirling PDF
  service.
- **An A2A agent server** — a Pydantic-AI agent (console script `stirlingpdf-agent`)
  that drives the MCP tools for multi-step workflows.

The connector remains inactive when credentials are absent, degrading safely until a
Stirling PDF service is configured.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP and agent servers, Docker Compose, Caddy + Technitium.
- :material-console: **[Usage](usage.md)** — the MCP tool surface, the `StirlingPdfApi` client, and the CLI.
- :material-database-cog: **[Backing Platform](platform.md)** — deploy Stirling PDF with Docker.
- :material-sitemap: **[Architecture](overview.md)** — the agent-package pattern and tool routing.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:STIRLINGPDF-*` registry.

</div>

## Quick start

```bash
pip install stirlingpdf-agent
stirlingpdf-mcp                       # stdio MCP server (default transport)
```

Connect it to a Stirling PDF service:

```bash
export STIRLINGPDF_URL=http://your-stirlingpdf:8080
export STIRLINGPDF_API_KEY=your_token
stirlingpdf-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (PyPI extras, Docker image, all transports, the agent server, reverse
proxy, DNS).
