---
name: stirlingpdf-agent-operations
skill_type: skill
description: >-
  Operate stirlingpdf-agent through its governed MCP and Arbora capabilities, including stirlingpdf agent docs, stirlingpdf document operations, stirlingpdf knowledge graph, stirlingpdf watermarking. Use when a request requires this provider's read, change, automation, ingestion, troubleshooting, or evidence workflows.
---

# Stirlingpdf Agent Operations

Use the provider's governed MCP tools through Arbora delegation.

## Workflow

1. Establish the verified GraphSession and tenant before discovery or retrieval.
2. Discover the current condensed tool surface; never assume a stale tool name or schema.
3. Prefer read-only inspection first. For changes, present impact and use the provider's
   dry-run or preview mode when available.
4. Execute mutations as fenced WorkItems so retries remain idempotent and auditable.
5. Ingest source data only through the signed connector preset and ChangeEnvelope path.
6. Verify the durable result and its trace/evidence before reporting completion.

## Steps
1. Establish the verified GraphSession and tenant with `ask(intent='show my session and tenant')`. Verify the session reports an authenticated tenant.
2. Discover the current tool surface with `find(intent='stirlingpdf')`. Verify the returned tool names and schemas before using any.
3. Run a read-only inspection first, such as `stirlingpdf_get_status`. Verify the response reports a healthy server version.
4. For a change, preview the plan with `act` and resubmit with `execute=true` only after approval. Verify the preview lists the intended operation and file.
5. Check the durable result and its trace with `ask(intent='show the trace of this operation')`. Verify the evidence record exists before reporting completion.

## Failure recovery
| Failure | Cause | Recovery |
|---------|-------|----------|
| Tool name or schema not found | A stale tool name was assumed | Call `find(intent='stirlingpdf')` again and use the returned tool name and params |
| Mutation refused | No approval or no verified session | Obtain explicit approval, re-establish the GraphSession, and resubmit the previewed plan with `execute=true` |
| Server unreachable | `STIRLINGPDF_URL` unset or wrong | Ask the operator to correct `STIRLINGPDF_URL`, then confirm with `stirlingpdf_get_status` |

## Safety contract

- Never persist credentials, endpoints, raw personal identifiers, hostnames, or local paths.
- Resolve TLS trust and verification from environment/configuration; never hardcode bypasses.
- Treat unknown ACL, tenant, schema, or tool-contract state as a hard failure.
- Require explicit approval for destructive, externally visible, or irreversible actions.
- Keep runtime traces policy-scoped and privacy-sanitized.

## Specialized workflows

Read [the workflow catalog](references/catalog.md) only when the request needs a
provider-specific procedure, parameter map, script, or reference asset.
