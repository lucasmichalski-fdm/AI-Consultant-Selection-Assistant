"""Reason code generation stub."""

from __future__ import annotations

from src.models import ConsultantProfile, RoleRequirement, ScoreCard


def build_reason_codes(
    role: RoleRequirement,
    consultant: ConsultantProfile,
    score_card: ScoreCard,
    violations: list[str] | None = None,
) -> list[str]:
    """Generate compact reason codes for ranking output."""

    reasons: list[str] = []

    required_skill_matches = set(role.required_skills).intersection(consultant.normalized_skills)
    missing_required_skills = sorted(set(role.required_skills).difference(consultant.normalized_skills))

    if score_card.required_skills >= 0.8:
        reasons.append("REQ_SKILLS_STRONG")
    elif score_card.required_skills < 0.6:
        reasons.append("REQ_SKILLS_WEAK")

    for skill in missing_required_skills[:2]:
        reasons.append(f"GAP_REQUIRED_SKILL_{skill.upper().replace('.', '').replace('/', '_').replace('-', '_')}")

    if score_card.required_certs_tools >= 0.8:
        reasons.append("REQ_CERT_TOOLS_STRONG")

    missing_certs = sorted(set(role.required_certs).difference(consultant.normalized_certs))
    if missing_certs:
        reasons.append("GAP_REQUIRED_CERT")

    if score_card.domain >= 0.8:
        reasons.append("DOMAIN_STRONG_FIT")
    elif score_card.domain > 0:
        reasons.append("DOMAIN_PARTIAL_FIT")

    if role.required_years_experience > 0 and consultant.years_experience + 1 < role.required_years_experience:
        reasons.append("EXP_BELOW_TARGET")
    elif consultant.years_experience >= role.required_years_experience:
        reasons.append("EXP_MEETS_TARGET")

    has_location_violation = bool(violations and "CONSTRAINT_FAIL_LOCATION" in violations)
    if not has_location_violation and score_card.availability_location >= 0.8:
        reasons.append("LOCATION_LOGISTICS_STRONG")
    elif score_card.availability_location < 0.4:
        reasons.append("LOCATION_LOGISTICS_WEAK")

    if not has_location_violation and consultant.location_state != role.location_state and consultant.willing_to_relocate:
        reasons.append("LOCATION_RELOCATION_PATH")

    if required_skill_matches and not missing_required_skills:
        reasons.append("MUST_HAVE_COVERAGE_COMPLETE")

    if violations:
        reasons.extend(violations)

    if not reasons:
        reasons.append("PROFILE_REVIEW_REQUIRED")

    return reasons
