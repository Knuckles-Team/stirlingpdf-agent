---
name: stirlingpdf-agent-development
skill_type: skill
domain: development
description: >-
  Develop, test, gate, and release the stirlingpdf-agent connector. Use this
  skill when changing Stirling PDF API mappings, MCP content, packaging,
  documentation, or repository gates.
license: MIT
tags: [stirlingpdf-agent, development, connector, test, gates]
tier: repository
metadata:
  author: Genius
  version: '0.1.0'
---

# stirlingpdf-agent development

This repository owns the Stirling PDF REST client, connector identity, MCP
surface, packaged skills, prompts, ontology, and source bindings. Shared
connector transports and contracts belong to `agent-connector-sdk`; admission,
serving, and durable graph state belong to their owning repositories. Read
`AGENTS.md` before changing code and keep provider credentials, endpoints, and
customer data out of source, logs, and skill content.

## Rapid delivery: the 5-minute contract

Specs are already designed. Deliver small, reviewable slices and cite the
owning spec row in the commit trailer.

- Find the owning row first with `git grep -n "<term>" -- specs` and extend the
  existing spec before adding new requirement text.
- Reuse the existing SDK connector, REST client, manifest, and packaged content
  declarations. Do not create a second transport or connector identity.
- Keep changes scoped to this connector. Work owned by the SDK, Arbora, or the
  knowledge graph belongs in that repository instead.
- Bind delivered behavior to a focused test. Generated `status.json` files are
  produced by `pipelines-hook spec-status`; never hand-edit them.
- Use `Spec: <ID>` and the assisting agent trailer on consecutive final commit
  message lines when a change delivers a requirement.

## Setup and gates

Use the pinned environment from `uv sync --locked`. Run the repository gate
from the checkout root:

```bash
uv sync --locked
uvx pre-commit run --all-files
```

For focused feedback, run the repository's actual mocked tests:

```bash
uv run --all-extras pytest tests/test_publication_workflow.py -q
uv run --all-extras pytest tests/test_read_only_status.py tests/test_fleet_name.py -q
```

The canonical `.pre-commit-config.yaml` delegates connector-standard, secrets,
spec, tests-fast, and dependency-readiness checks to
`Knuckles-Team/pipelines` at `rev: main`. Keep those shared hooks intact and
fix failures at their source instead of bypassing them.

## Connector-specific checks

- Mock Stirling PDF requests in tests; never use live service credentials in a
  local gate.
- Keep `STIRLINGPDF_URL`, `STIRLINGPDF_API_KEY`, and TLS settings sourced from
  the existing environment configuration; never hardcode endpoints or secrets.
- Keep `stirlingpdf_agent/skills/` package data intact when adding skills.
- Preserve the single `stirlingpdf-mcp` connector identity across the manifest,
  content pack, fingerprints, and ingest bindings.
- Documentation lives under `docs/`, and generated delivery status comes from
  `specs/*/status.json`.

## Delivery discipline

Work in a real Git worktree based on `origin/main`. Inspect the complete diff,
stage only reviewed paths, and verify `git status --short` after every gate.
Do not use `git stash`, `git add -A`, or `git add .`; do not claim Pages
publication until a successful exact-source workflow run and the public
dashboard are both observed.
