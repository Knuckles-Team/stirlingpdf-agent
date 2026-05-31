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

*Version: 0.22.0*

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
- [Documentation Reference](#documentation-reference)

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

Install the Python package locally:

```bash
# Using uv (highly recommended for speed and isolation)
uv pip install stirlingpdf-agent[all]

# Using standard pip
python -m pip install stirlingpdf-agent[all]
```

---

## Quick Start & Usage Examples

Using the underlying Stirling PDF Client wrapper directly in Python:

```python
from stirlingpdf_agent.api_client import StirlingPdfApi

# Initialize the Stirling PDF client
client = StirlingPdfApi(
    base_url="http://localhost:8080",
    token="your-stirling-pdf-api-key",
    verify=True
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
| Tool Module | Toggle Env Var | Enabled by Default | Description & Nested Methods |
|-------------|----------------|--------------------|------------------------------|
| **Pdf** | `PDF_TOOL` | `True` | Execute any Stirling PDF API action dynamically. |

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

#### 1. stdio Transport (Recommended for local IDEs e.g., Cursor, Claude Desktop)
Configure your IDE's `mcp.json` to launch the MCP server via `uvx`:

```json
{
  "mcpServers": {
    "stirlingpdf-agent": {
      "command": "uvx",
      "args": [
        "--from",
        "stirlingpdf-agent",
        "stirlingpdf-mcp"
      ],
      "env": {
        "PDFTOOL": "True",
        "STIRLINGPDF_URL": "http://localhost:8080",
        "STIRLINGPDF_API_KEY": "your_api_key_here",
        "STIRLINGPDF_AGENT_VERIFY": "True"
      }
    }
  }
}
```

#### 2. Streamable-HTTP Transport (Recommended for production deployments)
Configure your client's `mcp.json` to launch the Streamable-HTTP server via `uvx` with explicit host and port definition:

```json
{
  "mcpServers": {
    "stirlingpdf-agent": {
      "command": "uvx",
      "args": [
        "--from",
        "stirlingpdf-agent",
        "stirlingpdf-mcp"
      ],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "PDFTOOL": "True",
        "STIRLINGPDF_URL": "http://localhost:8080",
        "STIRLINGPDF_API_KEY": "your_api_key_here",
        "STIRLINGPDF_AGENT_VERIFY": "True"
      }
    }
  }
}
```

Deploying the Streamable-HTTP server via Docker:

```bash
docker run -d \
  --name stirlingpdf-agent-mcp \
  -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e PORT=8000 \
  -e STIRLINGPDF_URL="http://your-service:8080" \
  -e STIRLINGPDF_API_KEY="your_api_key_here" \
  knucklessg1/stirlingpdf-agent:latest
```

---

## Agent Mode

This repository features a fully integrated Pydantic AI Graph Agent. It communicates over the **Agent Control Protocol (ACP)** and interacts seamlessly with the **Agent Web UI (AG-UI)** and Terminal interface.

### Running the Agent CLI
To start the interactive command-line agent:

```bash
# Set credentials
export STIRLINGPDF_URL="http://localhost:8080"
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
    image: knucklessg1/stirlingpdf-agent:latest
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
    image: knucklessg1/stirlingpdf-agent:latest
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

## Environment Variables Reference

Stirling PDF Agent utilizes both package-specific environment configurations and standard security settings inherited from the `agent-utilities` system core.

### Stirling PDF Agent Configs
- **`PDFTOOL`** (bool, default: `True`): Toggles the dynamic PDF action tool registration.
- **`STIRLINGPDF_URL`** (str, default: `http://localhost:8080`): The base endpoint of the external Stirling PDF API service.
- **`STIRLINGPDF_API_KEY`** (str): API connection token/secret used to authenticate REST requests.
- **`STIRLINGPDF_AGENT_VERIFY`** (bool, default: `True`): Toggles SSL certificate verification during REST requests.

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

## Documentation Reference

Extensive materials are available in the repository for developer guidance:
- Standard MCP Server Details: [docs/mcp.md](docs/mcp.md)
- Complete Client & SDK details: [docs/index.md](docs/index.md)
- Agent Graph Orchestration: [docs/agent.md](docs/agent.md)
