"""Score differences between model responses.

Pure functions over plain text; no external services, no secrets.
"""

from __future__ import annotations

import re
from typing import Iterable

_WORD_RE = re.compile(r"[a-z0-9]+", re.UNICODE)


def words(text: str) -> set[str]:
    """Return the set of lowercase word tokens in ``text``."""
    return set(_WORD_RE.findall(text.lower()))


def jaccard(a: str, b: str) -> float:
    """Jaccard similarity of the word sets of ``a`` and ``b`` (0..1)."""
    set_a, set_b = words(a), words(b)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def difference_score(a: str, b: str) -> float:
    """Difference between two responses (0 = identical words, 1 = no overlap)."""
    return 1.0 - jaccard(a, b)


def length_score(a: str, b: str) -> float:
    """Relative length difference between two responses (0..1)."""
    len_a, len_b = len(a), len(b)
    if len_a == 0 and len_b == 0:
        return 0.0
    if len_a == 0 or len_b == 0:
        return 1.0
    return abs(len_a - len_b) / max(len_a, len_b)


def pairwise_scores(responses: dict[str, str]) -> dict[str, dict[str, float]]:
    """Difference and length scores for every ordered pair of models."""
    models = list(responses)
    matrix: dict[str, dict[str, float]] = {}
    for first in models:
        row: dict[str, float] = {}
        for second in models:
            if first == second:
                row[second] = 0.0
            else:
                row[second] = round(
                    difference_score(responses[first], responses[second]), 3
                )
        matrix[first] = row
    return matrix
