from __future__ import annotations

import os
import time
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlencode

from ..utils import find_free_port, open_uri, serve_once


_VIEWER_AUTHORITY = 'Flexcompute.tidy3d-viewer'


def _viewer_uri_prefixes() -> tuple[str, ...]:
    """Return viewer URI prefixes ordered by preference."""
    override = os.environ.get('TIDY3D_VIEWER_URI_SCHEMES', '')
    if override:
        schemes = tuple(
            f'{candidate.strip()}://{_VIEWER_AUTHORITY}'
            for candidate in override.split(',')
            if candidate.strip()
        )
        if schemes:
            return schemes
    program = os.environ.get('TERM_PROGRAM', '').lower()
    if program.startswith('cursor'):
        return (
            f'cursor://{_VIEWER_AUTHORITY}',
            f'vscode://{_VIEWER_AUTHORITY}',
        )
    return (
        f'vscode://{_VIEWER_AUTHORITY}',
        f'cursor://{_VIEWER_AUTHORITY}',
    )


def _stringify_params(params: Mapping[str, object | None]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        result[key] = str(value)
    return result


def invoke_viewer_command(
    action: str,
    callback_segment: str,
    params: Mapping[str, object | None],
    *,
    timeout: float,
) -> dict[str, Any]:
    """Dispatch a viewer URI command and wait for its callback payload."""
    port = find_free_port()
    nonce = str(int(time.time() * 1000))
    callback_path = f'/cb/{callback_segment}/{nonce}'
    query_params = _stringify_params(params)
    with serve_once(port, callback_path) as session:
        query_params['cb'] = f'http://127.0.0.1:{port}{callback_path}'
        encoded_params = urlencode(query_params)
        for prefix in _viewer_uri_prefixes():
            link = f'{prefix}/{action}?{encoded_params}'
            if open_uri(link):
                break
        else:
            raise RuntimeError('no supported viewer URI scheme')
        if not session.wait(timeout):
            raise RuntimeError(f'timed out waiting for {action} callback')
        payload = session.payload
    if not isinstance(payload, dict):
        raise RuntimeError(f'unexpected payload for {action}')
    return payload
