from __future__ import annotations

import json
import os
from pathlib import Path

from .utils import default_screenshots_root, uri_to_path


def screenshot_index(viewer_id: str) -> str:
    """List screenshot URIs for `viewer_id` as a formatted JSON string.

    Reads the viewer's screenshot directory, orders PNG files newest first, and
    returns a JSON document containing `viewer_id` and a `files` array of file
    URIs.
    """
    root = uri_to_path(default_screenshots_root())
    folder = os.path.join(root, viewer_id)
    try:
        files = [f for f in os.listdir(folder) if f.endswith('.png')]
        files.sort(key=lambda name: os.path.getmtime(os.path.join(folder, name)), reverse=True)
    except Exception:
        files = []
    uris: list[str] = []
    for name in files:
        try:
            uris.append((Path(folder) / name).resolve().as_uri())
        except Exception:
            continue
    return json.dumps({'viewer_id': viewer_id, 'files': uris}, indent=2)


def screenshot_file(viewer_id: str, name: str) -> bytes:
    """Load screenshot `name` for `viewer_id` and return its PNG bytes."""
    root = uri_to_path(default_screenshots_root())
    path = os.path.join(root, viewer_id, name)
    with open(path, 'rb') as f:
        return f.read()
