"""Evidence retrieval stub for Milestone C."""

from __future__ import annotations

from src.models import ConsultantProfile, RoleRequirement


def retrieve_evidence(role: RoleRequirement, consultant: ConsultantProfile) -> list[dict[str, str]]:
    """Return simple profile evidence snippets.

    Replace with stronger field-level snippets and scoring in Milestone C.
    """

    return [
        {
            "source_id": f"consultant:{consultant.consultant_id}",
            "title": f"Consultant Profile {consultant.consultant_id}",
            "snippet": f"Skills: {', '.join(consultant.normalized_skills[:5])}",
            "role_id": role.role_id,
        }
    ]
