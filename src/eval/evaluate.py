"""Evaluation runner stub for later milestones."""

from __future__ import annotations


def evaluate_batch() -> dict[str, float]:
    """Placeholder batch metrics."""

    return {
        "runs": 0,
        "top5_generated_rate": 0.0,
        "citation_coverage_rate": 0.0,
    }
