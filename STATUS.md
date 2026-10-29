# STATUS.md

## What was built

**compare-cli** — a local-first Python CLI to compare local LLM models side by side.

### Features

- Sends one prompt to multiple models through any OpenAI-compatible endpoint (default: Ollama at `http://localhost:11434/v1`)
- `--list-models` flag to discover which models the endpoint knows about
- Saves each response as a timestamped text file and a machine-readable JSON summary
- Scores pairwise differences between responses (Jaccard word-set difference and length ratio)
- Prints a human-readable comparison table
- Zero runtime dependencies beyond Python 3.9+ standard library
- No API keys, no network calls beyond the configured endpoint
- MIT licensed, copyright (c) 2026 Asdale Dynamics, LLC

### Project structure

```
ollama-model-comparer-cli/
├── LICENSE                    # MIT License with exact copyright line
├── README.md                  # Usage docs, credits Asdale Dynamics, LLC
├── STATUS.md                  # This file
├── pyproject.toml             # Package config, console script entry point
├── .gitignore                 # Standard Python ignores + responses/
├── src/
│   └── model_comparer/
│       ├── __init__.py
│       ├── __main__.py        # Enables `python -m model_comparer`
│       ├── cli.py             # Argument parsing, output formatting, orchestration
│       ├── client.py          # LLMClient for OpenAI-compatible endpoints
│       ├── scorer.py          # Pure scoring functions (jaccard, length, pairwise)
│       └── storage.py         # Local file persistence
└── tests/
    ├── conftest.py            # Mock HTTP endpoint (ThreadingHTTPServer)
    ├── test_cli.py            # 2 tests for CLI (compare + list-models)
    ├── test_client.py         # 7 tests for LLMClient
    ├── test_scorer.py         # 7 tests for scoring functions
    └── test_storage.py        # 2 tests for storage
```

## How to run

```bash
# Install (no runtime deps beyond stdlib)
pip install -e . --break-system-packages
# or run directly:
python -m model_comparer --prompt "..." --models model1 model2

# Example with a running Ollama:
ollama pull llama3.2
ollama pull mistral
compare-cli --prompt "Explain AI like I'm ten" --models llama3.2 mistral

# See what models are available:
compare-cli --list-models
```

### Options

| Option | Description |
|--------|-------------|
| `--prompt` | Prompt to send to every model (required unless `--list-models`) |
| `--models` | Model names, space-separated (required unless `--list-models`) |
| `--endpoint` | OpenAI-compatible base URL (default: `http://localhost:11434/v1`) |
| `--out-dir` | Output directory for responses & summaries (default: `responses/`) |
| `--timeout` | Request timeout in seconds (default: 60) |
| `--list-models` | Print the models the endpoint knows about, then exit |

## Verification results

- **Tests**: 19/19 pass (pytest with mock endpoint, no network, no keys)
  - `test_client.py`: 7 passed — chat, list_models, compare, error handling
  - `test_scorer.py`: 7 passed — jaccard, difference, length, pairwise
  - `test_storage.py`: 2 passed — slugify, save_response, save_summary
  - `test_cli.py`: 2 passed — end-to-end compare + list-models with monkeypatched client
- **CLI smoke test**: Works against mock server; `--list-models` lists models, compare writes files and prints table, exit code 0
- **Build/install**: `pip install -e .` builds and installs successfully
- **Entry points**: Both `compare-cli` (console script) and `python -m model_comparer` function
- **License**: MIT with exact line `Copyright (c) 2026 Asdale Dynamics, LLC`
- **README**: Credits Asdale Dynamics, LLC with link and description; rewritten in warm, step-by-step beginner-friendly style
- **No secrets**: Confirmed no API keys, tokens, or personal data in any file
- **No workflows**: No `.github/workflows/` files created

## Known gaps / future improvements

1. **No streaming support** — only non-streaming `/chat/completions`; streaming would allow token-by-token output for long responses.
2. **Single prompt only** — no batch/multi-prompt or conversation history support.
3. **Basic scoring** — only Jaccard word overlap and length difference; could add semantic similarity (e.g., sentence embeddings) if a local embedding model is available.
4. **No config file** — all options via CLI flags; could add `~/.compare-cli/config.toml` for defaults.
5. **No colored output** — plain text table; could use `rich` if dependencies were acceptable.
6. **Error handling** — minimal; retries, exponential backoff, or connection pooling could improve reliability against flaky local endpoints.
7. **No packaging for distribution** — only editable install tested; no `pipx` or `uv tool` install verification.
8. **Responses directory not in .gitignore by default path** — `responses/` is in .gitignore but users may choose other paths.

## License & credit

- **License**: MIT License
- **Copyright**: `Copyright (c) 2026 Asdale Dynamics, LLC`
- **Author**: Dylan Asdale, founder of Asdale Dynamics, LLC (Indiana, formed Oct 2026)
- **Project style**: Local-first, beginner-friendly, plain English, no secrets, polished, tested
