"""Runtime configuration for the consultant ranking MVP."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    ai_provider: str = "mock"
    top_n: int = 5
    retrieve_k: int = 25
    confidence_threshold: float = 0.70
    max_rationale_tokens: int = 450
    component_pipeline_enabled: bool = False


@dataclass(frozen=True)
class ScoreWeights:
    """Deterministic ranking weights that sum to 100."""

    required_skills: float = 40.0
    required_certs_tools: float = 15.0
    domain: float = 12.0
    preferred_skills: float = 10.0
    experience: float = 8.0
    behavioral: float = 8.0
    availability_location: float = 5.0
    prior_rating: float = 2.0


def load_settings() -> Settings:
    """Load settings from environment with safe defaults."""

    def _as_bool(value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        normalized = value.strip().lower()
        return normalized in {"1", "true", "yes", "y", "on"}

    return Settings(
        ai_provider=os.getenv("AI_PROVIDER", "mock"),
        top_n=int(os.getenv("TOP_N", "5")),
        retrieve_k=int(os.getenv("RETRIEVE_K", "25")),
        confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.70")),
        max_rationale_tokens=int(os.getenv("MAX_RATIONALE_TOKENS", "450")),
        component_pipeline_enabled=_as_bool(os.getenv("COMPONENT_PIPELINE_ENABLED"), False),
    )
