"""Tests for local response storage."""

from __future__ import annotations

import json
from pathlib import Path

from model_comparer.storage import save_response, save_summary, slugify


def test_slugify() -> None:
    assert slugify("Llama 3.2") == "llama-3-2"
    assert slugify("   ") == "model"


def test_save_response_creates_file(tmp_path) -> None:
    path = save_response(tmp_path, "Llama 3.2", "hello world")
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "hello world"
    assert "llama-3-2" in path.name


def test_save_summary(tmp_path) -> None:
    results = [
        {"model": "m1", "prompt": "p", "response": "one", "error": None},
        {"model": "m2", "prompt": "p", "response": "", "error": "boom"},
    ]
    scores = {"m1": {"m2": 0.5}, "m2": {"m1": 0.5}}
    path = save_summary(tmp_path, "p", results, scores)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["prompt"] == "p"
    assert data["errors"] == {"m2": "boom"}
    assert data["scores"] == scores
