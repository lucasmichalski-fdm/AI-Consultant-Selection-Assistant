"""Rank comparison agent interfaces and starter deterministic explainer."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.agents.deterministic_scoring_agent import DeterministicEvaluation


@dataclass
class RankComparison:
    """Pairwise rank explanation output."""

    higher_consultant_id: str
    lower_consultant_id: str
    narrative: str
    evidence_lines: list[str] = field(default_factory=list)


class RankComparisonAgent:
    """Interface for explaining deterministic rank outcomes."""

    def compare(
        self,
        evaluations: list[DeterministicEvaluation],
    ) -> list[RankComparison]:
        raise NotImplementedError


class DeterministicRankComparisonAgent(RankComparisonAgent):
    """Starter rank explainer based on component deltas."""

    def compare(
        self,
        evaluations: list[DeterministicEvaluation],
    ) -> list[RankComparison]:
        if len(evaluations) < 2:
            return []

        comparisons: list[RankComparison] = []
        for idx in range(len(evaluations) - 1):
            higher_eval = evaluations[idx]
            lower_eval = evaluations[idx + 1]
            higher = higher_eval.ranked_candidate
            lower = lower_eval.ranked_candidate

            higher_req = higher.score_components.get("required_skills", 0.0)
            lower_req = lower.score_components.get("required_skills", 0.0)
            req_delta = round(higher_req - lower_req, 4)

            fit_delta = round(higher.fit_score - lower.fit_score, 2)
            evidence = [
                f"fit_score_delta={fit_delta}",
                f"required_skills_delta={req_delta}",
                f"higher_risk_flags={len(higher.risk_flags)}",
                f"lower_risk_flags={len(lower.risk_flags)}",
            ]

            if fit_delta >= 0:
                narrative = (
                    f"{higher.consultant_id} ranks above {lower.consultant_id} "
                    f"with stronger deterministic fit ({higher.fit_score} vs {lower.fit_score})."
                )
            else:
                narrative = (
                    f"{higher.consultant_id} ranks above {lower.consultant_id} "
                    "because eligibility and risk ordering outweighed raw fit score."
                )

            comparisons.append(
                RankComparison(
                    higher_consultant_id=higher.consultant_id,
                    lower_consultant_id=lower.consultant_id,
                    narrative=narrative,
                    evidence_lines=evidence,
                )
            )
        return comparisons
