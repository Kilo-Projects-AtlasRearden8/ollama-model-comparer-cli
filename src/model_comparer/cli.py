"""Command line interface for model comparison."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, Sequence

from .client import LLMClient, LLMError
from .scorer import difference_score, length_score, pairwise_scores
from .storage import save_response, save_summary

DEFAULT_ENDPOINT = "http://localhost:11434/v1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compare-cli",
        description=(
            "Send one prompt to several local LLM models through an "
            "OpenAI-compatible endpoint (default Ollama), save responses, "
            "and score their differences."
        ),
    )
    parser.add_argument(
        "--prompt",
        help="Prompt to send to every model.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        help="Model names to compare (space-separated).",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help=f"OpenAI-compatible base URL (default: {DEFAULT_ENDPOINT}).",
    )
    parser.add_argument(
        "--out-dir",
        default="responses",
        help="Directory where responses and summaries are saved (default: responses).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Request timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List models advertised by the endpoint and exit.",
    )
    return parser


def format_table(results: Sequence[dict], scores: dict[str, dict[str, float]]) -> str:
    """Build a human-readable comparison table."""
    lines = [
        "Model comparison results",
        "=========================",
        "",
    ]
    widths = {
        "model": max([len(str(r.get("model", ""))) for r in results] + [5]),
        "chars": max([len(str(len(r.get("response", "")))) for r in results] + [4]),
        "words": max([len(str(len(r.get("response", "").split()))) for r in results] + [5]),
    }
    header = (
        f"{'Model':<{widths['model']}}  "
        f"{'Chars':>{widths['chars']}}  "
        f"{'Words':>{widths['words']}}  "
        f"{'Status':<8}"
    )
    lines.append(header)
    lines.append("-" * len(header))
    for result in results:
        model = str(result.get("model", ""))
        response = str(result.get("response", ""))
        status = "error" if result.get("error") else "ok"
        lines.append(
            f"{model:<{widths['model']}}  "
            f"{len(response):>{widths['chars']}}  "
            f"{len(response.split()):>{widths['words']}}  "
            f"{status:<8}"
        )
    if scores:
        lines.append("")
        lines.append("Pairwise difference scores (0 = same words, 1 = no overlap):")
        models = list(scores)
        head = " " * (widths["model"] + 2) + "  ".join(
            f"{m:>{widths['model']}}" for m in models
        )
        lines.append(head)
        for first in models:
            row = " ".join(
                f"{scores[first].get(second, 0.0):>{widths['model']}.3f}"
                for second in models
            )
            lines.append(f"{first:<{widths['model']}}  {row}")
    lines.append("")
    return "\n".join(lines)


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    client = LLMClient(base_url=args.endpoint, timeout=args.timeout)

    if args.list_models:
        try:
            models = client.list_models()
        except LLMError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if not models:
            print("No models found at endpoint.", file=sys.stderr)
            return 1
        print("Models available at endpoint:")
        for model in models:
            print(f"  - {model}")
        return 0

    if not args.prompt or not args.models:
        parser.error("--prompt and --models are required unless --list-models is used.")

    try:
        results = client.compare(args.models, args.prompt)
    except LLMError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    responses = {r["model"]: r.get("response", "") for r in results}
    scores = pairwise_scores(responses)

    print(format_table(results, scores))

    try:
        saved = [save_response(args.out_dir, r["model"], str(r.get("response", ""))) for r in results]
        summary_path = save_summary(args.out_dir, args.prompt, results, scores)
    except OSError as exc:
        print(f"warning: could not save responses: {exc}", file=sys.stderr)
        saved = []
        summary_path = None

    if saved:
        print(f"Saved {len(saved)} response(s) to {args.out_dir}/")
        if summary_path is not None:
            print(f"Summary written to {summary_path}")
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
