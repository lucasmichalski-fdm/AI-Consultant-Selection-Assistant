"""Constraint evaluation stubs."""

from __future__ import annotations

from datetime import datetime

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

    return len(violations) == 0, violations
