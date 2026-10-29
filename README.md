# compare-cli

Local-first CLI for comparing local LLM models side by side. Send one prompt to
multiple models through any OpenAI-compatible endpoint (default: Ollama),
save the responses to disk, and score how different they are — no API keys
required.

Built and maintained by [Asdale Dynamics, LLC](https://dylanasdale.github.io)
(Dylan Asdale, Indiana). Plain English, step by step, never condescending —
built for anyone getting started with local AI.

## What it does

- Sends the same prompt to several models at once
- Saves every response locally as a timestamped text file
- Writes a machine-readable summary JSON with per-model errors and pairwise
  difference scores
- Prints a readable comparison table to the terminal
- Works offline against your own endpoint (Ollama runs entirely on your
  machine)

## Install

```bash
git clone <this-repo>
cd ollama-model-comparer-cli
pip install .
```

This installs the `compare-cli` command. No runtime dependencies beyond
Python 3.9+ (the standard library only).

## Usage

Make sure your endpoint is running (Ollama by default on
`http://localhost:11434/v1`) and that the models you want are pulled:

```bash
ollama pull llama3.2
ollama pull mistral
```

Compare two models:

```bash
compare-cli --prompt "Explain AI like I'm ten" \
  --models llama3.2 mistral \
  --out-dir responses/
```

Sample output:

```
Model comparison results
=========================

Model        Chars  Words  Status
--------------------------------
llama3.2       142     24  ok
mistral        128     22  ok

Pairwise difference scores (0 = same words, 1 = no overlap):
              llama3.2     mistral
llama3.2      0.000        0.316
mistral       0.316        0.000

Saved 2 response(s) to responses/
Summary written to responses/20261029-093000-summary.json
```

Options:

- `--prompt` — prompt to send to every model (required)
- `--models` — model names, space-separated (required)
- `--endpoint` — OpenAI-compatible base URL
  (default: `http://localhost:11434/v1`, i.e. Ollama)
- `--out-dir` — where responses and summaries are saved
  (default: `responses/`)
- `--timeout` — request timeout in seconds (default: 60)

You can also run without installing:

```bash
python -m model_comparer --prompt "..." --models model1 model2
```

## Local-first by design

- Nothing is saved to the cloud. Responses live only in `--out-dir` on your
  machine.
- No API keys, no secrets, no registration. Ollama and other local endpoints
  don't require keys.
- Configure `--endpoint` to point at any OpenAI-compatible server (LLama.cpp,
  vLLM, Ollama, etc.).

## Tests

```bash
pytest
```

Tests use a mock endpoint on localhost, so no network or real models are
needed.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC (Indiana, formed October 2026) is founded by Dylan
Asdale, a registered nurse turned AI author. His book *The Massive AI Manual*
and hub site dylanasdale.github.io explain AI "like a friend would": plain
English, step by step, never condescending. The LLC publishes beginner-friendly
AI education, books and guides, and practical open-source tools like this one.
