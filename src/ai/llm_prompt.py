"""Prompt builder stubs."""

from __future__ import annotations

from src.models import ConsultantProfile, RoleRequirement


def build_rationale_prompt(role: RoleRequirement, consultant: ConsultantProfile, evidence: list[dict[str, str]]) -> str:
    """Build a grounded prompt for explanation generation."""

    evidence_lines = "\n".join(f"- {item['snippet']}" for item in evidence)
    return (
        "Use only the provided evidence. Return JSON with rationale and confidence.\n"
        f"Role: {role.role_id}\n"
        f"Consultant: {consultant.consultant_id}\n"
        f"Evidence:\n{evidence_lines}\n"
    )
