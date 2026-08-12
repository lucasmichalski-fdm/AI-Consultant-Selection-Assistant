"""Ranking policy toggles used to control gating and scoring behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

PolicyMode = Literal["hard", "soft", "ignore"]


@dataclass(frozen=True)
class RankingPolicy:
    """Policy controls aligned to frontend toggle semantics."""

    location_mode: PolicyMode = "hard"
    enforce_office_schedule: bool = True
    allow_relocation_path: bool = True
    start_date_mode: PolicyMode = "hard"
    authorization_mode: PolicyMode = "hard"
    experience_mode: PolicyMode = "hard"
    certification_mode: PolicyMode = "soft"
    domain_mode: PolicyMode = "soft"

    @staticmethod
    def _normalized_mode(value: Any, fallback: PolicyMode) -> PolicyMode:
        if isinstance(value, str) and value in {"hard", "soft", "ignore"}:
            return value
        return fallback

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> "RankingPolicy":
        if not data:
            return cls()
        return cls(
            location_mode=cls._normalized_mode(data.get("locationMode"), "hard"),
            enforce_office_schedule=bool(data.get("enforceOfficeSchedule", True)),
            allow_relocation_path=bool(data.get("allowRelocationPath", True)),
            start_date_mode=cls._normalized_mode(data.get("startDateMode"), "hard"),
            authorization_mode=cls._normalized_mode(data.get("authorizationMode"), "hard"),
            experience_mode=cls._normalized_mode(data.get("experienceMode"), "hard"),
            certification_mode=cls._normalized_mode(data.get("certificationMode"), "soft"),
            domain_mode=cls._normalized_mode(data.get("domainMode"), "soft"),
        )
