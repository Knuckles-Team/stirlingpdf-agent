---
name: stirlingpdf-agent-docs
skill_type: skill
description: Reference documentation for Stirling PDF, crawled from its public docs site. Use when the agent needs to look up Stirling PDF features, settings or API behaviour before calling the stirlingpdf-agent tools. Do NOT use to run PDF operations (use stirlingpdf-document-operations).
crawl_depth: 2
source_url: https://docs.stirlingpdf.com
categories: [Documentation, Knowledge Base, Reference]
tags: [docs, reference, stirlingpdf-agent-docs, knowledge-base]
---

# Stirlingpdf Agent Docs Documentation

Comprehensive reference documentation for Stirlingpdf Agent Docs.

**Original Sources**:
- [https://docs.stirlingpdf.com](https://docs.stirlingpdf.com)

**Contains**: 1 markdown files with full folder structure (crawled at depth 2).
*Last updated: March 05, 2026*

## 📚 Table of Contents

- [Index](references/index.md)

## Steps
1. Search the reference for the topic with `grep -n -i "<term>" references/index.md`. Verify at least one matching line number is returned.
2. Read the matching section with `sed -n '<start>,<end>p' references/index.md`. Verify the quoted text covers the question asked.
3. Cite the exact quote and the original source link `https://docs.stirlingpdf.com` in the answer. Verify the quote appears verbatim in the file.

## Failure recovery
| Failure | Cause | Recovery |
|---------|-------|----------|
| `grep` returns nothing | The term is not in the crawled page | Try a synonym with `grep -n -i`, or search the live source `https://docs.stirlingpdf.com` |
| Section looks outdated | The crawl is dated (see "Last updated" above) | Compare with the live source and state the crawl date in the answer |
| Cookie-banner text in results | The crawl captured page chrome | Skip those lines and read the section headings, such as `## Benefits of Stirling-PDF` |

## 🤖 Agent Usage Guide

- When the user asks anything about **Stirlingpdf Agent Docs**, consult the reference files.
- Prefer exact quotes and direct links to the relevant file/section.
- The hierarchical TOC above makes navigation fast and intuitive.
- All images and assets are preserved so links work perfectly.
