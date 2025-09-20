from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from ..utils import ensure_file_uri
from ._dispatcher import invoke_viewer_command


def _normalize_warnings(raw: object) -> list[str] | None:
    if not raw:
        return None
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, Iterable):
        normalized = [str(item) for item in raw if item]
        return normalized or None
    return [str(raw)]


async def start_viewer(
    file: str,
    symbol: str | None = None,
    index: int | None = None,
    window_id: str | None = None,
) -> dict[str, Any]:
    """Open the viewer for `file` and wait for its ready payload.

    Optionally selects `symbol` or `index` within the target `window_id`. The
    returned mapping always contains `viewer_id` and may also provide `status`,
    `window_id`, and `warnings`. Raises `RuntimeError` if the viewer fails to
    acknowledge the request or reports an error.
    """
    params: dict = {'file': ensure_file_uri(file)}
    if symbol:
        params['symbol'] = symbol
    if index is not None:
        params['index'] = index
    if window_id:
        params['window'] = window_id
    result = invoke_viewer_command('start', 'ready', params, timeout=300.0)
    error_msg = result.get('error')
    if isinstance(error_msg, str) and error_msg:
        raise RuntimeError(f'Viewer reported error: {error_msg}')
    viewer_id = result.get('viewer_id')
    if not isinstance(viewer_id, str) or not viewer_id:
        raise RuntimeError('Viewer did not report ready')
    response: dict[str, Any] = {'viewer_id': viewer_id}
    status = result.get('status')
    if isinstance(status, str) and status:
        response['status'] = status
    reported_window = result.get('window_id')
    if isinstance(reported_window, str) and reported_window:
        response['window_id'] = reported_window
    warnings = _normalize_warnings(result.get('warnings') or result.get('warning'))
    if warnings:
        response['warnings'] = warnings
    return response


async def rotate_viewer(
    viewer_id: str, direction: str, window_id: str | None = None
) -> dict[str, Any]:
    """Rotate `viewer_id` toward `direction`, scoped to `window_id` when given.

    Returns the viewer identifier, the normalized direction string, and the
    reported status. Raises `ValueError` when `direction` is empty and
    `RuntimeError` when the viewer reports a failure or fails to respond.
    """
    if not direction:
        raise ValueError('direction is required')
    normalized = direction.upper()
    params: dict[str, object | None] = {'viewer': viewer_id, 'direction': normalized}
    if window_id:
        params['window'] = window_id
    result = invoke_viewer_command('rotate', 'rotate', params, timeout=60.0)
    error_msg = result.get('error')
    if isinstance(error_msg, str) and error_msg:
        raise RuntimeError(f'Rotation failed: {error_msg}')
    status = result.get('status', 'ok')
    return {'viewer_id': viewer_id, 'direction': normalized, 'status': status}


async def set_viewer_structure_visibility(
    viewer_id: str,
    visibility: list[bool],
    window_id: str | None = None,
) -> dict[str, Any]:
    """Apply `visibility` flags to the viewer's structures for `window_id`.

    Returns the viewer identifier, reported status, optional `window_id`, and
    the effective `visibility` payload echoed by the viewer.
    """
    flags = [bool(entry) for entry in visibility]
    payload = json.dumps(flags)
    params: dict[str, object | None] = {'viewer': viewer_id, 'visibility': payload}
    if window_id:
        params['window'] = window_id
    result = invoke_viewer_command('visibility', 'visibility', params, timeout=60.0)
    error_msg = result.get('error')
    if isinstance(error_msg, str) and error_msg:
        raise RuntimeError(f'Visibility update failed: {error_msg}')
    response: dict[str, Any] = {'viewer_id': viewer_id, 'status': result.get('status', 'ok')}
    reported_window = result.get('window_id')
    if isinstance(reported_window, str) and reported_window:
        response['window_id'] = reported_window
    returned_flags = result.get('visibility')
    if isinstance(returned_flags, list):
        response['visibility'] = [bool(entry) for entry in returned_flags]
    return response


async def check_simulation(viewer_id: str, window_id: str | None = None) -> dict[str, Any]:
    """Return warnings and errors reported by `viewer_id` within `window_id`.

    The response always includes `viewer_id` and may include `warnings`,
    `error`, `status`, and `window_id`.
    """
    params: dict[str, object | None] = {'viewer': viewer_id}
    if window_id:
        params['window'] = window_id
    result = invoke_viewer_command('check', 'check', params, timeout=60.0)
    response: dict[str, Any] = {'viewer_id': viewer_id}
    warnings = _normalize_warnings(result.get('warnings'))
    if warnings is not None:
        response['warnings'] = warnings
    error_msg = result.get('error')
    if isinstance(error_msg, str) and error_msg:
        response['error'] = error_msg
    status = result.get('status')
    if isinstance(status, str) and status:
        response['status'] = status
    reported_window = result.get('window_id')
    if isinstance(reported_window, str) and reported_window:
        response['window_id'] = reported_window
    return response
