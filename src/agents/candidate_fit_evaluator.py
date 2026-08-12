"""Candidate fit evaluator contracts and starter deterministic packet builder."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.config import ScoreWeights
from src.models import ConsultantProfile, RoleRequirement
from src.scoring.constraints import evaluate_constraints
from src.scoring.evidence import find_potential_unconfirmed_terms, match_terms_from_structured_and_text
from src.scoring.ranker import rank_candidates


@dataclass
class RetrievalContext:
    """Discovery metadata attached to one candidate-role evaluation."""

    retrieval_score: float = 0.0
    retrieval_reasons: list[str] = field(default_factory=list)


@dataclass
class ConfirmedEvidence:
    """Requirement evidence that is confirmed and score-eligible."""

    required_skills: list[str] = field(default_factory=list)
    required_certs: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    required_domains: list[str] = field(default_factory=list)


@dataclass
class PotentialUnconfirmedEvidence:
    """Potential but unconfirmed relevance signals for recruiter review."""

    required_skills: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    required_certs: list[str] = field(default_factory=list)


@dataclass
class ConstraintResult:
    """Hard-rule gate result for one candidate-role pair."""

    passes: bool
    violations: list[str] = field(default_factory=list)


@dataclass
class CoverageDimension:
    """Coverage details for one requirement dimension."""

    required_terms: list[str] = field(default_factory=list)
    matched_terms: list[str] = field(default_factory=list)
    missing_terms: list[str] = field(default_factory=list)
    coverage: float = 1.0


@dataclass
class RequirementCoverage:
    """Separated coverage for required and preferred requirement groups."""

    required_skills: CoverageDimension = field(default_factory=CoverageDimension)
    required_certifications: CoverageDimension = field(default_factory=CoverageDimension)
    required_tools: CoverageDimension = field(default_factory=CoverageDimension)
    preferred_skills: CoverageDimension = field(default_factory=CoverageDimension)
    preferred_certifications: CoverageDimension = field(default_factory=CoverageDimension)
    preferred_tools: CoverageDimension = field(default_factory=CoverageDimension)


@dataclass
class EvaluationPacket:
    """Standardized handoff from fit evaluator to deterministic scorer."""

    role_id: str
    consultant_id: str
    consultant_profile: ConsultantProfile
    retrieval_context: RetrievalContext = field(default_factory=RetrievalContext)
    confirmed_evidence: ConfirmedEvidence = field(default_factory=ConfirmedEvidence)
    potential_unconfirmed: PotentialUnconfirmedEvidence = field(default_factory=PotentialUnconfirmedEvidence)
    requirement_coverage: RequirementCoverage = field(default_factory=RequirementCoverage)
    component_scores: dict[str, float] = field(default_factory=dict)
    constraints: ConstraintResult = field(default_factory=lambda: ConstraintResult(passes=True, violations=[]))
    reason_seed_codes: list[str] = field(default_factory=list)


def _build_coverage_dimension(
    required_terms: list[str],
    structured_terms: list[str],
    consultant: ConsultantProfile,
) -> CoverageDimension:
    required = sorted({term for term in required_terms if term})
    matched = sorted(match_terms_from_structured_and_text(required, structured_terms, consultant))
    missing = sorted(set(required).difference(set(matched)))
    coverage = 1.0 if not required else (len(matched) / len(required))
    return CoverageDimension(
        required_terms=required,
        matched_terms=matched,
        missing_terms=missing,
        coverage=round(coverage, 4),
    )


class CandidateFitEvaluator:
    """Interface for one-role/one-consultant evaluation."""

    def evaluate(
        self,
        role: RoleRequirement,
        consultant: ConsultantProfile,
        retrieval_context: RetrievalContext | None = None,
    ) -> EvaluationPacket:
        raise NotImplementedError


class DeterministicCandidateFitEvaluator(CandidateFitEvaluator):
    """Starter evaluator using current deterministic logic and evidence tiers."""

    def __init__(self) -> None:
        self._weights = ScoreWeights()

    def evaluate(
        self,
        role: RoleRequirement,
        consultant: ConsultantProfile,
        retrieval_context: RetrievalContext | None = None,
    ) -> EvaluationPacket:
        retrieval = retrieval_context or RetrievalContext()

        confirmed_skills = sorted(
            match_terms_from_structured_and_text(role.required_skills, consultant.normalized_skills, consultant)
        )
        confirmed_certs = sorted(
            match_terms_from_structured_and_text(role.required_certs, consultant.normalized_certs, consultant)
        )
        confirmed_tools = sorted(
            match_terms_from_structured_and_text(role.required_tools, consultant.normalized_tools, consultant)
        )
        confirmed_domains = sorted(
            match_terms_from_structured_and_text(role.required_domains, consultant.normalized_domains, consultant)
        )

        requirement_coverage = RequirementCoverage(
            required_skills=_build_coverage_dimension(role.required_skills, consultant.normalized_skills, consultant),
            required_certifications=_build_coverage_dimension(role.required_certs, consultant.normalized_certs, consultant),
            required_tools=_build_coverage_dimension(role.required_tools, consultant.normalized_tools, consultant),
            preferred_skills=_build_coverage_dimension(role.preferred_skills, consultant.normalized_skills, consultant),
            preferred_certifications=_build_coverage_dimension(role.preferred_certs, consultant.normalized_certs, consultant),
            preferred_tools=_build_coverage_dimension(role.nice_to_have_tools, consultant.normalized_tools, consultant),
        )

        potential_skills = sorted(
            find_potential_unconfirmed_terms(role.required_skills, consultant.normalized_skills, consultant).keys()
        )
        potential_tools = sorted(
            find_potential_unconfirmed_terms(role.required_tools, consultant.normalized_tools, consultant).keys()
        )
        potential_certs = sorted(
            find_potential_unconfirmed_terms(role.required_certs, consultant.normalized_certs, consultant).keys()
        )

        passes, violations = evaluate_constraints(role, consultant)
        ranked_single = rank_candidates(role, [consultant], self._weights)[0]

        return EvaluationPacket(
            role_id=role.role_id,
            consultant_id=consultant.consultant_id,
            consultant_profile=consultant,
            retrieval_context=retrieval,
            confirmed_evidence=ConfirmedEvidence(
                required_skills=confirmed_skills,
                required_certs=confirmed_certs,
                required_tools=confirmed_tools,
                required_domains=confirmed_domains,
            ),
            potential_unconfirmed=PotentialUnconfirmedEvidence(
                required_skills=potential_skills,
                required_tools=potential_tools,
                required_certs=potential_certs,
            ),
            requirement_coverage=requirement_coverage,
            component_scores=ranked_single.score_components,
            constraints=ConstraintResult(passes=passes, violations=violations),
            reason_seed_codes=ranked_single.reason_codes,
        )
