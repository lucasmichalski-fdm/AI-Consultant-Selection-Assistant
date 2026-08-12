"""Resume upskill advisor interface and starter advisory generator."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.agents.deterministic_scoring_agent import DeterministicEvaluation


@dataclass
class UpskillAdvice:
    """Advisory output for improving a consultant's role positioning."""

    consultant_id: str
    role_id: str
    requirement_gaps: list[RequirementGap] = field(default_factory=list)
    upskill_targets: list[UpskillTarget] = field(default_factory=list)


@dataclass
class RequirementGap:
    """Structured requirement gap for UI and business logic."""

    requirement: str
    requirement_type: str
    mandatory: bool = True
    mandatory_scope: str = "role_requirement_non_gating"
    gates_eligibility: bool = False
    gap_status: str = "missing"
    source_dimensions: list[str] = field(default_factory=list)


@dataclass
class UpskillTarget:
    """Minimal upskill target with estimated time range in weeks."""

    requirement: str
    requirement_type: str
    gap_status: str
    estimated_weeks_low: int
    estimated_weeks_high: int


class ResumeUpskillAdvisor:
    """Interface for role-targeted, non-assertive upskilling guidance."""

    def advise(self, evaluation: DeterministicEvaluation) -> UpskillAdvice:
        raise NotImplementedError


class DefaultResumeUpskillAdvisor(ResumeUpskillAdvisor):
    """Starter advisor that separates confirmed gaps from potential signals."""

    @staticmethod
    def _gap_type_from_source(source: str) -> str:
        mapping = {
            "required_skills": "required_skill",
            "required_tools": "required_tool",
            "required_certifications": "required_certification",
        }
        return mapping.get(source, "required_requirement")

    @staticmethod
    def _gap_type_from_sources(sources: set[str]) -> str:
        if {"required_skills", "required_tools"}.issubset(sources):
            return "required_technology"
        if "required_skills" in sources:
            return "required_skill"
        if "required_tools" in sources:
            return "required_tool"
        if "required_certifications" in sources:
            return "required_certification"
        return "required_requirement"

    @staticmethod
    def _canonical_term(term: str) -> str:
        return term.strip().lower()

    @staticmethod
    def _infer_gap_status(
        requirement: str,
        potential_terms: set[str],
        reason_codes: list[str],
    ) -> str:
        term = requirement.strip().lower()
        if term in potential_terms:
            if "REQ_SKILLS_STRONG" in reason_codes:
                return "development_opportunity"
            return "unverified"
        return "missing"

    @staticmethod
    def _established_strength(evaluation: DeterministicEvaluation) -> float:
        coverage = evaluation.requirement_coverage
        values: list[float] = []
        if coverage.required_skills.required_terms:
            values.append(coverage.required_skills.coverage)
        if coverage.required_tools.required_terms:
            values.append(coverage.required_tools.coverage)
        if not values:
            return 1.0
        return sum(values) / len(values)

    @staticmethod
    def _estimate_upskill_weeks(gap_status: str, established_strength: float) -> tuple[int, int]:
        if gap_status == "unverified":
            base_low, base_high = 2, 4
        elif gap_status == "development_opportunity":
            base_low, base_high = 3, 6
        else:
            base_low, base_high = 6, 10

        if established_strength >= 0.75:
            base_low = max(1, base_low - 1)
            base_high = max(base_low, base_high - 2)
        elif established_strength < 0.4:
            base_low += 2
            base_high += 2

        return base_low, base_high

    def advise(self, evaluation: DeterministicEvaluation) -> UpskillAdvice:
        coverage = evaluation.requirement_coverage

        confirmed_gap_records: list[tuple[str, str]] = []
        confirmed_gap_records.extend(
            [(term, "required_skills") for term in coverage.required_skills.missing_terms]
        )
        confirmed_gap_records.extend(
            [(term, "required_tools") for term in coverage.required_tools.missing_terms]
        )
        confirmed_gap_records.extend(
            [(term, "required_certifications") for term in coverage.required_certifications.missing_terms]
        )

        # If a role has required certs but terms are missing in metadata, keep a generic fallback.
        if coverage.required_certifications.required_terms and not coverage.required_certifications.matched_terms:
            if not coverage.required_certifications.missing_terms:
                confirmed_gap_records.append(("required_certification", "required_certifications"))

        grouped_confirmed: dict[str, set[str]] = {}
        for requirement, source in confirmed_gap_records:
            canonical = self._canonical_term(requirement)
            if canonical not in grouped_confirmed:
                grouped_confirmed[canonical] = set()
            grouped_confirmed[canonical].add(source)

        requirement_gaps: list[RequirementGap] = []
        for canonical in sorted(grouped_confirmed):
            sources = grouped_confirmed[canonical]
            requirement_gaps.append(
                RequirementGap(
                    requirement=canonical,
                    requirement_type=self._gap_type_from_sources(sources),
                    mandatory=True,
                    mandatory_scope="role_requirement_non_gating",
                    gates_eligibility=False,
                    source_dimensions=sorted(sources),
                )
            )

        potential_terms = sorted(
            set(evaluation.potential_unconfirmed.required_skills)
            .union(evaluation.potential_unconfirmed.required_tools)
            .union(evaluation.potential_unconfirmed.required_certs)
        )
        potential_term_set = {self._canonical_term(term) for term in potential_terms}

        updated_confirmed: list[RequirementGap] = []
        for gap in requirement_gaps:
            status = self._infer_gap_status(
                requirement=gap.requirement,
                potential_terms=potential_term_set,
                reason_codes=evaluation.ranked_candidate.reason_codes,
            )
            updated_confirmed.append(
                RequirementGap(
                    requirement=gap.requirement,
                    requirement_type=gap.requirement_type,
                    mandatory=gap.mandatory,
                    mandatory_scope=gap.mandatory_scope,
                    gates_eligibility=gap.gates_eligibility,
                    gap_status=status,
                    source_dimensions=gap.source_dimensions,
                )
            )
        requirement_gaps = updated_confirmed

        established_strength = self._established_strength(evaluation)
        upskill_targets: list[UpskillTarget] = []
        upskill_types = {"required_skill", "required_tool", "required_technology"}
        for gap in requirement_gaps:
            if gap.requirement_type not in upskill_types:
                continue
            low, high = self._estimate_upskill_weeks(gap.gap_status, established_strength)
            upskill_targets.append(
                UpskillTarget(
                    requirement=gap.requirement,
                    requirement_type=gap.requirement_type,
                    gap_status=gap.gap_status,
                    estimated_weeks_low=low,
                    estimated_weeks_high=high,
                )
            )

        return UpskillAdvice(
            consultant_id=evaluation.consultant_id,
            role_id=evaluation.role_id,
            requirement_gaps=requirement_gaps,
            upskill_targets=upskill_targets,
        )
