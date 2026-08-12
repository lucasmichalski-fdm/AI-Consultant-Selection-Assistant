"""Deterministic scoring agent interface and starter adapter."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from src.config import ScoreWeights
from src.models import RankedCandidate, RoleRequirement
from src.scoring.policy import RankingPolicy
from src.scoring.ranker import rank_candidates

from src.agents.candidate_fit_evaluator import (
    ConfirmedEvidence,
    EvaluationPacket,
    PotentialUnconfirmedEvidence,
    RequirementCoverage,
    RetrievalContext,
)


@dataclass
class CanonicalRequirementAttribution:
    """Attribution details for one canonical requirement group."""

    requirement_type: str
    source_dimensions: list[str] = field(default_factory=list)
    required_terms: list[str] = field(default_factory=list)
    matched_terms: list[str] = field(default_factory=list)
    missing_terms: list[str] = field(default_factory=list)
    coverage: float = 1.0
    allocated_weight: float = 0.0
    weighted_points: float = 0.0


@dataclass
class DeterministicScoreAttribution:
    """Parallel score attribution for raw weighted and canonical requirement groups."""

    attribution_model: str = "canonical_groups_decompose_requirement_dimensions"
    canonical_scope_dimensions: list[str] = field(
        default_factory=lambda: ["required_skills", "required_certs_tools"]
    )
    raw_weighted_dimensions: dict[str, float] = field(default_factory=dict)
    canonical_requirement_groups: list[CanonicalRequirementAttribution] = field(default_factory=list)
    requirement_dimension_points_total: float = 0.0
    canonical_weighted_points_total: float = 0.0
    requirement_canonical_rounding_delta: float = 0.0
    overall_fit_points_total: float = 0.0
    reconciliation_note: str = (
        "canonical_requirement_groups only decompose requirement-related dimensions "
        "(required_skills and required_certs_tools), not total fit score."
    )


@dataclass
class DeterministicEvaluation:
    """Canonical scoring output for downstream componentized agents."""

    role_id: str
    consultant_id: str
    ranked_candidate: RankedCandidate
    retrieval_context: RetrievalContext = field(default_factory=RetrievalContext)
    confirmed_evidence: ConfirmedEvidence = field(default_factory=ConfirmedEvidence)
    potential_unconfirmed: PotentialUnconfirmedEvidence = field(default_factory=PotentialUnconfirmedEvidence)
    requirement_coverage: RequirementCoverage = field(default_factory=RequirementCoverage)
    score_attribution: DeterministicScoreAttribution = field(default_factory=DeterministicScoreAttribution)


class DeterministicScoringAgent:
    """Interface for authoritative deterministic ranking."""

    def rank(
        self,
        role: RoleRequirement,
        packets: list[EvaluationPacket],
        top_n: int | None = None,
        policy: RankingPolicy | None = None,
    ) -> list[DeterministicEvaluation]:
        raise NotImplementedError


class DefaultDeterministicScoringAgent(DeterministicScoringAgent):
    """Starter adapter over the existing deterministic ranker."""

    def __init__(self, weights: ScoreWeights | None = None) -> None:
        self._weights = weights or ScoreWeights()

    @staticmethod
    def _normalized_term_set(terms: list[str]) -> set[str]:
        normalized: set[str] = set()
        for term in terms:
            cleaned = term.strip().lower()
            if cleaned:
                normalized.add(cleaned)
        return normalized

    @staticmethod
    def _build_canonical_group(
        requirement_type: str,
        required_terms: set[str],
        matched_terms: set[str],
        source_dimensions: list[str],
        allocated_weight: float,
    ) -> CanonicalRequirementAttribution:
        sorted_required = sorted(required_terms)
        sorted_matched = sorted(required_terms.intersection(matched_terms))
        missing = sorted(required_terms.difference(set(sorted_matched)))
        coverage = 1.0 if not sorted_required else (len(sorted_matched) / len(sorted_required))
        weighted_points = allocated_weight * coverage

        return CanonicalRequirementAttribution(
            requirement_type=requirement_type,
            source_dimensions=source_dimensions,
            required_terms=sorted_required,
            matched_terms=sorted_matched,
            missing_terms=missing,
            coverage=round(coverage, 4),
            allocated_weight=round(allocated_weight, 4),
            weighted_points=round(weighted_points, 4),
        )

    def _build_raw_weighted_dimensions(self, ranked_candidate: RankedCandidate) -> dict[str, float]:
        dimension_weights = {
            "required_skills": self._weights.required_skills,
            "required_certs_tools": self._weights.required_certs_tools,
            "domain": self._weights.domain,
            "preferred_skills": self._weights.preferred_skills,
            "experience": self._weights.experience,
            "behavioral": self._weights.behavioral,
            "availability_location": self._weights.availability_location,
            "prior_rating": self._weights.prior_rating,
        }

        weighted: dict[str, float] = {}
        for dimension, weight in dimension_weights.items():
            component_score = ranked_candidate.score_components.get(dimension, 0.0)
            weighted[dimension] = round(component_score * weight, 4)
        return weighted

    def _build_canonical_requirement_groups(
        self,
        requirement_coverage: RequirementCoverage,
    ) -> list[CanonicalRequirementAttribution]:
        skill_required = self._normalized_term_set(requirement_coverage.required_skills.required_terms)
        skill_matched = self._normalized_term_set(requirement_coverage.required_skills.matched_terms)
        tool_required = self._normalized_term_set(requirement_coverage.required_tools.required_terms)
        tool_matched = self._normalized_term_set(requirement_coverage.required_tools.matched_terms)
        cert_required = self._normalized_term_set(requirement_coverage.required_certifications.required_terms)
        cert_matched = self._normalized_term_set(requirement_coverage.required_certifications.matched_terms)

        required_technology = skill_required.intersection(tool_required)
        required_skill_only = skill_required.difference(required_technology)
        required_tool_only = tool_required.difference(required_technology)

        skill_allocation_count = len(required_skill_only) + len(required_technology)
        bundle_allocation_count = len(required_tool_only) + len(required_technology) + len(cert_required)

        skill_only_weight = 0.0
        technology_from_skills_weight = 0.0
        if skill_allocation_count > 0:
            skill_only_weight = self._weights.required_skills * (len(required_skill_only) / skill_allocation_count)
            technology_from_skills_weight = self._weights.required_skills * (
                len(required_technology) / skill_allocation_count
            )

        tool_only_weight = 0.0
        technology_from_bundle_weight = 0.0
        cert_weight = 0.0
        if bundle_allocation_count > 0:
            tool_only_weight = self._weights.required_certs_tools * (len(required_tool_only) / bundle_allocation_count)
            technology_from_bundle_weight = self._weights.required_certs_tools * (
                len(required_technology) / bundle_allocation_count
            )
            cert_weight = self._weights.required_certs_tools * (len(cert_required) / bundle_allocation_count)

        groups: list[CanonicalRequirementAttribution] = []
        if required_skill_only:
            groups.append(
                self._build_canonical_group(
                    requirement_type="required_skill",
                    required_terms=required_skill_only,
                    matched_terms=skill_matched,
                    source_dimensions=["required_skills"],
                    allocated_weight=skill_only_weight,
                )
            )

        if required_technology:
            groups.append(
                self._build_canonical_group(
                    requirement_type="required_technology",
                    required_terms=required_technology,
                    matched_terms=skill_matched.union(tool_matched),
                    source_dimensions=["required_skills", "required_tools"],
                    allocated_weight=technology_from_skills_weight + technology_from_bundle_weight,
                )
            )

        if required_tool_only:
            groups.append(
                self._build_canonical_group(
                    requirement_type="required_tool",
                    required_terms=required_tool_only,
                    matched_terms=tool_matched,
                    source_dimensions=["required_tools"],
                    allocated_weight=tool_only_weight,
                )
            )

        if cert_required:
            groups.append(
                self._build_canonical_group(
                    requirement_type="required_certification",
                    required_terms=cert_required,
                    matched_terms=cert_matched,
                    source_dimensions=["required_certifications"],
                    allocated_weight=cert_weight,
                )
            )

        groups.sort(key=lambda item: item.requirement_type)
        return groups

    def _build_score_attribution(
        self,
        ranked_candidate: RankedCandidate,
        requirement_coverage: RequirementCoverage,
    ) -> DeterministicScoreAttribution:
        raw = self._build_raw_weighted_dimensions(ranked_candidate)
        canonical_groups = self._build_canonical_requirement_groups(requirement_coverage)
        requirement_total = raw.get("required_skills", 0.0) + raw.get("required_certs_tools", 0.0)
        canonical_total = sum(group.weighted_points for group in canonical_groups)
        rounding_delta = canonical_total - requirement_total
        overall_total = sum(raw.values())

        return DeterministicScoreAttribution(
            raw_weighted_dimensions=raw,
            canonical_requirement_groups=canonical_groups,
            requirement_dimension_points_total=round(requirement_total, 4),
            canonical_weighted_points_total=round(canonical_total, 4),
            requirement_canonical_rounding_delta=round(rounding_delta, 4),
            overall_fit_points_total=round(overall_total, 4),
        )

    def rank(
        self,
        role: RoleRequirement,
        packets: list[EvaluationPacket],
        top_n: int | None = None,
        policy: RankingPolicy | None = None,
    ) -> list[DeterministicEvaluation]:
        consultants = [packet.consultant_profile for packet in packets]
        ranked = rank_candidates(role, consultants, self._weights, policy=policy)
        if top_n is not None:
            ranked = ranked[:top_n]

        packet_by_id = {packet.consultant_id: packet for packet in packets}

        evaluations: list[DeterministicEvaluation] = []
        for ranked_candidate in ranked:
            packet = packet_by_id.get(ranked_candidate.consultant_id)
            if packet is None:
                continue
            score_attribution = self._build_score_attribution(ranked_candidate, packet.requirement_coverage)
            evaluations.append(
                DeterministicEvaluation(
                    role_id=role.role_id,
                    consultant_id=ranked_candidate.consultant_id,
                    ranked_candidate=ranked_candidate,
                    retrieval_context=packet.retrieval_context,
                    confirmed_evidence=packet.confirmed_evidence,
                    potential_unconfirmed=packet.potential_unconfirmed,
                    requirement_coverage=packet.requirement_coverage,
                    score_attribution=score_attribution,
                )
            )

        return evaluations
