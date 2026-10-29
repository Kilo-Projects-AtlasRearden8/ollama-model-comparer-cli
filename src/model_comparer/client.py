"""Client for OpenAI-compatible LLM endpoints (default: Ollama).

No API keys are required by default. Local-first: everything is saved to
disk and nothing is sent anywhere except the endpoint you configure.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Iterable


class LLMError(Exception):
    """Raised when the LLM endpoint cannot be reached or returns an error."""


class LLMClient:
    """Talk to an OpenAI-compatible chat completions endpoint.

    Ollama exposes this interface at http://localhost:11434/v1 by default.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        timeout: float = 60.0,
        api_key: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            url, data=body, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:  # pragma: no cover - endpoint dependent
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(
                f"endpoint returned HTTP {exc.code} for {url}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:  # pragma: no cover - endpoint dependent
            raise LLMError(f"cannot reach endpoint {url}: {exc}") from exc
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise LLMError(f"endpoint returned invalid JSON from {url}") from exc

    def chat(self, model: str, prompt: str) -> str:
        """Send a single prompt to one model and return its response text."""
        data = self._post(
            "/chat/completions",
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
        )
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(
                f"unexpected response format from {self.base_url}: {data!r}"
            ) from exc

    def list_models(self) -> list[str]:
        """Return model ids advertised by the endpoint (GET /models)."""
        url = f"{self.base_url}/models"
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:  # pragma: no cover - endpoint dependent
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(
                f"endpoint returned HTTP {exc.code} for {url}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:  # pragma: no cover - endpoint dependent
            raise LLMError(f"cannot reach endpoint {url}: {exc}") from exc
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise LLMError(f"endpoint returned invalid JSON from {url}") from exc
        return [item.get("id", "") for item in data.get("data", []) if item.get("id")]

    def compare(self, models: Iterable[str], prompt: str) -> list[dict[str, Any]]:
        """Send one prompt to several models and return one result per model."""
        results: list[dict[str, Any]] = []
        for model in models:
            result: dict[str, Any] = {"model": model, "prompt": prompt}
            try:
                result["response"] = self.chat(model, prompt)
                result["error"] = None
            except LLMError as exc:
                result["response"] = ""
                result["error"] = str(exc)
            results.append(result)
        return results
