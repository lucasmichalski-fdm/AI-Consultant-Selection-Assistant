"""Constraint evaluation stubs."""

from __future__ import annotations

from datetime import datetime

from src.models import ConsultantProfile, RoleRequirement


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


def _is_onsite_or_hybrid(role: RoleRequirement) -> bool:
    mode = role.remote_or_onsite.lower()
    return "onsite" in mode or "hybrid" in mode


def evaluate_constraints(role: RoleRequirement, consultant: ConsultantProfile) -> tuple[bool, list[str]]:
    """Return (passes, violations) for hard constraints."""

    violations: list[str] = []

    if role.required_years_experience > 0 and consultant.years_experience < role.required_years_experience:
        violations.append("CONSTRAINT_FAIL_EXPERIENCE_MIN")

    if _requires_no_sponsorship(role):
        auth = consultant.work_authorization_status.lower()
        if "sponsorship required" in auth and "no sponsorship required" not in auth:
            violations.append("CONSTRAINT_FAIL_AUTHORIZATION")

    if _is_onsite_or_hybrid(role):
        state_match = consultant.location_state == role.location_state
        relocation_path = role.relocation_allowed and consultant.willing_to_relocate
        if not state_match and not relocation_path:
            violations.append("CONSTRAINT_FAIL_LOCATION")

    role_start = _parse_date(role.start_date)
    availability = _parse_date(consultant.availability_date)
    if role_start and availability and availability > role_start:
        violations.append("CONSTRAINT_FAIL_START_DATE")

    return len(violations) == 0, violations
