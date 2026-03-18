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

*Version: 0.1.17*

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
