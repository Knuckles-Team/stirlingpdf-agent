# MCP_AGENTS.md - Dynamic Agent Registry

This file tracks the generated agents from MCP servers. You can manually modify the 'Tools' list to customize agent expertise.

## Agent Mapping Table

| Name | Description | System Prompt | Tools | Tag | Source MCP |
|------|-------------|---------------|-------|-----|------------|
| Stirlingpdf Pdf Specialist | Expert specialist for pdf domain tasks. | You are a Stirlingpdf Pdf specialist. Help users manage and interact with Pdf functionality using the available tools. | stirlingpdf-agent_pdf_toolset | pdf | stirlingpdf-agent |

## Tool Inventory Table

| Tool Name | Description | Tag | Source |
|-----------|-------------|-----|--------|
| stirlingpdf-agent_pdf_toolset | Static hint toolset for pdf based on config env. | pdf | stirlingpdf-agent |
