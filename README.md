# Stirling PDF Agent
## CLI or API | MCP | Agent

![PyPI - Version](https://img.shields.io/pypi/v/stirlingpdf-agent)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/stirlingpdf-agent)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/stirlingpdf-agent)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/stirlingpdf-agent)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/stirlingpdf-agent)
![PyPI - License](https://img.shields.io/pypi/l/stirlingpdf-agent)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/stirlingpdf-agent)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/stirlingpdf-agent)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/stirlingpdf-agent)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/stirlingpdf-agent)
![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/stirlingpdf-agent)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/stirlingpdf-agent)

*Version: 2.0.0*

> **Documentation** — Installation, deployment, usage across the MCP, API, and CLI
> interfaces, and guidance for provisioning the Stirling PDF service are maintained in
> the [official documentation](https://knuckles-team.github.io/stirlingpdf-agent/).

---

## 📚 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start & Usage Examples](#quick-start--usage-examples)
- [MCP Server Mode](#mcp-server-mode)
  - [Available MCP Tools](#available-mcp-tools)
  - [MCP Configuration Examples](#mcp-configuration-examples)
- [Agent Mode](#agent-mode)
  - [Running the Agent CLI](#running-the-agent-cli)
  - [Docker Compose Orchestration](#docker-compose-orchestration)
- [Environment Variables Reference](#environment-variables-reference)
- [Security & Governance](#security--governance)
- [Developer & Contribute Guidelines](#contribute)
- [Documentation](#documentation)

---

## Overview

**Stirling PDF Agent** is a production-grade Agent and Model Context Protocol (MCP) server designed to interface directly with Stirling PDF via REST APIs. It provides seamless capability to manipulate, edit, and overlay PDFs (e.g. adding watermarks) programmatically or using large language models.

---

## Key Features

- **Consolidated Action-Routed MCP Tools:** Minimizes token overhead and eliminates tool bloat in LLM contexts by grouping methods into optimized, togglable tool modules.
- **Enterprise-Grade Security:** Comprehensive support for Eunomia policies, OIDC token delegation, and granular execution context tracking.
- **Integrated Graph Agent:** Built-in Pydantic AI agent supporting the Agent Control Protocol (ACP) and standard Web interfaces (AG-UI).
- **Native Telemetry & Tracing:** Out-of-the-box OpenTelemetry exports and native Langfuse tracing.

---

## Installation

Pick the extra that matches what you want to run:

| Extra | Installs | Use when |
|-------|----------|----------|
| `stirlingpdf-agent[mcp]` | Connector-focused MCP server (`agent-utilities[mcp]` — FastMCP/FastAPI + `epistemic-graph[full]`) | You only run the **MCP server** (smallest install / image) |
| `stirlingpdf-agent[agent]` | Agent runtime (`agent-utilities[agent-runtime,logfire]` — model orchestration + `epistemic-graph[full]`) | You run the **integrated agent** |
| `stirlingpdf-agent[all]` | Everything (`mcp` + `agent` + `logfire`) | Development / both surfaces |

```bash
# Connector-focused MCP server (includes the shared graph engine)
uv pip install "stirlingpdf-agent[mcp]"

# Agent runtime (adds model orchestration to the shared graph engine)
uv pip install "stirlingpdf-agent[agent]"

# Everything (development)
uv pip install "stirlingpdf-agent[all]"      # or: python -m pip install "stirlingpdf-agent[all]"
```

### Container images (`:mcp` vs `:agent`)

One multi-stage `docker/Dockerfile` builds two right-sized images, selected by `--target`:

| Image tag | Build target | Contents | Entrypoint |
|-----------|--------------|----------|------------|
| `knucklessg1/stirlingpdf-agent:mcp` | `--target mcp` | `stirlingpdf-agent[mcp]` — **connector-focused**, includes `epistemic-graph[full]`; no model-orchestration stack | `stirlingpdf-mcp` |
| `knucklessg1/stirlingpdf-agent:latest` | `--target agent` (default) | `stirlingpdf-agent[agent]` — **agent runtime**, model orchestration + `epistemic-graph[full]` | `stirlingpdf-agent` |

```bash
docker build --target mcp   -t knucklessg1/stirlingpdf-agent:mcp    docker/   # connector-focused MCP server
docker build --target agent -t knucklessg1/stirlingpdf-agent:latest docker/   # agent runtime
```

`docker/mcp.compose.yml` runs the connector-focused `:mcp` server; `docker/agent.compose.yml` runs the
agent (`:latest`) with a co-located `:mcp` sidecar. Both compose files require the deployed
image to be pinned by digest via `STIRLINGPDF_AGENT_MCP_IMAGE` / `STIRLINGPDF_AGENT_AGENT_IMAGE`
(e.g. `knucklessg1/stirlingpdf-agent@sha256:<digest>`) — least-privilege, read-only,
non-root (`10001:10001`) containers with no floating tag in production.

### Knowledge-graph database (`epistemic-graph`)

Both `[mcp]` and `[agent]` carry the **epistemic-graph** engine through the required
Agent Utilities core dependency (`epistemic-graph[full]`). The `[mcp]` extra keeps
the server connector-focused; `[agent]` additionally enables model orchestration. Local
deployments can use the bundled engine. For production or shared state, run
**epistemic-graph as a dedicated database service** and configure the runtime to use it.
Deployment recipes (single-node + Raft HA), connection configuration, and architecture
diagrams are documented in the
[epistemic-graph deployment guide](https://knuckles-team.github.io/epistemic-graph/deployment/).

---

## Quick Start & Usage Examples

Using the underlying Stirling PDF Client wrapper directly in Python:

```python
from stirlingpdf_agent.api_client import StirlingPdfApi

# Initialize the Stirling PDF client
client = StirlingPdfApi(
    base_url="http://localhost:8080",
    token="your-stirling-pdf-api-key",
)

# Example action: Add a watermark to an existing PDF
response = client.add_watermark(
    filepath="input.pdf",
    watermarkText="CONFIDENTIAL",
    percentOfPage=30,
    opacity=0.5,
    rotation=45
)

# Save output PDF bytes
with open("watermarked_output.pdf", "wb") as f:
    f.write(response.data)
```

---

## MCP Server Mode

This server utilizes dynamic Action-Routed tools to optimize token overhead and maximize IDE compatibility.

### Available MCP Tools

The table below is auto-generated from the MCP server — do not edit by hand.

<!-- MCP-TOOLS-TABLE:START -->

#### Condensed action-routed tools (default — `MCP_TOOL_MODE=condensed`)

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `pdf_action` | `PDFTOOL` | Execute any Stirling PDF API action dynamically. |

#### Verbose 1:1 API-mapped tools (`MCP_TOOL_MODE=verbose` or `both`)

<details>
<summary>1 per-operation tools — one per public API method (click to expand)</summary>

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `stirlingpdf_add_watermark` | `WATERMARK_CLIENTTOOL` | Add a watermark to a PDF file. |

</details>

_1 action-routed tool(s) (default) · 1 verbose 1:1 tool(s). Each is enabled unless its `<DOMAIN>TOOL` toggle is set false; `MCP_TOOL_MODE` selects the surface (`condensed` default · `verbose` 1:1 · `both`). Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->

---

### Dynamic Tool Selection & Visibility

This MCP server supports dynamic toolset selection and visibility filtering at runtime. This allows you to restrict the set of exposed tools in order to prevent blowing up the LLM's context window.

You can configure tool filtering via multiple input channels:

- **CLI Arguments:** Pass `--tools` or `--toolsets` (or their disabled counterparts `--disabled-tools` and `--disabled-toolsets`) during startup.
- **Environment Variables:** Define standard environment variables:
  - `MCP_ENABLED_TOOLS` / `MCP_DISABLED_TOOLS`
  - `MCP_ENABLED_TAGS` / `MCP_DISABLED_TAGS`
- **HTTP SSE Request Headers:** Pass custom headers during transport initialization:
  - `x-mcp-enabled-tools` / `x-mcp-disabled-tools`
  - `x-mcp-enabled-tags` / `x-mcp-disabled-tags`
- **HTTP SSE Request Query Parameters:** Append query parameters directly to your transport connection URL:
  - `?tools=tool1,tool2`
  - `?tags=tag1`

When query strings or parameters are supplied, an LLM-free **Knowledge Graph resolution layer** (using `DynamicToolOrchestrator`) matches query intents against known tool tags, names, or descriptions, with safe fallback and automated 24-hour background cache refreshing.

---

### MCP Configuration Examples

<!-- MCP-CONFIG-EXAMPLES:START -->

> **Install the connector-focused `[mcp]` extra.** Examples use `stirlingpdf-agent[mcp]` to add
> FastMCP / FastAPI through `agent-utilities[mcp]`; the required Agent Utilities core
> still carries `epistemic-graph[full]`. The `[agent-runtime]` extra additionally
> enables model orchestration.

#### stdio Transport (local IDEs — Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "stirlingpdf-agent[mcp]",
        "stirlingpdf-mcp"
      ],
      "env": {
        "MCP_TOOL_MODE": "condensed",
        "PDFTOOL": "True",
        "STIRLINGPDF_API_KEY": "",
        "STIRLINGPDF_TOKEN": "",
        "STIRLINGPDF_URL": ""
      }
    }
  }
}
```

Runtime references require an alias-aware launcher such as GraphOS. Other
launchers must omit those entries and inject the resolved values through their
own runtime secret boundary.

#### Streamable-HTTP Transport (networked / production)

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "stirlingpdf-agent[mcp]",
        "stirlingpdf-mcp",
        "--transport",
        "streamable-http",
        "--port",
        "8000"
      ],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "127.0.0.1",
        "PORT": "8000",
        "MCP_TOOL_MODE": "condensed",
        "PDFTOOL": "True",
        "STIRLINGPDF_API_KEY": "",
        "STIRLINGPDF_TOKEN": "",
        "STIRLINGPDF_URL": ""
      }
    }
  }
}
```

Alternatively, connect to a pre-deployed Streamable-HTTP instance by `url`:

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": {
      "url": "http://localhost:8000/stirlingpdf-mcp/mcp"
    }
  }
}
```

Deploying the Streamable-HTTP server via Docker (networked):

```bash
docker run -d \
  --name stirlingpdf-mcp-mcp \
  -p 127.0.0.1:8000:8000 \
  -e TRANSPORT=streamable-http \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e MCP_TOOL_MODE=condensed \
  -e PDFTOOL=True \
  -e STIRLINGPDF_API_KEY="" \
  -e STIRLINGPDF_TOKEN="" \
  -e STIRLINGPDF_URL="" \
  knucklessg1/stirlingpdf-agent@sha256:<digest>
```

Or run a reviewed container image as a least-privilege stdio child (no
listener or published port):

```bash
docker run -i --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --pids-limit=256 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \
  -e TRANSPORT=stdio \
  -e MCP_TOOL_MODE=condensed \
  -e PDFTOOL=True \
  knucklessg1/stirlingpdf-agent@sha256:<digest> stirlingpdf-mcp
```

For containerized network HTTP, supply an authenticated TLS ingress (or
direct server TLS), exact `MCP_ALLOWED_HOSTS`, and an exact trusted-proxy
CIDR policy through the operator-owned deployment profile. Never run an
unauthenticated non-loopback listener.

_Auto-generated from the code-read env surface (`MCP_TOOL_MODE` + package vars) — do not edit._
<!-- MCP-CONFIG-EXAMPLES:END -->

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`stirlingpdf-agent` can run as a local stdio process or container, or behind a remote
network boundary. The
[Deployment guide](https://knuckles-team.github.io/stirlingpdf-agent/deployment/) carries
the detailed transport contract for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run` as a reviewed, least-privilege stdio child with no
  listener or published port, or point at a local streamable-http container by `url`.
- **Remote URL** — connect through an operator-supplied authenticated HTTPS ingress
  (for example a server deployed behind Caddy at `http://stirlingpdf-mcp.arpa/mcp`)
  using the `"url"` key. Keep its URL, outbound identity references, trust profile,
  and exact `MCP_ALLOWED_HOSTS` in `AgentConfig`.
<!-- END GENERATED: additional-deployment-options -->

## Agent Mode

This repository features a fully integrated Pydantic AI Graph Agent. It communicates over the **Agent Control Protocol (ACP)** and interacts seamlessly with the **Agent Web UI (AG-UI)** and Terminal interface.

### Running the Agent CLI
To start the interactive command-line agent:

```bash
# Set credentials
export STIRLINGPDF_URL="<configured-endpoint>"
export STIRLINGPDF_API_KEY="your-api-key"

# Run the agent server
stirlingpdf-agent --provider openai --model-id gpt-4o
```

---

### Docker Compose Orchestration

```yaml
version: '3.8'

services:
  stirlingpdf-agent-mcp:
    image: example/stirlingpdf-agent@sha256:<digest>
    container_name: stirlingpdf-agent-mcp
    hostname: stirlingpdf-agent-mcp
    restart: always
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports:
      - "8000:8000"

  stirlingpdf-agent-agent:
    image: example/stirlingpdf-agent@sha256:<digest>
    container_name: stirlingpdf-agent-agent
    hostname: stirlingpdf-agent-agent
    restart: always
    depends_on:
      - stirlingpdf-agent-mcp
    env_file:
      - .env
    command: [ "stirlingpdf-agent" ]
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=9004
      - MCP_URL=http://stirlingpdf-agent-mcp:8000/mcp
      - PROVIDER=${PROVIDER:-openai}
      - MODEL_ID=${MODEL_ID:-gpt-4o}
      - ENABLE_WEB_UI=True
      - ENABLE_OTEL=True
    ports:
      - "9004:9004"
```

---

## Environment Variables

<!-- ENV-VARS-TABLE:START -->

#### Package environment variables

| Variable | Example | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` |  |
| `PORT` | `8000` |  |
| `TRANSPORT` | `stdio` | options: stdio, streamable-http, sse |
| `ENABLE_OTEL` | `True` |  |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:8080/api/public/otel` |  |
| `OTEL_EXPORTER_OTLP_PUBLIC_KEY` | `pk-...` |  |
| `OTEL_EXPORTER_OTLP_SECRET_KEY` | `sk-...` |  |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` |  |
| `EUNOMIA_TYPE` | `none` | options: none, embedded, remote |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` |  |
| `EUNOMIA_REMOTE_URL` | `http://eunomia-server:8000` |  |
| `PDFTOOL` | `True` |  |
| `STIRLINGPDF_URL` | Required |  |
| `STIRLINGPDF_API_KEY` | — |  |
| `STIRLINGPDF_TOKEN` | — | alternate to STIRLINGPDF_API_KEY (bearer token) |
| `TLS_PROFILE` | — | Named `AgentConfig` transport-security profile; verification is mandatory. |
| `TLS_PROFILES_REF` | — | Runtime secret reference for the TLS profile catalog. |

#### Inherited agent-utilities variables (apply to every connector)

| Variable | Example | Description |
|----------|---------|-------------|
| `MCP_TOOL_MODE` | `condensed` | Tool surface: `condensed` | `verbose` | `both` |
| `MCP_ENABLED_TOOLS` | — | Comma-separated tool allow-list |
| `MCP_DISABLED_TOOLS` | — | Comma-separated tool deny-list |
| `MCP_ENABLED_TAGS` | — | Comma-separated tag allow-list |
| `MCP_DISABLED_TAGS` | — | Comma-separated tag deny-list |
| `MCP_CLIENT_AUTH` | — | Outbound MCP auth (`oidc-client-credentials` for fleet calls) |
| `OIDC_CLIENT_ID` | — | OIDC client id (service-account auth) |
| `OIDC_CLIENT_SECRET` | — | OIDC client secret (service-account auth) |
| `DEBUG` | `False` | Verbose logging |
| `PYTHONUNBUFFERED` | `1` | Unbuffered stdout (recommended in containers) |
| `MCP_URL` | `http://localhost:8000/mcp` | URL of the MCP server the agent connects to |
| `PROVIDER` | `openai` | LLM provider for the agent |
| `MODEL_ID` | `gpt-4o` | Model id for the agent |
| `ENABLE_WEB_UI` | `True` | Serve the AG-UI web interface |

_17 package + 14 inherited variable(s). Auto-generated from `.env.example` + the shared agent-utilities set — do not edit._
<!-- ENV-VARS-TABLE:END -->
 Reference

Stirling PDF Agent utilizes both package-specific environment configurations and standard security settings inherited from the `agent-utilities` system core.

### Stirling PDF Agent Configs
- **`PDFTOOL`** (bool, default: `True`): Toggles the dynamic PDF action tool registration.
- **`STIRLINGPDF_URL`** (str, required): The base endpoint of the external Stirling PDF API service.
- **`STIRLINGPDF_API_KEY`** (str): API connection token/secret used to authenticate REST requests.
- **`TLS_PROFILE`** (str): Selects a named `AgentConfig` transport-security profile. Certificate and hostname verification are mandatory.
- **`TLS_PROFILES_REF`** (secret reference): Resolves the runtime-only TLS profile catalog.

### Inherited agent-utilities Configs
- **`TRANSPORT`** (str, default: `stdio`): Server transport type. Options: `stdio`, `sse`, `streamable-http`.
- **`HOST`** (str, default: `0.0.0.0`): Network host interface to bind the HTTP server.
- **`PORT`** (int, default: `8000`): Port to listen on.
- **`ENABLE_OTEL`** (bool, default: `False`): Enables OpenTelemetry tracing integration.
- **`ALLOWED_CLIENT_REDIRECT_URIS`** (str): Comma-separated list of approved redirect URLs for authentication loops.
- **`AUTH_TYPE`** (str): Server authentication mode configurations.
- **`EUNOMIA_TYPE`** (str, default: `none`): Policy configuration enforcement. Options: `none`, `embedded`, `remote`.
- **`EUNOMIA_POLICY_FILE`** (str): Path to local JSON configuration policy maps.
- **`EUNOMIA_REMOTE_URL`** (str): Target URL for remote auth policy coordination.
- **`OAUTH_BASE_URL`** (str): Base OAuth service endpoint.
- **`OAUTH_UPSTREAM_AUTH_ENDPOINT`** (str): Upstream OAuth service authorization endpoint.
- **`OAUTH_UPSTREAM_CLIENT_ID`** (str): Client application identity ID.
- **`OAUTH_UPSTREAM_CLIENT_SECRET`** (str): Client secret credential token.
- **`OAUTH_UPSTREAM_TOKEN_ENDPOINT`** (str): Remote OAuth token resolution endpoint.

---

## Security & Governance

Built directly upon the enterprise-ready [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities) core, standard security parameters are fully supported:

- **Eunomia Policies:** Fine-grained, policy-driven tool authorization. Supports `none`, local `embedded` (`mcp_policies.json`), or centralized `remote` modes.
- **OIDC Token Delegation:** Compliant with RFC 8693 token exchange for flowing authenticating user credentials from Web UI / ACP → Agent → MCP.
- **Scoped Credentials:** Execution context runs restricted to the specific caller identity.

| Feature Guard | Functionality | Status |
|---------------|---------------|--------|
| **Tool Guard** | Sensitivity inspection with human-in-the-loop validation | Enabled by default |
| **Prompt Injection Defense** | Input scanning, repetition monitoring, and recursive loop blocks | Enabled by default |
| **Context Safety Guard** | Stuck-loop detectors and contextual overflow preemptive alerts | Enabled by default |

---

## Contribute

Contributions are welcome! Please ensure code quality by executing local checks before submitting pull requests:
- Format code using `ruff format .`
- Lint code using `ruff check .`
- Validate type-safety with `mypy .`
- Execute test suites using `pytest`

---

## Documentation

The complete documentation is published as the
[official documentation site](https://knuckles-team.github.io/stirlingpdf-agent/) and is
the recommended reference for installation, deployment, and day-to-day operation.

| Page | Contents |
|---|---|
| [Installation](https://knuckles-team.github.io/stirlingpdf-agent/installation/) | pip, source, extras, prebuilt Docker image |
| [Deployment](https://knuckles-team.github.io/stirlingpdf-agent/deployment/) | run the MCP and agent servers, Compose, Caddy + Technitium, env config |
| [Usage](https://knuckles-team.github.io/stirlingpdf-agent/usage/) | the MCP tools, the `StirlingPdfApi` client, the CLI |
| [Backing Platform](https://knuckles-team.github.io/stirlingpdf-agent/platform/) | deploy Stirling PDF with Docker |
| [Overview](https://knuckles-team.github.io/stirlingpdf-agent/overview/) | the agent-package pattern and tool routing |
| [Concepts](https://knuckles-team.github.io/stirlingpdf-agent/concepts/) | concept registry (`CONCEPT:STIRLINGPDF-*`) |

`AGENTS.md` is the canonical contributor/agent guidance.


<!-- BEGIN agent-os-genesis-deploy (generated; do not edit between markers) -->

## Deploy with `agent-os-genesis`

This package can be provisioned for you — skill-guided — by the **`agent-os-genesis`**
universal skill (its *single-package deploy mode*): it picks your install method, seeds
secrets to OpenBao/Vault (or `.env`), trusts your enterprise CA, registers the MCP
server, and verifies it — the same machinery that stands up the whole Agent OS, narrowed
to just this package. Ask your agent to **"deploy `stirlingpdf-agent` with agent-os-genesis"**.

| Install mode | Command |
|------|---------|
| Bare-metal, prod (PyPI) | `uvx stirlingpdf-mcp` · or `uv tool install stirlingpdf-agent` |
| Bare-metal, dev (editable) | `uv pip install -e ".[all]"` · or `pip install -e ".[all]"` |
| Container, prod | deploy `knucklessg1/stirlingpdf-agent@sha256:<digest>` via docker-compose / swarm / podman / podman-compose / kubernetes |
| Container, dev (editable) | deploy `docker/compose.dev.yml` (source-mounted at `/src`; edits live on restart) |

Secrets are read-existing + seeded via `vault_sync` — you are only prompted for what's missing.

<!-- END agent-os-genesis-deploy -->

<!-- BEGIN agent-utilities-deployment (generated; do not edit between markers) -->

## Deploy with `agent-utilities-deployment`

Provision this package with the consolidated **`agent-utilities-deployment`**
workflow. It selects an installed-package, editable-source, or immutable-container
path; records only runtime secret and TLS-profile references in `AgentConfig`; and
runs doctor, registration, policy, observability, and rollback gates. Ask your agent
to **"deploy `stirlingpdf-agent` with agent-utilities-deployment"**.

| Install mode | Command |
|------|---------|
| Installed package | `uv tool install "stirlingpdf-agent[mcp]"`, then run `stirlingpdf-mcp` |
| Editable source | `uv pip install -e ".[agent]"`, then run `stirlingpdf-mcp` |
| Immutable container | deploy `knucklessg1/stirlingpdf-agent@sha256:<digest>` through the operator-selected orchestrator |

The repository embeds no deployment profile, credential value, certificate path, or
environment-specific endpoint. Supply those at runtime through `AgentConfig` and the
configured secret provider.

<!-- END agent-utilities-deployment -->

<!-- GOVERNED-CAPABILITY:START -->
## Governed capability contract

This package ships a compact canonical skill surface with specialist procedures
kept as referenced workflows. The current MCP tools, skill metadata,
`connector_manifest.yml`, ontology, mappings, shapes, fixtures, migrations,
tool-schema fingerprints, and certification metadata form one versioned
capability contract. Validate them together; do not rely on stale tool names or
historical per-task skill wrappers.

Runtime endpoints, credentials, certificate trust, tenant identity, retention,
and observability policy are deployment inputs and are never packaged values.
See [Configuration, trust, and privacy](docs/configuration.md) before enabling a
network transport, connector ingestion, GraphOS delegation, or trace export.
<!-- GOVERNED-CAPABILITY:END -->
