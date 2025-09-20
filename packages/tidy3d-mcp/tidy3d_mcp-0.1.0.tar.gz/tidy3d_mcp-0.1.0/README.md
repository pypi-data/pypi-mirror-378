# Tidy3D MCP Proxy

FastMCP proxy that bridges stdio-only MCP clients to the Flexcompute Tidy3D viewer tooling.

## Features

- Proxies the remote FlexAgent MCP endpoint while authenticating with OAuth.
- Exposes viewer automation utilities (launch, rotate, visibility, status, screenshots).
- Serves local screenshot files and indexes as MCP resources.

## Quick Start

1. Ensure `uv` is available and Python 3.10+ is active.
2. Install dependencies: `uv sync`.
3. Launch the proxy: `uv run tidy3d-mcp-proxy`.

Set `REMOTE_MCP_URL` to point at an alternative MCP endpoint if needed. OAuth tokens are cached under `~/.fastmcp/oauth-mcp-client-cache` scoped by proxy workspace.
