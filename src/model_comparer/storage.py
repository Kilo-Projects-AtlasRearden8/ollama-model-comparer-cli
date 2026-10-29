"""Local persistence for comparison responses."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    """Turn a model name into a filesystem-safe slug."""
    return _SLUG_RE.sub("-", name.strip().lower()).strip("-") or "model"


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def save_response(out_dir: str | Path, model: str, response: str) -> Path:
    """Write one model response to a timestamped file. Returns the file path."""
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    safe = slugify(model)
    path = directory / f"{timestamp()}-{safe}.txt"
    path.write_text(response, encoding="utf-8")
    return path


def save_summary(
    out_dir: str | Path,
    prompt: str,
    results: list[dict[str, Any]],
    scores: dict[str, dict[str, float]],
) -> Path:
    """Write a machine-readable summary JSON. Returns the file path."""
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{timestamp()}-summary.json"
    payload = {
        "prompt": prompt,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "models": [result.get("model") for result in results],
        "errors": {
            result["model"]: result["error"]
            for result in results
            if result.get("error")
        },
        "scores": scores,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
