from __future__ import annotations

from typing import Any

from ..utils import ensure_file_uri
from ._dispatcher import invoke_viewer_command


async def capture_screenshot(
    viewer_id: str,
    dest_folder_uri: str | None = None,
    window_id: str | None = None,
) -> dict[str, Any]:
    """Capture the current frame for `viewer_id`, scoped by `window_id`.

    Saves to `dest_folder_uri` (defaulting to the shared screenshot root) and
    returns the `viewer_id` together with the absolute PNG `file_uri`. Raises
    `RuntimeError` if the viewer fails to deliver a screenshot in time.
    """
    params: dict[str, object | None] = {
        'viewer': viewer_id,
        'destFolderUri': ensure_file_uri(dest_folder_uri),
    }
    if window_id:
        params['window'] = window_id
    result = invoke_viewer_command('capture', 'shot', params, timeout=180.0)
    file_uri = result.get('file_uri')
    if not isinstance(file_uri, str) or not file_uri:
        raise RuntimeError('No screenshot was produced')
    return {'viewer_id': viewer_id, 'file_uri': file_uri}


async def clear_screenshots(
    viewer_id: str,
    dest_folder_uri: str | None = None,
    window_id: str | None = None,
) -> dict[str, Any]:
    """Remove cached screenshots for `viewer_id` under `dest_folder_uri`.

    Optionally limits the cleanup to `window_id` and returns the viewer
    identifier together with the integer `deleted_count`.
    """
    params: dict[str, object | None] = {
        'viewer': viewer_id,
        'destFolderUri': ensure_file_uri(dest_folder_uri),
    }
    if window_id:
        params['window'] = window_id
    result = invoke_viewer_command('clear', 'clear', params, timeout=120.0)
    deleted = result.get('deleted_count', 0)
    try:
        deleted_count = int(deleted)
    except (TypeError, ValueError):
        deleted_count = 0
    return {'viewer_id': viewer_id, 'deleted_count': deleted_count}
