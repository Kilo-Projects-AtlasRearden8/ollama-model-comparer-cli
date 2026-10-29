"""Pytest fixtures: mock OpenAI-compatible endpoint (no keys, no network)."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from model_comparer.client import LLMClient

RESPONSES = {
    "llama3.2": "The sky appears blue because air molecules scatter short-wavelength blue light more strongly than other colors.",
    "mistral": "Blue skies happen when sunlight scatters off molecules in the atmosphere; blue light scatters the most.",
    "codellama": "def explain_blue_sky():\n    return 'Rayleigh scattering of blue light'",
}
ERROR_MODEL = "failing-model"


class _Handler(BaseHTTPRequestHandler):
    """Minimal mock of /v1/chat/completions and /v1/models."""

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        model = body.get("model", "")
        if model == ERROR_MODEL:
            payload = {"error": {"message": "model not found", "type": "invalid_request_error"}}
            self._respond(400, payload)
            return
        text = RESPONSES.get(model, f"mock response for {model}")
        self._respond(200, {"choices": [{"message": {"content": text}}]})

    def do_GET(self) -> None:
        if self.path != "/v1/models":
            self.send_error(404)
            return
        self._respond(
            200,
            {"data": [{"id": name} for name in RESPONSES]},
        )

    def _respond(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        pass  # keep test output quiet


@pytest.fixture
def mock_endpoint() -> str:
    """Start a mock endpoint on a free port and return its base URL."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        yield f"http://127.0.0.1:{port}/v1"
    finally:
        server.shutdown()
        server.server_close()
