"""Core typed models for Milestone A."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConsultantProfile:
    """Normalized consultant record from consultant_profiles_train.csv."""

    consultant_id: str
    raw: dict[str, Any]
    normalized_skills: list[str] = field(default_factory=list)
    normalized_certs: list[str] = field(default_factory=list)
    normalized_domains: list[str] = field(default_factory=list)
    normalized_tools: list[str] = field(default_factory=list)
    years_experience: float = 0.0
    location_state: str = ""
    work_authorization_status: str = ""
    willing_to_relocate: bool = False
    remote_preference: str = ""
    availability_date: str = ""
    previous_client_rating: float | None = None
    behavioral_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class RoleRequirement:
    """Normalized role record from role_requirements_train.csv."""

    role_id: str
    raw: dict[str, Any]
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    required_certs: list[str] = field(default_factory=list)
    preferred_certs: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    nice_to_have_tools: list[str] = field(default_factory=list)
    required_domains: list[str] = field(default_factory=list)
    required_years_experience: float = 0.0
    remote_or_onsite: str = ""
    location_state: str = ""
    relocation_allowed: bool = False
    start_date: str = ""
    must_have_constraints: str = ""
    behavioral_importance: dict[str, float] = field(default_factory=dict)


@dataclass
class ScoreCard:
    """Deterministic score components for a candidate-role pair."""

    required_skills: float = 0.0
    required_certs_tools: float = 0.0
    domain: float = 0.0
    preferred_skills: float = 0.0
    experience: float = 0.0
    behavioral: float = 0.0
    availability_location: float = 0.0
    prior_rating: float = 0.0


@dataclass
class RankedCandidate:
    """Ranked candidate output skeleton."""

    rank: int
    consultant_id: str
    fit_score: float
    eligibility_status: str = "unknown"
    eligibility_basis: str = "hard_constraints_only"
    eligibility_explanation: str = (
        "eligibility_status is driven only by hard constraints; required skill/tool/cert gaps affect fit_score but are non-gating unless encoded as hard constraints."
    )
    ranking_tier: int = 1
    risk_tier: int = 0
    ranking_key: list[Any] = field(default_factory=list)
    ranking_key_semantics: str = (
        "[ranking_tier, -fit_score, -required_skills, risk_tier, -required_certs_tools, availability_date, consultant_id]"
    )
    score_components: dict[str, float] = field(default_factory=dict)
    reason_codes: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)


@dataclass
class RankingResponse:
    """Top-level response skeleton aligned with MVP spec."""

    request_id: str
    summary: str
    confidence: float
    human_review_required: bool
    candidate_rankings: list[RankedCandidate] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    latency_ms: int = 0
