"""Location compatibility helpers for ranking and constraints."""

from __future__ import annotations

from src.models import ConsultantProfile, RoleRequirement

NYC_METRO_STATES = {"NY", "NJ", "CT"}


def is_remote_role(role: RoleRequirement) -> bool:
    mode = role.remote_or_onsite.lower()
    return "remote" in mode


def is_onsite_or_hybrid_role(role: RoleRequirement) -> bool:
    mode = role.remote_or_onsite.lower()
    return "onsite" in mode or "hybrid" in mode


def _schedule_preference_score(consultant: ConsultantProfile) -> float:
    preference = consultant.remote_preference.lower()
    if "onsite ok" in preference:
        return 1.0
    if "flexible" in preference:
        return 1.0
    if "hybrid" in preference:
        return 0.85
    if "remote preferred" in preference:
        return 0.55
    if "remote only" in preference:
        return 0.0
    # Unknown preference should not be treated as hard fail, but lower confidence.
    return 0.6


def _same_or_metro_state(role_state: str, consultant_state: str) -> bool:
    if not role_state or not consultant_state:
        return False
    if role_state == consultant_state:
        return True
    if role_state in NYC_METRO_STATES and consultant_state in NYC_METRO_STATES:
        return True
    return False


def location_compatible(role: RoleRequirement, consultant: ConsultantProfile) -> bool:
    """Return True when location/work-mode logistics are feasible for the role."""

    if is_remote_role(role):
        return True

    if _schedule_preference_score(consultant) <= 0.0:
        return False

    in_commute_range = _same_or_metro_state(role.location_state, consultant.location_state)
    relocation_path = role.relocation_allowed and consultant.willing_to_relocate
    return in_commute_range or relocation_path


def location_alignment_score(role: RoleRequirement, consultant: ConsultantProfile) -> float:
    """Return normalized location fit score in [0, 1]."""

    preference = consultant.remote_preference.lower()

    if is_remote_role(role):
        if "remote only" in preference:
            return 1.0
        if "remote preferred" in preference:
            return 1.0
        return 0.8

    if not location_compatible(role, consultant):
        return 0.0

    schedule = _schedule_preference_score(consultant)

    in_commute_range = _same_or_metro_state(role.location_state, consultant.location_state)
    if in_commute_range:
        proximity = 1.0
    elif role.relocation_allowed and consultant.willing_to_relocate:
        proximity = 0.6
    else:
        proximity = 0.0

    # FDM business priority: onsite logistics/proximity dominates, schedule alignment still matters.
    score = (0.75 * proximity) + (0.25 * schedule)
    return max(0.0, min(1.0, score))
