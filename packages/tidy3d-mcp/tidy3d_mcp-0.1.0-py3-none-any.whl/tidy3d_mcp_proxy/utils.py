from __future__ import annotations

from collections.abc import Callable
import json
import os
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import url2pathname


class CallbackSession:
    """Context manager for a single JSON callback."""

    def __init__(
        self,
        server: ThreadingHTTPServer,
        thread: threading.Thread,
        event: threading.Event,
        on_json: Callable[[dict[str, Any]], None] | None,
    ):
        self._server = server
        self._thread = thread
        self._event = event
        self._on_json = on_json
        self._payload: dict[str, Any] | None = None
        self._lock = threading.Lock()
        self._closed = False
        self._started = False

    def wait(self, timeout: float | None = None) -> bool:
        """Block until the callback arrives or the timeout elapses."""
        return self._event.wait(timeout)

    @property
    def payload(self) -> dict[str, Any] | None:
        """Return the JSON payload captured from the callback."""
        return self._payload

    def close(self):
        """Stop the server thread and release resources."""
        if self._closed:
            return
        self._closed = True
        if self._started:
            try:
                self._server.shutdown()
            except Exception:
                pass
            self._thread.join(timeout=1.0)
        self._server.server_close()
        self._event.set()

    def __enter__(self) -> CallbackSession:
        if not self._started:
            self._thread.start()
            self._started = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _handle_payload(self, payload: dict[str, Any]):
        with self._lock:
            self._payload = payload
        try:
            if self._on_json:
                self._on_json(payload)
        finally:
            self._event.set()

    def _request_shutdown(self):
        if self._closed or not self._started:
            return
        try:
            self._server.shutdown()
        except Exception:
            pass


def open_uri(uri: str) -> bool:
    """Launch a platform handler for a URI and report success."""
    if not uri:
        raise ValueError('empty uri')
    try:
        if sys.platform.startswith('darwin'):
            result = subprocess.run(
                ['open', uri],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        if sys.platform.startswith('win'):
            result = subprocess.run(
                ['cmd', '/c', 'start', '', uri],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        result = subprocess.run(
            ['xdg-open', uri],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except OSError:
        return False


def find_free_port() -> int:
    """Allocate an ephemeral localhost port for callbacks."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def serve_once(
    port: int,
    path: str,
    on_json: Callable[[dict[str, Any]], None] | None = None,
) -> CallbackSession:
    """Return a `CallbackSession` that stops after one JSON POST to `path`."""
    event = threading.Event()
    session: CallbackSession | None = None

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, fmt: str, *args: object):
            return

        def _cors(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        def do_options(self):
            if self.path != path:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_post(self):
            if self.path != path:
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get('content-length', '0'))
            raw_body = self.rfile.read(length) if length else b''
            try:
                text = raw_body.decode('utf-8')
            except UnicodeDecodeError:
                text = ''
            try:
                payload = json.loads(text) if text else {}
            except json.JSONDecodeError:
                payload = {}
            status = 200
            body = b'{}'
            try:
                assert session is not None
                session._handle_payload(payload)
            except Exception:
                status = 500
                body = b''
            self.send_response(status)
            self._cors()
            if status == 200:
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
            else:
                self.send_header('Content-Length', '0')
            self.end_headers()
            if status == 200 and body:
                self.wfile.write(body)
            assert session is not None
            session._request_shutdown()

        do_OPTIONS = do_options
        do_POST = do_post

    httpd = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    httpd.daemon_threads = True
    httpd.timeout = 0.5
    httpd.allow_reuse_address = True
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    session = CallbackSession(httpd, thread, event, on_json)
    return session


def default_screenshots_root() -> str:
    """Return the default screenshot directory as a file URI."""
    base = Path(os.getcwd()).resolve() / '.tidy3d-screenshots'
    return base.as_uri()


def ensure_file_uri(path: str | None) -> str:
    """Normalize input into a file URI, falling back to the default root."""
    if not path:
        return default_screenshots_root()
    if path.startswith('file://'):
        return path
    return Path(path).expanduser().resolve().as_uri()


def uri_to_path(uri: str) -> str:
    """Convert a file URI into a local filesystem path."""
    parsed = urlparse(uri)
    if parsed.scheme == 'file':
        combined = (parsed.netloc or '') + parsed.path
        return url2pathname(combined)
    return uri
