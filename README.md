# compare-cli

A local-first command-line tool that lets you compare local LLM models side by
side. Send the same prompt to several models through an OpenAI-compatible
endpoint (Ollama by default), save every response to your computer, and see a
clear score of how different the answers are.

No API keys. No accounts. Nothing leaves your machine unless you choose to send
it there.

Built and maintained by [Asdale Dynamics, LLC](https://dylanasdale.github.io)
(Dylan Asdale, Indiana) — plain English, step by step, never condescending.

## What it does

Imagine you've got a few local models running (say `llama3.2` and `mistral`)
and you want to see which one answers a question better. `compare-cli` helps
you do that:

1. You type one prompt.
2. The tool sends that same prompt to each model you name.
3. Every model's answer is saved as a file on your computer.
4. The tool prints a table showing each answer's length and a score showing how
   much the answers differ from one another (0 = same words, 1 = totally
   different words).
5. A summary file is saved too, so you can look back later.

It works against Ollama out of the box, but you can point it at any
OpenAI-compatible endpoint (LLama.cpp, vLLM, and others).

## Who this is for

This tool is made for anyone getting started with local AI — no background in
coding or machine learning required. It's published by Asdale Dynamics, LLC,
which makes beginner-friendly AI education, books, guides, and practical tools.

## Install

You need Python 3.9 or newer. No extra libraries are required — everything
comes with Python.

```bash
git clone <this-repo>
cd ollama-model-comparer-cli
pip install -e .
```

This installs the `compare-cli` command so you can run it from anywhere.

> **Tip:** On some systems (including recent Ubuntu), `pip install` refuses to
> modify the system Python. If you see an error about "externally managed
> environment," try one of these instead:
> - `pip install -e . --break-system-packages` (if you're comfortable with that)
> - `python3 -m venv .venv && source .venv/bin/activate && pip install -e .`
> - `pipx install .` (if you have pipx installed)

## Get ready (Ollama)

`compare-cli` talks to an endpoint that's already running. If you use Ollama,
make sure it's running and pull the models you want to compare:

```bash
ollama serve        # start Ollama (if it isn't already running)
ollama pull llama3.2
ollama pull mistral
```

Not sure which models you have? Ask the endpoint:

```bash
compare-cli --list-models
```

That prints every model the endpoint knows about, so you can copy the names
straight into your comparison.

## Run a comparison

Compare two models:

```bash
compare-cli --prompt "Explain AI like I'm ten" \
  --models llama3.2 mistral \
  --out-dir responses/
```

You'll see something like this:

```
Model comparison results
=========================

Model     Chars  Words  Status
------------------------------
llama3.2    142     24  ok
mistral     128     22  ok

Pairwise difference scores (0 = same words, 1 = no overlap):
          llama3.2   mistral
llama3.2     0.000    0.316
mistral      0.316    0.000

Saved 2 response(s) to responses/
Summary written to responses/20261029-093000-summary.json
```

- **Chars / Words**: how long each answer is.
- **Status**: `ok` means the model answered; `error` means it couldn't.
- **Difference scores**: a lower number means the two models used more of the
  same words; a higher number means their answers were more different.

Each model's full answer is saved as its own timestamped text file, and a
`summary.json` file records the prompt, the models, any errors, and the scores.

## All the options

| Option | What it does | Default |
|--------|--------------|---------|
| `--prompt` | The prompt to send to every model (required) | — |
| `--models` | Model names to compare, separated by spaces (required) | — |
| `--endpoint` | The OpenAI-compatible base URL to talk to | `http://localhost:11434/v1` (Ollama) |
| `--out-dir` | Folder where responses and the summary are saved | `responses/` |
| `--timeout` | How many seconds to wait for each answer | `60` |
| `--list-models` | Print the models the endpoint knows about, then stop | — |

You can also run without installing:

```bash
python -m model_comparer --prompt "..." --models model1 model2
```

## Local-first by design

- Nothing is uploaded to the cloud. Responses and summaries are saved only to
  `--out-dir` on your own computer.
- No API keys, no secrets, no registration. Local endpoints like Ollama don't
  use keys.
- Change `--endpoint` to point at any OpenAI-compatible server running on your
  machine or network.

## Tests

```bash
pytest
```

The tests spin up a fake endpoint on your computer, so no network connection or
real models are needed.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC (Indiana, formed October 2026) is founded by Dylan
Asdale, a registered nurse turned AI author. His book *The Massive AI Manual*
and hub site dylanasdale.github.io explain AI "like a friend would": plain
English, step by step, never condescending. The LLC publishes beginner-friendly
AI education, books and guides, and practical open-source tools like this one.
