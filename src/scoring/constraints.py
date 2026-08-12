"""Constraint evaluation stubs."""

from __future__ import annotations

from datetime import datetime
import re

from src.models import ConsultantProfile, RoleRequirement
from src.scoring.location import is_onsite_or_hybrid_role, location_compatible


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def _requires_no_sponsorship(role: RoleRequirement) -> bool:
    text = role.must_have_constraints.lower()
    return "without sponsorship" in text or "no sponsorship" in text


def _has_mandatory_language(text: str) -> bool:
    return any(token in text for token in ("mandatory", "must", "required"))


def _extract_context_targets(role: RoleRequirement) -> set[str]:
    """Extract context/domain targets implied by must-have text.

    This is intentionally generic: use role domains + client industry terms when
    must-have language suggests contextual experience requirements.
    """

    constraints = (role.must_have_constraints or "").lower()
    if not constraints or not _has_mandatory_language(constraints):
        return set()

    candidate_targets: set[str] = set()
    for domain in role.required_domains:
        if domain and domain.lower() in constraints:
            candidate_targets.add(domain.lower())

    industry = (role.raw.get("client_industry", "") or "").strip().lower()
    if industry and industry in constraints:
        candidate_targets.add(industry)

    # Optional generalized extraction for phrases like "X-regulated".
    for token in re.findall(r"([a-z]+)-regulated", constraints):
        if token:
            candidate_targets.add(token.lower())

    return candidate_targets


def evaluate_mandatory_context_evidence(role: RoleRequirement, consultant: ConsultantProfile) -> tuple[str, list[str], set[str]]:
    """Evaluate mandatory contextual evidence.

    Returns:
    - status: one of "none", "explicit", "proxy", "missing"
    - matched_targets: matched context targets
    - required_targets: required context targets inferred from constraints
    """

    required_targets = _extract_context_targets(role)
    if not required_targets:
        return "none", [], required_targets

    consultant_domains = {d.lower() for d in consultant.normalized_domains}
    searchable_text = " ".join(
        [
            (consultant.raw.get("resume_text", "") or "").lower(),
            (consultant.raw.get("project_experience_summary", "") or "").lower(),
            (consultant.raw.get("notes", "") or "").lower(),
        ]
    )

    explicit_matches: list[str] = []
    proxy_matches: list[str] = []
    for target in sorted(required_targets):
        if target in searchable_text:
            explicit_matches.append(target)
        elif target in consultant_domains:
            proxy_matches.append(target)

    if explicit_matches:
        return "explicit", explicit_matches, required_targets
    if proxy_matches:
        return "proxy", proxy_matches, required_targets
    return "missing", [], required_targets


def evaluate_constraints(role: RoleRequirement, consultant: ConsultantProfile) -> tuple[bool, list[str]]:
    """Return (passes, violations) for hard constraints."""

    violations: list[str] = []

    if role.required_years_experience > 0 and consultant.years_experience < role.required_years_experience:
        violations.append("CONSTRAINT_FAIL_EXPERIENCE_MIN")

    if _requires_no_sponsorship(role):
        auth = consultant.work_authorization_status.lower()
        if "sponsorship required" in auth and "no sponsorship required" not in auth:
            violations.append("CONSTRAINT_FAIL_AUTHORIZATION")

    if is_onsite_or_hybrid_role(role):
        if not location_compatible(role, consultant):
            violations.append("CONSTRAINT_FAIL_LOCATION")

    role_start = _parse_date(role.start_date)
    availability = _parse_date(consultant.availability_date)
    if role_start and availability and availability > role_start:
        violations.append("CONSTRAINT_FAIL_START_DATE")

    mandatory_status, _matches, required_targets = evaluate_mandatory_context_evidence(role, consultant)
    if required_targets and mandatory_status == "missing":
        violations.append("CONSTRAINT_FAIL_MANDATORY_CONTEXT")

    return len(violations) == 0, violations
