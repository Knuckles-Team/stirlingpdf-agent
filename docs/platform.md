# Backing Platform — Stirling PDF

`stirlingpdf-agent` is a **client** of a [Stirling PDF](https://www.stirlingpdf.com/)
service. This page provides a Docker recipe for deploying one locally to serve as the
target of `STIRLINGPDF_URL`. For production topologies, follow the upstream
[Stirling PDF documentation](https://docs.stirlingpdf.com/).

!!! note "Backing-system recipe"
    Each connector in the ecosystem follows the same convention — a
    `docs/platform.md` recipe for the system it integrates with, accompanied by a
    sample Compose stack that mirrors [`services/`](https://github.com/Knuckles-Team).
    Systems offered only as a managed service have no local recipe.

## Single-node deployment (Compose)

Stirling PDF publishes an official image. The following stack runs one instance on
`:8080`:

```yaml
# docker/stirling-pdf.compose.yml
services:
  stirling-pdf:
    image: docker.stirlingpdf.com/stirlingtools/stirling-pdf@sha256:<digest>
    container_name: stirling-pdf
    hostname: stirling-pdf
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - DISABLE_ADDITIONAL_FEATURES=false
      - LANGS=en_GB
    volumes:
      - training_data:/usr/share/tessdata
      - extra_configs:/configs
      - custom_files:/customFiles/
      - logs:/logs/
      - pipeline:/pipeline/
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8080/api/v1/info/status"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 40s

volumes:
  training_data:
  extra_configs:
  custom_files:
  logs:
  pipeline:
```

```bash
docker compose -f docker/stirling-pdf.compose.yml up -d

# Wait for the service to answer
curl -fsS http://localhost:8080/api/v1/info/status
```

## Connect stirlingpdf-agent

```bash
export STIRLINGPDF_URL=<configured-endpoint>
export STIRLINGPDF_API_KEY=your_token          # if the service requires one
export TLS_PROFILE=private-pki
export TLS_PROFILES_REF=secret://runtime/tls-profiles

stirlingpdf-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Combined deployment

A combined stack places Stirling PDF and the MCP server on one Docker network, so the
server reaches the service by container name:

```yaml
# docker/stack.compose.yml
services:
  stirling-pdf:
    image: docker.stirlingpdf.com/stirlingtools/stirling-pdf@sha256:<digest>
    hostname: stirling-pdf
    ports: ["8080:8080"]
    environment:
      - DISABLE_ADDITIONAL_FEATURES=false
      - LANGS=en_GB

  stirlingpdf-agent-mcp:
    image: example/stirlingpdf-agent@sha256:<digest>
    depends_on: [stirling-pdf]
    environment:
      - STIRLINGPDF_URL=${STIRLINGPDF_URL:?required}
      - TLS_PROFILE=private-pki
      - TLS_PROFILES_REF=secret://runtime/tls-profiles
      - TRANSPORT=streamable-http
      - HOST=0.0.0.0
      - PORT=8000
    ports: ["8000:8000"]
```

```bash
docker compose -f docker/stack.compose.yml up -d
```

With the service running, the [MCP tools and the `StirlingPdfApi` client](usage.md)
operate against it directly.
