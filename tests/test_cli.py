"""Tests for the CLI against a mocked client."""

from __future__ import annotations

from model_comparer import cli


class FakeClient:
    def __init__(self, base_url: str, timeout: float, api_key: str | None = None) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def compare(self, models, prompt):
        return [
            {"model": "m1", "prompt": prompt, "response": "alpha beta gamma", "error": None},
            {"model": "m2", "prompt": prompt, "response": "alpha delta", "error": None},
        ]

    def list_models(self):
        return ["m1", "m2"]


def test_cli_runs_and_scores(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "LLMClient", FakeClient)
    out_dir = tmp_path / "responses"
    code = cli.run(
        ["--prompt", "hello", "--models", "m1", "m2", "--endpoint", "http://x/v1", "--out-dir", str(out_dir)]
    )
    assert code == 0
    captured = capsys.readouterr().out
    assert "m1" in captured and "m2" in captured
    assert "Pairwise difference scores" in captured
    files = list(out_dir.iterdir())
    assert len(files) == 3  # two responses + one summary
    summary = [f for f in files if f.name.endswith("-summary.json")][0]
    import json

    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["prompt"] == "hello"
    assert data["models"] == ["m1", "m2"]


def test_cli_list_models(monkeypatch, capsys):
    monkeypatch.setattr(cli, "LLMClient", FakeClient)
    code = cli.run(["--list-models", "--endpoint", "http://x/v1"])
    assert code == 0
    captured = capsys.readouterr().out
    assert "Models available at endpoint:" in captured
    assert "m1" in captured and "m2" in captured
