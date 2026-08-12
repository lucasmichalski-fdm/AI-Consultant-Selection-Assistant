"""Evidence matching helpers for structured fields + free-text profile evidence."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from src.models import ConsultantProfile


RELATED_TERM_HINTS: dict[str, tuple[str, ...]] = {
    "airflow": ("prefect", "dagster", "luigi", "scheduler", "workflow orchestration", "orchestration"),
    "snowflake": ("redshift", "bigquery", "synapse", "data warehouse", "warehouse"),
    "dbt": ("data build tool", "transform", "transformation framework"),
    "kubernetes": ("k8s", "container orchestration", "helm"),
    "terraform": ("infrastructure as code", "iac", "pulumi", "cloudformation"),
    "aws certified": ("certification", "certified", "badge"),
    "azure certified": ("certification", "certified", "badge"),
}


def _normalize_for_match(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def consultant_evidence_text(consultant: ConsultantProfile) -> str:
    """Return normalized free-text evidence fields for matching."""

    joined = " ".join(
        [
            consultant.raw.get("resume_text", "") or "",
            consultant.raw.get("project_experience_summary", "") or "",
            consultant.raw.get("notes", "") or "",
        ]
    )
    return f" {_normalize_for_match(joined)} "


def _token_set(text: str) -> set[str]:
    return {token for token in text.strip().split(" ") if token}


def _contains_phrase(evidence: str, phrase: str) -> bool:
    norm = _normalize_for_match(phrase)
    if not norm:
        return False
    return f" {norm} " in evidence


def _soft_lexical_near_match(term_norm: str, observed_phrases: set[str]) -> bool:
    for observed in observed_phrases:
        if observed == term_norm:
            continue
        ratio = SequenceMatcher(a=term_norm, b=observed).ratio()
        if ratio >= 0.84:
            return True
    return False


def match_terms_from_structured_and_text(
    required_terms: list[str],
    structured_terms: list[str],
    consultant: ConsultantProfile,
) -> set[str]:
    """Return required terms matched from either structured fields or text evidence."""

    required = [term for term in required_terms if term]
    required_norm = {_normalize_for_match(term) for term in required}
    structured = {_normalize_for_match(term) for term in structured_terms if term}
    matched_norm = set(required_norm.intersection(structured))

    evidence = consultant_evidence_text(consultant)
    for term_norm in required_norm:
        if term_norm in matched_norm:
            continue
        if f" {term_norm} " in evidence:
            matched_norm.add(term_norm)

    matched_required_terms: set[str] = set()
    for term in required:
        if _normalize_for_match(term) in matched_norm:
            matched_required_terms.add(term)

    return matched_required_terms


def find_potential_unconfirmed_terms(
    required_terms: list[str],
    structured_terms: list[str],
    consultant: ConsultantProfile,
) -> dict[str, list[str]]:
    """Return review-only potential matches for missing required terms.

    This does not mark requirements as satisfied. It only surfaces adjacent
    evidence cues for recruiter follow-up.
    """

    explicit_matches = match_terms_from_structured_and_text(required_terms, structured_terms, consultant)
    evidence = consultant_evidence_text(consultant)

    structured_norm = {_normalize_for_match(term) for term in structured_terms if term}
    observed_phrases = set(structured_norm)
    observed_phrases.update({_normalize_for_match(token) for token in evidence.split(" ") if token})
    evidence_tokens = _token_set(evidence)

    potential: dict[str, list[str]] = {}
    for required_term in required_terms:
        if not required_term or required_term in explicit_matches:
            continue

        term_norm = _normalize_for_match(required_term)
        cues: list[str] = []

        for hint in RELATED_TERM_HINTS.get(term_norm, ()):
            if _contains_phrase(evidence, hint) or _normalize_for_match(hint) in structured_norm:
                cues.append(f"related:{_normalize_for_match(hint)}")

        term_tokens = _token_set(term_norm)
        shared_tokens = term_tokens.intersection(evidence_tokens)
        if term_tokens and len(shared_tokens) >= max(1, len(term_tokens) // 2):
            cues.append("partial_token_overlap")

        if _soft_lexical_near_match(term_norm, observed_phrases):
            cues.append("soft_lexical_similarity")

        if cues:
            potential[required_term] = sorted(set(cues))

    return potential
