"""Reason code generation stub."""

from __future__ import annotations

from src.models import ConsultantProfile, RoleRequirement, ScoreCard
from src.scoring.constraints import evaluate_mandatory_context_evidence
from src.scoring.evidence import find_potential_unconfirmed_terms, match_terms_from_structured_and_text


def _sanitize_reason_token(value: str) -> str:
    return value.upper().replace('.', '').replace('/', '_').replace('-', '_').replace(' ', '_')


def build_reason_codes(
    role: RoleRequirement,
    consultant: ConsultantProfile,
    score_card: ScoreCard,
    violations: list[str] | None = None,
) -> list[str]:
    """Generate compact reason codes for ranking output."""

    reasons: list[str] = []

    required_skill_matches = match_terms_from_structured_and_text(
        role.required_skills,
        consultant.normalized_skills,
        consultant,
    )
    missing_required_skills = sorted(set(role.required_skills).difference(required_skill_matches))

    if score_card.required_skills >= 0.8:
        reasons.append("REQ_SKILLS_STRONG")
    elif score_card.required_skills < 0.6:
        reasons.append("REQ_SKILLS_WEAK")

    for skill in missing_required_skills[:2]:
        reasons.append(f"GAP_REQUIRED_SKILL_{_sanitize_reason_token(skill)}")

    potential_skill_terms = find_potential_unconfirmed_terms(
        role.required_skills,
        consultant.normalized_skills,
        consultant,
    )
    for skill in missing_required_skills[:2]:
        if skill in potential_skill_terms:
            reasons.append(f"REVIEW_POTENTIAL_SKILL_{_sanitize_reason_token(skill)}")

    matched_required_tools = match_terms_from_structured_and_text(
        role.required_tools,
        consultant.normalized_tools,
        consultant,
    )
    missing_tools = sorted(set(role.required_tools).difference(matched_required_tools))

    potential_tool_terms = find_potential_unconfirmed_terms(
        role.required_tools,
        consultant.normalized_tools,
        consultant,
    )
    for tool in missing_tools[:2]:
        if tool in potential_tool_terms:
            reasons.append(f"REVIEW_POTENTIAL_TOOL_{_sanitize_reason_token(tool)}")

    if score_card.required_certs_tools >= 0.8:
        reasons.append("REQ_CERT_TOOLS_STRONG")

    matched_required_certs = match_terms_from_structured_and_text(
        role.required_certs,
        consultant.normalized_certs,
        consultant,
    )
    missing_certs = sorted(set(role.required_certs).difference(matched_required_certs))
    if missing_certs:
        reasons.append("GAP_REQUIRED_CERT")

    potential_cert_terms = find_potential_unconfirmed_terms(
        role.required_certs,
        consultant.normalized_certs,
        consultant,
    )
    for cert in missing_certs[:2]:
        if cert in potential_cert_terms:
            reasons.append(f"REVIEW_POTENTIAL_CERT_{_sanitize_reason_token(cert)}")

    if score_card.domain >= 0.8:
        reasons.append("DOMAIN_STRONG_FIT")
    elif score_card.domain > 0:
        reasons.append("DOMAIN_PARTIAL_FIT")

    if role.required_years_experience > 0 and consultant.years_experience + 1 < role.required_years_experience:
        reasons.append("EXP_BELOW_TARGET")
    elif consultant.years_experience >= role.required_years_experience:
        reasons.append("EXP_MEETS_TARGET")

    has_location_violation = bool(violations and "CONSTRAINT_FAIL_LOCATION" in violations)
    if not has_location_violation:
        if score_card.availability_location >= 0.8:
            reasons.append("LOCATION_LOGISTICS_STRONG")
        elif score_card.availability_location < 0.4:
            reasons.append("LOCATION_LOGISTICS_WEAK")

    if not has_location_violation and consultant.location_state != role.location_state and consultant.willing_to_relocate:
        reasons.append("LOCATION_RELOCATION_PATH")

    if required_skill_matches and not missing_required_skills:
        reasons.append("REQUIRED_SKILLS_COVERAGE_COMPLETE")

    mandatory_status, _mandatory_matches, required_targets = evaluate_mandatory_context_evidence(role, consultant)
    if required_targets:
        if mandatory_status == "explicit":
            reasons.append("MANDATORY_CONTEXT_EXPLICIT_MATCH")
        elif mandatory_status == "proxy":
            reasons.append("MANDATORY_CONTEXT_PLAUSIBLE_UNVERIFIED")
            reasons.append("REVIEW_MANDATORY_CONTEXT_UNVERIFIED")
        else:
            reasons.append("MANDATORY_CONTEXT_LOW_EVIDENCE")

    if not violations:
        reasons.append("MANDATORY_CONSTRAINTS_PASSED")

    if not reasons:
        reasons.append("PROFILE_REVIEW_REQUIRED")

    return reasons
