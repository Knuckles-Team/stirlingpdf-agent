# Stirling PDF Agent - A2A | AG-UI | MCP

![PyPI - Version](https://img.shields.io/pypi/v/stirlingpdf-agent)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/stirlingpdf-agent)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/stirlingpdf-agent)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/stirlingpdf-agent)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/stirlingpdf-agent)
![PyPI - License](https://img.shields.io/pypi/l/stirlingpdf-agent)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/stirlingpdf-agent)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/stirlingpdf-agent)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/stirlingpdf-agent)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/stirlingpdf-agent)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/stirlingpdf-agent)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/stirlingpdf-agent)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/stirlingpdf-agent)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/stirlingpdf-agent)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/stirlingpdf-agent)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/stirlingpdf-agent)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/stirlingpdf-agent)

*Version: 0.11.1*

## Overview

**Stirling PDF Agent MCP Server + A2A Agent**

Agent package for communicating with Stirling PDF via REST APIs.

This repository is actively maintained - Contributions are welcome!

## MCP

### Using as an MCP Server

The MCP Server can be run in two modes: `stdio` (for local testing) or `http` (for networked access).

#### Environment Variables

*   `STIRLINGPDF_URL`: The URL of the target service.
*   `STIRLINGPDF_API_KEY`: The API token or access token.

#### Run in stdio mode (default):
```bash
export STIRLINGPDF_URL="http://localhost:8080"
export STIRLINGPDF_API_KEY="your_token"
stirlingpdf-mcp --transport "stdio"
```

#### Run in HTTP mode:
```bash
export STIRLINGPDF_URL="http://localhost:8080"
export STIRLINGPDF_API_KEY="your_token"
stirlingpdf-mcp --transport "http" --host "0.0.0.0" --port "8000"
```

## A2A Agent

### Run A2A Server
```bash
export STIRLINGPDF_URL="http://localhost:8080"
export STIRLINGPDF_API_KEY="your_token"
stirlingpdf-agent --provider openai --model-id gpt-4o --api-key sk-...
```

## Security & Governance

This project is built on [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities), inheriting enterprise-grade security and governance features.

### Authentication & Authorization
| Feature | Description |
|---------|-------------|
| **OIDC Token Delegation** | RFC 8693 token exchange for user-context propagation from A2A → MCP |
| **Eunomia Policies** | Fine-grained, policy-driven tool authorization (`none`, `embedded`, `remote`) |
| **Scoped Credentials** | Tools execute with the caller's scoped identity where possible |
| **3LO / OAuth / API Token** | Multiple auth strategies with graceful fallback |

### Eunomia Policy Enforcement
Eunomia provides a policy enforcement point for all tool calls:
- **Embedded mode**: Load local `mcp_policies.json` for role-based access, sensitivity gating, and audit logging
- **Remote mode**: Forward authorization decisions to a central Eunomia policy server for multi-agent governance
- Enable via CLI: `--eunomia-type embedded --eunomia-policy-file mcp_policies.json`

### Runtime Protections
| Protection | Description |
|------------|-------------|
| **Tool Guard** | Sensitivity detection with human-in-the-loop approval gating |
| **Prompt Injection Defense** | Input scanning and repetition/loop guards |
| **Content Filtering** | Output schema enforcement and cost budget controls |
| **Stuck Loop Detection** | Automatic detection and recovery from agent loops |
| **Context Limit Warnings** | Proactive alerts before context window exhaustion |

### Graph Agent Architecture
The A2A agent uses `pydantic-graph` orchestration with:
- **RouterNode**: Lightweight classifier that routes queries to specialized domains
- **DomainNode**: Focused executor with only relevant tools loaded, preventing tool hallucination
- **Approval Gates**: Policy-driven approval workflows before sensitive operations
- **Usage Guards**: Budget and rate limiting enforcement

> **Production Recommendation**: Enable `--eunomia-type embedded` (or `remote`) + OIDC delegation + containerized deployment. See [`agent-utilities` documentation](https://github.com/Knuckles-Team/agent-utilities) for full policy configuration.

## Docker

### Build

```bash
docker build -t stirlingpdf-agent .
```

### Run MCP Server

```bash
docker run -d \
  --name stirlingpdf-agent \
  -p 8000:8000 \
  -e TRANSPORT=http \
  -e STIRLINGPDF_URL="http://your-service:8080" \
  -e STIRLINGPDF_API_KEY="your_token" \
  knucklessg1/stirlingpdf-agent:latest
```

### Deploy with Docker Compose

```yaml
services:
  stirlingpdf-agent:
    image: knucklessg1/stirlingpdf-agent:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=http
      - STIRLINGPDF_URL=http://your-service:8080
      - STIRLINGPDF_API_KEY=your_token
    ports:
      - 8000:8000
```

#### Configure `mcp.json` for AI Integration (e.g. Claude Desktop)

```json
{
  "mcpServers": {
    "stirlingpdf": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "stirlingpdf-agent",
        "stirlingpdf-mcp"
      ],
      "env": {
        "STIRLINGPDF_URL": "http://your-service:8080",
        "STIRLINGPDF_API_KEY": "your_token"
      }
    }
  }
}
```

## Install Python Package

```bash
python -m pip install stirlingpdf-agent
```
```bash
uv pip install stirlingpdf-agent
```

## Repository Owners

<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)


## MCP Configuration Examples

### stdio (recommended for local development)
```json
{
  "mcpServers": {
    "stirlingpdf": {
      "command": ".venv/bin/stirlingpdf-mcp",
      "args": [],
      "env": {
        "STIRLINGPDF_URL": "",
        "STIRLINGPDF_API_KEY": ""
}
    }
  }
}
```

### Streamable HTTP (recommended for production)
```json
{
  "mcpServers": {
    "stirlingpdf": {
      "url": "http://localhost:8080/stirlingpdf-mcp/mcp"
    }
  }
}
```
