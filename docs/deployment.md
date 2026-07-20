# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`stirlingpdf-agent` supports local stdio, a loopback-only development listener, a
least-privilege stdio container, and a remote authenticated HTTPS boundary.
Provider endpoint, credential, selector, identity, and trust material are supplied
at runtime through `AgentConfig`; none is stored in this repository.

### Installed stdio process

```json
{
  "mcpServers": {
    "stirlingpdf": {
      "command": "stirlingpdf-mcp",
      "args": [],
      "env": {"MCP_TOOL_MODE": "intent"}
    }
  }
}
```

### Loopback development listener

```bash
stirlingpdf-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Do not expose this listener beyond loopback. Network deployments require direct TLS
or an explicitly trusted TLS-terminating ingress, configured authentication, exact
`MCP_ALLOWED_HOSTS`, and an exact trusted-proxy CIDR policy.

### Least-privilege local container

```bash
docker run -i --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --pids-limit=256 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \
  -e TRANSPORT=stdio \
  registry.example.invalid/stirlingpdf-agent@sha256:<digest> stirlingpdf-mcp
```

The operator projects the selected AgentConfig profile into the process at runtime;
the image remains immutable and contains no environment connection profile.

### Remote authenticated HTTPS endpoint

```json
{
  "mcpServers": {
    "stirlingpdf": {"url": "https://service.example.invalid/mcp"}
  }
}
```

Store the real remote URL, outbound identity reference, and TLS-profile reference in
`AgentConfig`, not in MCP client JSON or documentation.
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
| `STIRLINGPDF_URL` | Required | Stirling PDF service base URL |
| `STIRLINGPDF_API_KEY` | _(empty)_ | API key for the Stirling PDF service (sent as `X-API-KEY`) |
| `TLS_PROFILE` | _(empty)_ | Named `AgentConfig` transport-security profile; verification is mandatory |
| `TLS_PROFILES_REF` | _(empty)_ | Runtime secret reference for the TLS profile catalog |
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
    image: example/stirlingpdf-agent@sha256:<digest>
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
export STIRLINGPDF_URL=<configured-endpoint>
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
    image: example/stirlingpdf-agent@sha256:<digest>
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
# Internal (self-signed) — homelab .example.invalid zone
stirlingpdf-agent.example.invalid {
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
curl -s "http://technitium.example.invalid:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=stirlingpdf-agent.example.invalid" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=192.0.2.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `stirlingpdf-agent.example.invalid → <caddy-host-ip>` in the Technitium
web console (`http://technitium.example.invalid:5380`). The ecosystem
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
        "STIRLINGPDF_URL": "<configured-endpoint>",
        "STIRLINGPDF_API_KEY": "your_token",
        "TLS_PROFILE": "private-pki",
        "TLS_PROFILES_REF": "secret://runtime/tls-profiles"
      }
    }
  }
}
```

For a remote HTTP server, point the client at `http://stirlingpdf-agent.example.invalid/mcp`
instead.
