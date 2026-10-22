# CONN-STIRLINGPDF-AGENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

The SDK registers one typed tool per client method. The SDK derives the read-only annotation from the method name.

## Architecture

The client method calls the external API. The SDK wraps the method as one MCP tool.

## Interfaces and data model

The change adds no wire field. The tool returns the API response document.

## Live integration path

The fleet gateway lists the tool, reads its annotation and calls it as the gateway identity.

## Quality and release gates

The focused tests run with `pytest -q`. A merge to the default branch publishes the package and the image.

## Risks, alternatives, and decisions

No new risk. The operation reads state and changes nothing.
