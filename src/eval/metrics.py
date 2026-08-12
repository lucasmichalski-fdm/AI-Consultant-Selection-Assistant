"""Metrics utility stubs."""

from __future__ import annotations


def safe_rate(numerator: int, denominator: int) -> float:
    """Avoid division-by-zero in metric calculations."""

    if denominator <= 0:
        return 0.0
    return numerator / denominator
