"""Tests for the LLM client against a mock endpoint."""

from __future__ import annotations

import pytest

from model_comparer.client import LLMClient, LLMError

ERROR_MODEL = "failing-model"


def test_chat_returns_response(mock_endpoint: str) -> None:
    client = LLMClient(base_url=mock_endpoint)
    text = client.chat("llama3.2", "Why is the sky blue?")
    assert "scatter" in text.lower()
    assert "blue" in text.lower()


def test_chat_uses_correct_model(mock_endpoint: str) -> None:
    client = LLMClient(base_url=mock_endpoint)
    assert client.chat("mistral", "x") != client.chat("codellama", "x")


def test_list_models(mock_endpoint: str) -> None:
    client = LLMClient(base_url=mock_endpoint)
    models = client.list_models()
    assert "llama3.2" in models
    assert "mistral" in models
    assert "codellama" in models


def test_compare_sends_one_prompt_to_many_models(mock_endpoint: str) -> None:
    client = LLMClient(base_url=mock_endpoint)
    results = client.compare(["llama3.2", "mistral"], "Why is the sky blue?")
    assert [r["model"] for r in results] == ["llama3.2", "mistral"]
    assert all(r["prompt"] == "Why is the sky blue?" for r in results)
    assert all(r["error"] is None for r in results)


def test_error_model_is_recorded(mock_endpoint: str) -> None:
    client = LLMClient(base_url=mock_endpoint)
    # chat() raises on error; compare() catches and records
    with pytest.raises(LLMError):
        client.chat(ERROR_MODEL, "anything")
    results = client.compare([ERROR_MODEL, "llama3.2"], "anything")
    failing = [r for r in results if r["model"] == ERROR_MODEL][0]
    assert failing["error"] is not None
    assert failing["response"] == ""
    working = [r for r in results if r["model"] == "llama3.2"][0]
    assert working["error"] is None


def test_chat_raises_on_endpoint_error(mock_endpoint: str) -> None:
    client = LLMClient(base_url=mock_endpoint)
    with pytest.raises(LLMError):
        client.chat(ERROR_MODEL, "anything")


def test_default_endpoint_is_ollama() -> None:
    client = LLMClient()
    assert client.base_url == "http://localhost:11434/v1"
