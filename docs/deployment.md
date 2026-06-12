# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`stirlingpdf-agent` exposes its MCP server (console script `stirlingpdf-mcp`) four ways. Pick the row that
matches where the server runs relative to your MCP client, then copy the matching
`mcp_config.json` below. Replace the `<your-…>` placeholders with the values from the **Configuration / Environment Variables** section.

| # | Option | Transport | Where it runs | `mcp_config.json` key |
|---|--------|-----------|---------------|------------------------|
| 1 | stdio | `stdio` | client launches a subprocess | `command` |
| 2 | Streamable-HTTP (local) | `streamable-http` | a local network port | `command` or `url` |
| 3 | Local container / uv | `stdio` or `streamable-http` | Docker / Podman / uv on this host | `command` or `url` |
| 4 | Remote URL | `streamable-http` | a remote host behind Caddy | `url` |

### 1. stdio (local subprocess)

The client launches the server over stdio via `uvx` — best for local IDEs
(Cursor, Claude Desktop, VS Code):

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": {
      "command": "uvx",
      "args": ["--from", "stirlingpdf-agent", "stirlingpdf-mcp"],
      "env": {
        "STIRLINGPDF_URL": "<your-stirlingpdf_url>",
        "STIRLINGPDF_API_KEY": "<your-stirlingpdf_api_key>"
      }
    }
  }
}
```

### 2. Streamable-HTTP (local process)

Run the server as a long-lived HTTP process:

```bash
uvx --from stirlingpdf-agent stirlingpdf-mcp --transport streamable-http --host 0.0.0.0 --port 8000
curl -s http://localhost:8000/health        # {"status":"OK"}
```

Then either let the client launch it:

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": {
      "command": "uvx",
      "args": ["--from", "stirlingpdf-agent", "stirlingpdf-mcp", "--transport", "streamable-http", "--port", "8000"],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "STIRLINGPDF_URL": "<your-stirlingpdf_url>",
        "STIRLINGPDF_API_KEY": "<your-stirlingpdf_api_key>"
      }
    }
  }
}
```

…or connect to the already-running process by URL:

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": { "url": "http://localhost:8000/mcp" }
  }
}
```

### 3. Local container / uv

**(a) Launch a container directly from `mcp_config.json`** (stdio over the container —
no ports to manage). Swap `docker` for `podman` for a daemonless runtime:

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "TRANSPORT=stdio",
        "-e", "STIRLINGPDF_URL=<your-stirlingpdf_url>",
        "-e", "STIRLINGPDF_API_KEY=<your-stirlingpdf_api_key>",
        "knucklessg1/stirlingpdf-agent:latest"
      ]
    }
  }
}
```

**(b) Run a local streamable-http container, then connect by URL:**

```bash
docker run -d --name stirlingpdf-mcp -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e PORT=8000 \
  -e STIRLINGPDF_URL="<your-stirlingpdf_url>" \
  -e STIRLINGPDF_API_KEY="<your-stirlingpdf_api_key>" \
  knucklessg1/stirlingpdf-agent:latest
# or, from a clone of this repo:
docker compose -f docker/mcp.compose.yml up -d
```

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": { "url": "http://localhost:8000/mcp" }
  }
}
```

**(c) From a local checkout with `uv`:**

```bash
uv run stirlingpdf-mcp --transport streamable-http --port 8000
```

### 4. Remote URL (deployed behind Caddy)

When the server is deployed remotely (e.g. as a Docker service) and published through
Caddy on the internal `*.arpa` zone, connect with the `"url"` key — no local process or
image required:

```json
{
  "mcpServers": {
    "stirlingpdf-mcp": { "url": "http://stirlingpdf-mcp.arpa/mcp" }
  }
}
```

Caddy reverse-proxies `http://stirlingpdf-mcp.arpa` to the container's `:8000`
streamable-http listener; `http://stirlingpdf-mcp.arpa/health` returns
`{"status":"OK"}` when the service is live.
<!-- END GENERATED: deployment-options -->

This page covers running `stirlingpdf-agent` as a long-lived server: the transports,
a Docker Compose stack, the optional A2A agent server, putting it behind a Caddy
reverse proxy, and giving it a DNS name with Technitium. To provision the **Stirling
PDF** service it connects to, see [Backing Platform](platform.md).

> `stirlingpdf-agent` ships **two** console scripts: an **MCP server**
> (`stirlingpdf-mcp`) exposing the typed PDF tool surface, and an **A2A agent server**
> (`stirlingpdf-agent`) — a Pydantic-AI agent that drives those tools for multi-step
> workflows.

## Run the MCP server

The transport is selected with `--transport` (or the `TRANSPORT` env var):

=== "stdio (default)"

    ```bash
    stirlingpdf-mcp
    ```
    For IDE / desktop MCP clients that launch the server as a subprocess.

=== "streamable-http"

    ```bash
    stirlingpdf-mcp --transport streamable-http --host 0.0.0.0 --port 8000
    ```
    A network server with a `/health` endpoint and `/mcp` route.

=== "sse"

    ```bash
    stirlingpdf-mcp --transport sse --host 0.0.0.0 --port 8000
    ```

Health check (HTTP transports):

```bash
curl -s http://localhost:8000/health        # {"status":"OK"}
```

## Configuration (environment)

`stirlingpdf-agent` is configured entirely from the environment. The **required** set:

| Var | Default | Meaning |
|---|---|---|
| `STIRLINGPDF_URL` | `http://localhost:8080` | Stirling PDF service base URL |
| `STIRLINGPDF_API_KEY` | _(empty)_ | API key for the Stirling PDF service (sent as `X-API-KEY`) |
| `STIRLINGPDF_AGENT_VERIFY` | `True` | Verify TLS (set `False` for self-signed homelab) |
| `PDFTOOL` | `True` | Register the PDF tool set |
| `HOST` | `0.0.0.0` | Bind address (HTTP transports) |
| `PORT` | `8000` | Bind port (HTTP transports) |
| `TRANSPORT` | `stdio` | `stdio`, `streamable-http`, or `sse` |

The full set, including telemetry (`ENABLE_OTEL`, OTLP exporter) and access-governance
(`EUNOMIA_*`) variables, is documented in
[`.env.example`](https://github.com/Knuckles-Team/stirlingpdf-agent/blob/main/.env.example).
Copy it to `.env` and populate only what you use.

## Docker Compose

The repo ships [`docker/mcp.compose.yml`](https://github.com/Knuckles-Team/stirlingpdf-agent/blob/main/docker/mcp.compose.yml).
It reads a sibling `.env` and publishes the HTTP server on `:8000`:

```yaml
services:
  stirlingpdf-agent-mcp:
    image: knucklessg1/stirlingpdf-agent:latest
    container_name: stirlingpdf-agent-mcp
    hostname: stirlingpdf-agent-mcp
    restart: always
    env_file:
      - ../.env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
cp .env.example .env          # then edit STIRLINGPDF_* values
docker compose -f docker/mcp.compose.yml up -d
docker compose -f docker/mcp.compose.yml logs -f
```

## Run the A2A agent server

The agent server is a Pydantic-AI agent (console script `stirlingpdf-agent`) that
connects to the MCP server over `MCP_URL` and exposes an A2A / web-UI surface. It
listens on port `9004`:

```bash
export STIRLINGPDF_URL=http://your-stirlingpdf:8080
export STIRLINGPDF_API_KEY=your_token
export MCP_URL=http://localhost:8000/mcp
stirlingpdf-agent --provider openai --model-id gpt-4o --api-key sk-...
```

The repo ships [`docker/agent.compose.yml`](https://github.com/Knuckles-Team/stirlingpdf-agent/blob/main/docker/agent.compose.yml),
which deploys the MCP server and the agent server together. The agent service wires
itself to the MCP server by container name:

```yaml
services:
  stirlingpdf-agent-agent:
    image: knucklessg1/stirlingpdf-agent:latest
    container_name: stirlingpdf-agent-agent
    depends_on:
      - stirlingpdf-agent-mcp
    command: ["stirlingpdf-agent"]
    environment:
      - HOST=0.0.0.0
      - PORT=9004
      - MCP_URL=http://stirlingpdf-agent-mcp:8000/mcp
      - PROVIDER=${PROVIDER:-openai}
      - MODEL_ID=${MODEL_ID:-gpt-4o}
      - ENABLE_WEB_UI=True
    ports:
      - "9004:9004"
```

```bash
docker compose -f docker/agent.compose.yml up -d
```

## Behind a Caddy reverse proxy

Expose the HTTP server on a hostname with automatic TLS. Add to your `Caddyfile`:

```caddy
# Internal (self-signed) — homelab .arpa zone
stirlingpdf-agent.arpa {
    tls internal
    reverse_proxy stirlingpdf-agent-mcp:8000
}
```

```caddy
# Public — automatic Let's Encrypt
stirlingpdf-agent.example.com {
    reverse_proxy stirlingpdf-agent-mcp:8000
}
```

Reload Caddy:

```bash
docker compose -f services/caddy/compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS with Technitium

Point the hostname at the host running Caddy. Via the Technitium API:

```bash
curl -s "http://technitium.arpa:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=stirlingpdf-agent.arpa" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=10.0.0.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `stirlingpdf-agent.arpa → <caddy-host-ip>` in the Technitium
web console (`http://technitium.arpa:5380`). The ecosystem
[`technitium-dns-mcp`](https://knuckles-team.github.io/technitium-dns-mcp/) automates
this as a tool.

## Register with an MCP client

Add to your client's `mcp_config.json`:

```json
{
  "mcpServers": {
    "stirlingpdf-agent": {
      "command": "uv",
      "args": ["run", "stirlingpdf-mcp"],
      "env": {
        "PDFTOOL": "True",
        "STIRLINGPDF_URL": "http://your-stirlingpdf:8080",
        "STIRLINGPDF_API_KEY": "your_token",
        "STIRLINGPDF_AGENT_VERIFY": "True"
      }
    }
  }
}
```

For a remote HTTP server, point the client at `http://stirlingpdf-agent.arpa/mcp`
instead.
