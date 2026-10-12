---
applyTo: "**"
description: When codebase-memory-mcp is connected, prefer its graph tools over grep/glob for code discovery. Apply only when MCP server exposes search_graph / trace_path / get_code_snippet / query_graph / get_architecture.
---

# Codebase Knowledge Graph (codebase-memory-mcp)

This MCP server exposes graph tools for code discovery. When it is
connected to the active tool session, prefer these tools over raw
file search.

## Priority Order

1. `search_graph` — find functions, classes, routes, variables by pattern
2. `trace_path` — trace who calls a function or what it calls
3. `get_code_snippet` — read specific function/class source code
4. `query_graph` — run Cypher queries for complex patterns
5. `get_architecture` — high-level project summary

## When to fall back to grep/glob

- Searching for string literals, error messages, config values
- Searching non-code files (Dockerfiles, shell scripts, configs)
- When MCP tools return insufficient results

## Examples

- Find a handler: `search_graph(name_pattern=".*OrderHandler.*")`
- Who calls it: `trace_path(function_name="OrderHandler", direction="inbound")`
- Read source: `get_code_snippet(qualified_name="pkg/orders.OrderHandler")`
