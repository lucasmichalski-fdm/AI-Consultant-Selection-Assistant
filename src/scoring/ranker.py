"""Deterministic ranking stub for Milestone B."""

from __future__ import annotations

from datetime import datetime

from src.config import ScoreWeights
from src.models import ConsultantProfile, RankedCandidate, RoleRequirement, ScoreCard
from src.scoring.constraints import evaluate_constraints
from src.scoring.location import location_alignment_score
from src.scoring.reason_codes import build_reason_codes


def _ratio(required: list[str], observed: list[str]) -> float:
    if not required:
        return 1.0
    required_set = set(required)
    observed_set = set(observed)
    return len(required_set.intersection(observed_set)) / len(required_set)


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def _behavioral_score(role: RoleRequirement, consultant: ConsultantProfile) -> float:
    importance = role.behavioral_importance
    scores = consultant.behavioral_scores
    total_weight = sum(importance.values())
    if total_weight <= 0:
        return 0.5

    weighted = 0.0
    for key, weight in importance.items():
        weighted += weight * (scores.get(key, 0.0) / 5.0)
    return max(0.0, min(1.0, weighted / total_weight))


def _experience_score(role: RoleRequirement, consultant: ConsultantProfile) -> float:
    required = role.required_years_experience
    if required <= 0:
        return 1.0
    years = consultant.years_experience
    if years >= required:
        return 1.0
    if years >= required - 1:
        return 0.7
    if years >= required - 2:
        return 0.4
    return max(0.0, min(0.3, years / required))


def _domain_score(role: RoleRequirement, consultant: ConsultantProfile) -> float:
    direct = _ratio(role.required_domains, consultant.normalized_domains)
    if direct > 0:
        return direct

    adjacency = {
        "banking": {"fintech"},
        "fintech": {"banking"},
        "healthcare": {"insurance"},
        "insurance": {"healthcare"},
        "retail": {"logistics"},
        "logistics": {"retail"},
    }
    if not role.required_domains:
        return 1.0

    role_domains = set(role.required_domains)
    candidate_domains = set(consultant.normalized_domains)
    for role_domain in role_domains:
        if adjacency.get(role_domain, set()).intersection(candidate_domains):
            return 0.5
    return 0.0


def _availability_location_score(role: RoleRequirement, consultant: ConsultantProfile) -> float:
    availability = 0.5
    role_start = _parse_date(role.start_date)
    consultant_date = _parse_date(consultant.availability_date)
    if role_start and consultant_date:
        availability = 1.0 if consultant_date <= role_start else 0.0

    location = location_alignment_score(role, consultant)

    # Location is intentionally weighted above availability per FDM onsite policy.
    score = (0.3 * availability) + (0.7 * location)
    return max(0.0, min(1.0, score))


def _prior_rating_score(consultant: ConsultantProfile) -> float:
    if consultant.previous_client_rating is None:
        return 0.5
    return max(0.0, min(1.0, consultant.previous_client_rating / 5.0))


def _score_components(role: RoleRequirement, consultant: ConsultantProfile) -> ScoreCard:
    required_bundle = role.required_certs + role.required_tools

    return ScoreCard(
        required_skills=_ratio(role.required_skills, consultant.normalized_skills),
        required_certs_tools=_ratio(required_bundle, consultant.normalized_certs + consultant.normalized_tools),
        domain=_domain_score(role, consultant),
        preferred_skills=_ratio(role.preferred_skills, consultant.normalized_skills),
        experience=_experience_score(role, consultant),
        behavioral=_behavioral_score(role, consultant),
        availability_location=_availability_location_score(role, consultant),
        prior_rating=_prior_rating_score(consultant),
    )


def _weighted_score(card: ScoreCard, weights: ScoreWeights) -> float:
    return (
        card.required_skills * weights.required_skills
        + card.required_certs_tools * weights.required_certs_tools
        + card.domain * weights.domain
        + card.preferred_skills * weights.preferred_skills
        + card.experience * weights.experience
        + card.behavioral * weights.behavioral
        + card.availability_location * weights.availability_location
        + card.prior_rating * weights.prior_rating
    )


def rank_candidates(role: RoleRequirement, consultants: list[ConsultantProfile], weights: ScoreWeights) -> list[RankedCandidate]:
    """Rank candidates deterministically using weighted score components."""

    scored: list[tuple[RankedCandidate, ScoreCard, int, str]] = []
    for consultant in consultants:
        passes, violations = evaluate_constraints(role, consultant)
        card = _score_components(role, consultant)
        raw_score = _weighted_score(card, weights)

        # Guardrail: do not allow low must-have coverage near the top.
        if card.required_skills < 0.60:
            raw_score = min(raw_score, 40.0)

        if not passes:
            raw_score = min(raw_score, 5.0)

        reasons = build_reason_codes(role, consultant, card, violations)

        ranked = RankedCandidate(
            rank=0,
            consultant_id=consultant.consultant_id,
            fit_score=round(raw_score, 2),
            score_components={
                "required_skills": round(card.required_skills, 4),
                "required_certs_tools": round(card.required_certs_tools, 4),
                "domain": round(card.domain, 4),
                "preferred_skills": round(card.preferred_skills, 4),
                "experience": round(card.experience, 4),
                "behavioral": round(card.behavioral, 4),
                "availability_location": round(card.availability_location, 4),
                "prior_rating": round(card.prior_rating, 4),
            },
            reason_codes=reasons,
            risk_flags=violations,
        )

        availability_sort_key = consultant.availability_date or "9999-12-31"
        scored.append((ranked, card, len(violations), availability_sort_key))

    scored.sort(
        key=lambda item: (
            -item[0].fit_score,
            -item[1].required_skills,
            item[2],
            -item[1].required_certs_tools,
            item[3],
            item[0].consultant_id,
        )
    )

    ordered: list[RankedCandidate] = []
    for idx, (ranked, _, _, _) in enumerate(scored, start=1):
        ranked.rank = idx
        ordered.append(ranked)
    return ordered
