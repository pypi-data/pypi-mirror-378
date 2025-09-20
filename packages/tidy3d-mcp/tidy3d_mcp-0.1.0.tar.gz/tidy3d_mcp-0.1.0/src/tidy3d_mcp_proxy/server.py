from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from fastmcp import FastMCP, settings as fastmcp_settings
from fastmcp.client.auth.oauth import OAuth
from fastmcp.resources.template import ResourceTemplate
from fastmcp.server.proxy import ProxyClient
from fastmcp.tools import Tool

from .resources import screenshot_file, screenshot_index
from .tools import (
    capture_screenshot,
    check_simulation,
    clear_screenshots,
    rotate_viewer,
    set_viewer_structure_visibility,
    start_viewer,
)


def _cache_dir_for_mcp(url: str, *, workdir: Path | None = None) -> Path:
    """Return a unique OAuth cache directory for the given MCP URL and working directory."""
    parsed = urlparse(url)
    slug_source = f'{parsed.scheme}://{parsed.netloc}{parsed.path}'
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', slug_source).strip('_') or 'default'
    digest = hashlib.sha256(url.encode('utf-8')).hexdigest()[:12]

    base = (workdir or Path.cwd()).resolve()
    workspace_key = str(base)
    workspace_digest = hashlib.sha256(workspace_key.encode('utf-8')).hexdigest()[:12]
    workspace_label_source = (
        base.name or re.sub(r'[^a-zA-Z0-9]+', '_', base.anchor).strip('_') or 'workspace'
    )
    workspace_slug = re.sub(r'[^a-zA-Z0-9]+', '_', workspace_label_source).strip('_') or 'workspace'

    return (
        fastmcp_settings.home
        / 'oauth-mcp-client-cache'
        / f'{slug}_{digest}'
        / f'{workspace_slug}_{workspace_digest}'
    )


def main():
    """Launch the FastMCP proxy exposing viewer tools and resources."""
    mcp_url = os.getenv('REMOTE_MCP_URL', 'https://flexagent.dev-simulation.cloud/')
    cache_dir = _cache_dir_for_mcp(mcp_url, workdir=Path.cwd())
    oauth = OAuth(mcp_url=mcp_url, token_storage_cache_dir=cache_dir)
    proxy = FastMCP.as_proxy(ProxyClient(mcp_url, auth=oauth), name='Tidy3D')

    proxy.add_tool(Tool.from_function(start_viewer))
    proxy.add_tool(Tool.from_function(capture_screenshot))
    proxy.add_tool(Tool.from_function(clear_screenshots))
    proxy.add_tool(Tool.from_function(rotate_viewer))
    proxy.add_tool(Tool.from_function(set_viewer_structure_visibility))
    proxy.add_tool(Tool.from_function(check_simulation))

    proxy.add_template(
        ResourceTemplate.from_function(
            fn=screenshot_index,
            uri_template='screenshot://{viewer_id}/index.json',
            mime_type='application/json',
        )
    )
    proxy.add_template(
        ResourceTemplate.from_function(
            fn=screenshot_file,
            uri_template='screenshot://{viewer_id}/{name}',
            mime_type='image/png',
        )
    )

    proxy.run()


if __name__ == '__main__':
    main()
