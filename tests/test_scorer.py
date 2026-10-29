"""Tests for the response scoring functions."""

from __future__ import annotations

from model_comparer.scorer import difference_score, jaccard, length_score, pairwise_scores


def test_jaccard_identical_texts() -> None:
    assert jaccard("hello world", "world hello") == 1.0


def test_jaccard_no_overlap() -> None:
    assert jaccard("hello world", "goodbye moon") == 0.0


def test_jaccard_partial_overlap() -> None:
    assert jaccard("a b c", "b c d") == 2 / 4


def test_jaccard_empty_both() -> None:
    assert jaccard("", "") == 1.0


def test_difference_score_complement() -> None:
    assert difference_score("a b c", "b c d") == 1 - 2 / 4


def test_length_score() -> None:
    assert length_score("hi", "hello there") > 0
    assert length_score("same", "same") == 0.0


def test_pairwise_scores() -> None:
    responses = {"m1": "apple banana", "m2": "banana cherry", "m3": "apple banana"}
    matrix = pairwise_scores(responses)
    assert matrix["m1"]["m2"] > 0
    assert matrix["m1"]["m3"] == 0.0
    assert all(matrix[m][m] == 0.0 for m in responses)
