"""Candidate retrieval stub for Milestone B."""

from __future__ import annotations

from rapidfuzz import fuzz

from src.models import ConsultantProfile, RoleRequirement


def _overlap_ratio(required: list[str], candidate: list[str]) -> float:
    if not required:
        return 1.0
    required_set = set(required)
    candidate_set = set(candidate)
    return len(required_set.intersection(candidate_set)) / len(required_set)


def _lexical_resume_score(role: RoleRequirement, consultant: ConsultantProfile) -> float:
    role_terms = " ".join(
        role.required_skills
        + role.preferred_skills
        + role.required_tools
        + role.required_domains
        + role.required_certs
    )
    resume_text = (consultant.raw.get("resume_text", "") or "").lower()
    if not role_terms or not resume_text:
        return 0.0
    return fuzz.token_set_ratio(role_terms, resume_text) / 100.0


def retrieve_candidates(role: RoleRequirement, consultants: list[ConsultantProfile], k: int = 25) -> list[ConsultantProfile]:
    """Retrieve top-k candidates using structured and lexical relevance."""

    scored: list[tuple[float, ConsultantProfile]] = []
    for consultant in consultants:
        skill_overlap = _overlap_ratio(role.required_skills, consultant.normalized_skills)
        preferred_overlap = _overlap_ratio(role.preferred_skills, consultant.normalized_skills)
        cert_overlap = _overlap_ratio(role.required_certs, consultant.normalized_certs)
        tool_overlap = _overlap_ratio(role.required_tools, consultant.normalized_tools)
        domain_overlap = _overlap_ratio(role.required_domains, consultant.normalized_domains)
        lexical = _lexical_resume_score(role, consultant)

        score = (
            0.35 * skill_overlap
            + 0.15 * preferred_overlap
            + 0.15 * cert_overlap
            + 0.10 * tool_overlap
            + 0.15 * domain_overlap
            + 0.10 * lexical
        )
        scored.append((score, consultant))

    scored.sort(key=lambda item: (item[0], item[1].consultant_id), reverse=True)
    return [consultant for _, consultant in scored[:k]]
