"""Normalization helpers for multi-value fields and aliases."""

from __future__ import annotations

import re
from typing import Any

from src.models import ConsultantProfile, RoleRequirement


SKILL_ALIASES = {
    "k8s": "kubernetes",
    "node": "node.js",
    "ci integration": "ci/cd",
    "ci cd": "ci/cd",
    "ci/cd": "ci/cd",
    "nodejs": "node.js",
}


def parse_bool(value: str | None) -> bool:
    if not value:
        return False
    normalized = normalize_token(value)
    return normalized in {"yes", "true", "y", "1"}


def parse_float(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.strip().replace("%", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_token(value: str) -> str:
    token = re.sub(r"\s+", " ", value.strip().lower())
    return SKILL_ALIASES.get(token, token)


def split_multi_value(value: str | None) -> list[str]:
    if not value:
        return []

    parts = [p.strip() for p in value.split("|")]
    return [p for p in parts if p]


def normalize_multi_value(value: str | None) -> list[str]:
    return [normalize_token(token) for token in split_multi_value(value)]


def normalize_consultant_record(row: dict[str, Any]) -> ConsultantProfile:
    """Normalize fields commonly used by retrieval and scoring."""

    consultant_id = row.get("consultant_id", "").strip()

    skills_raw = "|".join(
        [
            row.get("technical_skills", ""),
            row.get("programming_languages", ""),
            row.get("cloud_platforms", ""),
            row.get("data_tools", ""),
            row.get("devops_tools", ""),
            row.get("testing_tools", ""),
        ]
    )
    tools_raw = "|".join(
        [
            row.get("data_tools", ""),
            row.get("devops_tools", ""),
            row.get("testing_tools", ""),
        ]
    )
    certs_raw = row.get("certifications", "")
    domains_raw = row.get("business_domain_experience", "")

    behavioral_scores = {
        "communication": parse_float(row.get("communication_score")) or 0.0,
        "problem_solving": parse_float(row.get("problem_solving_score")) or 0.0,
        "teamwork": parse_float(row.get("teamwork_score")) or 0.0,
        "adaptability": parse_float(row.get("adaptability_score")) or 0.0,
        "leadership": parse_float(row.get("leadership_score")) or 0.0,
    }

    return ConsultantProfile(
        consultant_id=consultant_id,
        raw=row,
        normalized_skills=normalize_multi_value(skills_raw),
        normalized_certs=normalize_multi_value(certs_raw),
        normalized_domains=normalize_multi_value(domains_raw),
        normalized_tools=normalize_multi_value(tools_raw),
        years_experience=parse_float(row.get("years_experience")) or 0.0,
        location_state=(row.get("location_state", "") or "").strip().upper(),
        work_authorization_status=(row.get("work_authorization_status", "") or "").strip(),
        willing_to_relocate=parse_bool(row.get("willing_to_relocate")),
        remote_preference=(row.get("remote_preference", "") or "").strip(),
        availability_date=(row.get("availability_date", "") or "").strip(),
        previous_client_rating=parse_float(row.get("previous_client_rating")),
        behavioral_scores=behavioral_scores,
    )


def normalize_role_record(row: dict[str, Any]) -> RoleRequirement:
    """Normalize key role fields for retrieval and ranking."""

    role_id = row.get("role_id", "").strip()

    return RoleRequirement(
        role_id=role_id,
        raw=row,
        required_skills=normalize_multi_value(row.get("required_skills", "")),
        preferred_skills=normalize_multi_value(row.get("preferred_skills", "")),
        required_certs=normalize_multi_value(row.get("required_certifications", "")),
        preferred_certs=normalize_multi_value(row.get("preferred_certifications", "")),
        required_tools=normalize_multi_value(row.get("required_tools", "")),
        nice_to_have_tools=normalize_multi_value(row.get("nice_to_have_tools", "")),
        required_domains=normalize_multi_value(row.get("required_domain_experience", "")),
        required_years_experience=parse_float(row.get("required_years_experience")) or 0.0,
        remote_or_onsite=(row.get("remote_or_onsite", "") or "").strip(),
        location_state=(row.get("location_state", "") or "").strip().upper(),
        relocation_allowed=parse_bool(row.get("relocation_allowed")),
        start_date=(row.get("start_date", "") or "").strip(),
        must_have_constraints=(row.get("must_have_constraints", "") or "").strip(),
        behavioral_importance={
            "communication": parse_float(row.get("communication_importance")) or 0.0,
            "problem_solving": parse_float(row.get("problem_solving_importance")) or 0.0,
            "teamwork": parse_float(row.get("teamwork_importance")) or 0.0,
            "adaptability": parse_float(row.get("adaptability_importance")) or 0.0,
            "leadership": parse_float(row.get("leadership_importance")) or 0.0,
        },
    )
