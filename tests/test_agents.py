from src.agents.candidate_fit_evaluator import (
    CoverageDimension,
    ConfirmedEvidence,
    ConstraintResult,
    EvaluationPacket,
    PotentialUnconfirmedEvidence,
    RequirementCoverage,
)
from src.agents.deterministic_scoring_agent import DefaultDeterministicScoringAgent, DeterministicEvaluation
from src.agents.rank_comparison_agent import DeterministicRankComparisonAgent
from src.agents.resume_upskill_advisor import DefaultResumeUpskillAdvisor
from src.models import ConsultantProfile, RankedCandidate, RoleRequirement


def test_rank_comparison_uses_eligibility_narrative_when_fit_is_lower() -> None:
    higher = RankedCandidate(
        rank=1,
        consultant_id="C-001",
        fit_score=70.0,
        score_components={"required_skills": 0.6},
        risk_flags=[],
    )
    lower = RankedCandidate(
        rank=2,
        consultant_id="C-002",
        fit_score=82.0,
        score_components={"required_skills": 0.9},
        risk_flags=["CONSTRAINT_FAIL_LOCATION"],
    )

    evaluations = [
        DeterministicEvaluation(role_id="R-001", consultant_id="C-001", ranked_candidate=higher),
        DeterministicEvaluation(role_id="R-001", consultant_id="C-002", ranked_candidate=lower),
    ]
    comparisons = DeterministicRankComparisonAgent().compare(evaluations)

    assert len(comparisons) == 1
    assert "eligibility and risk ordering" in comparisons[0].narrative


def test_upskill_advisor_deduplicates_requirement_gaps() -> None:
    role = RoleRequirement(role_id="R-300", raw={})
    consultant = ConsultantProfile(consultant_id="C-300", raw={})
    packet = EvaluationPacket(
        role_id="R-300",
        consultant_id="C-300",
        consultant_profile=consultant,
        confirmed_evidence=ConfirmedEvidence(required_skills=["python"], required_tools=["snowflake"]),
        potential_unconfirmed=PotentialUnconfirmedEvidence(required_skills=["snowflake"]),
        constraints=ConstraintResult(passes=True, violations=[]),
    )
    ranked_candidate = RankedCandidate(
        rank=5,
        consultant_id="C-300",
        fit_score=62.1,
        reason_codes=["GAP_REQUIRED_SKILL_SNOWFLAKE", "GAP_REQUIRED_CERT"],
    )
    evaluation = DeterministicEvaluation(
        role_id="R-300",
        consultant_id="C-300",
        ranked_candidate=ranked_candidate,
        confirmed_evidence=packet.confirmed_evidence,
        potential_unconfirmed=packet.potential_unconfirmed,
        requirement_coverage=RequirementCoverage(
            required_skills=CoverageDimension(required_terms=["python", "snowflake"], matched_terms=["python"], missing_terms=["snowflake"], coverage=0.5),
            required_certifications=CoverageDimension(required_terms=["az-104"], matched_terms=[], missing_terms=["az-104"], coverage=0.0),
            required_tools=CoverageDimension(required_terms=["snowflake"], matched_terms=["snowflake"], missing_terms=[], coverage=1.0),
        ),
    )

    advice = DefaultResumeUpskillAdvisor().advise(evaluation)

    confirmed_requirements = [gap.requirement for gap in advice.requirement_gaps]
    assert confirmed_requirements.count("snowflake") == 1
    assert "az-104" in confirmed_requirements

    gap_types = {gap.requirement: gap.requirement_type for gap in advice.requirement_gaps}
    assert gap_types["snowflake"] == "required_skill"
    assert gap_types["az-104"] == "required_certification"

    snowflake_gap = next(gap for gap in advice.requirement_gaps if gap.requirement == "snowflake")
    assert snowflake_gap.source_dimensions == ["required_skills"]
    assert snowflake_gap.mandatory_scope == "role_requirement_non_gating"
    assert snowflake_gap.gates_eligibility is False

    gap_status = {gap.requirement: gap.gap_status for gap in advice.requirement_gaps}
    assert gap_status["snowflake"] in {"unverified", "development_opportunity"}
    assert gap_status["az-104"] == "missing"

    targets = {item.requirement: item for item in advice.upskill_targets}
    assert "snowflake" in targets
    assert targets["snowflake"].estimated_weeks_low >= 1
    assert targets["snowflake"].estimated_weeks_high >= targets["snowflake"].estimated_weeks_low


def test_upskill_advisor_does_not_infer_required_cert_gap_when_none_required() -> None:
    ranked_candidate = RankedCandidate(
        rank=3,
        consultant_id="C-038",
        fit_score=82.16,
        score_components={"required_certs_tools": 0.5},
        reason_codes=["REQ_SKILLS_STRONG", "DOMAIN_STRONG_FIT", "REQ_CERT_TOOLS_STRONG"],
    )

    evaluation = DeterministicEvaluation(
        role_id="R-003",
        consultant_id="C-038",
        ranked_candidate=ranked_candidate,
        requirement_coverage=RequirementCoverage(
            required_skills=CoverageDimension(required_terms=["python"], matched_terms=["python"], missing_terms=[], coverage=1.0),
            required_certifications=CoverageDimension(required_terms=[], matched_terms=[], missing_terms=[], coverage=1.0),
            required_tools=CoverageDimension(required_terms=["databricks"], matched_terms=[], missing_terms=["databricks"], coverage=0.0),
        ),
    )

    advice = DefaultResumeUpskillAdvisor().advise(evaluation)

    confirmed_requirements = [gap.requirement for gap in advice.requirement_gaps]
    assert "required_certification" not in confirmed_requirements
    assert "required_certifications" not in confirmed_requirements
    assert "databricks" in confirmed_requirements


def test_upskill_advisor_emits_development_opportunity_for_unverified_gap_with_strong_signal() -> None:
    ranked_candidate = RankedCandidate(
        rank=1,
        consultant_id="C-777",
        fit_score=88.0,
        reason_codes=["REQ_SKILLS_STRONG", "GAP_REQUIRED_SKILL_AIRFLOW"],
    )
    evaluation = DeterministicEvaluation(
        role_id="R-777",
        consultant_id="C-777",
        ranked_candidate=ranked_candidate,
        potential_unconfirmed=PotentialUnconfirmedEvidence(required_skills=["airflow"]),
        requirement_coverage=RequirementCoverage(
            required_skills=CoverageDimension(required_terms=["airflow"], matched_terms=[], missing_terms=["airflow"], coverage=0.0),
            required_certifications=CoverageDimension(),
            required_tools=CoverageDimension(),
        ),
    )

    advice = DefaultResumeUpskillAdvisor().advise(evaluation)

    airflow_gap = next(gap for gap in advice.requirement_gaps if gap.requirement == "airflow")
    assert airflow_gap.gap_status == "development_opportunity"


def test_upskill_advisor_emits_upskill_targets_for_required_skills_tools() -> None:
    ranked_candidate = RankedCandidate(
        rank=5,
        consultant_id="C-500",
        fit_score=70.0,
        reason_codes=[],
    )
    evaluation = DeterministicEvaluation(
        role_id="R-500",
        consultant_id="C-500",
        ranked_candidate=ranked_candidate,
        potential_unconfirmed=PotentialUnconfirmedEvidence(required_skills=["data modeling"]),
        requirement_coverage=RequirementCoverage(
            required_skills=CoverageDimension(
                required_terms=["data modeling"],
                matched_terms=[],
                missing_terms=["data modeling"],
                coverage=0.0,
            ),
            required_certifications=CoverageDimension(),
            required_tools=CoverageDimension(),
        ),
    )

    advice = DefaultResumeUpskillAdvisor().advise(evaluation)

    assert len(advice.upskill_targets) == 1
    item = advice.upskill_targets[0]
    assert item.requirement == "data modeling"
    assert item.requirement_type == "required_skill"
    assert item.gap_status == "unverified"
    assert item.estimated_weeks_low <= item.estimated_weeks_high


def test_upskill_advisor_estimates_missing_timeline_for_plain_gap() -> None:
    ranked_candidate = RankedCandidate(
        rank=1,
        consultant_id="C-999",
        fit_score=60.0,
        reason_codes=["GAP_REQUIRED_SKILL_AIRFLOW"],
    )
    evaluation = DeterministicEvaluation(
        role_id="R-999",
        consultant_id="C-999",
        ranked_candidate=ranked_candidate,
        requirement_coverage=RequirementCoverage(
            required_skills=CoverageDimension(required_terms=["airflow"], matched_terms=[], missing_terms=["airflow"], coverage=0.0),
            required_certifications=CoverageDimension(),
            required_tools=CoverageDimension(),
        ),
    )

    advice = DefaultResumeUpskillAdvisor().advise(evaluation)

    target = next(item for item in advice.upskill_targets if item.requirement == "airflow")
    assert target.gap_status == "missing"
    assert target.estimated_weeks_low >= 4


def test_upskill_advisor_collapses_skill_and_tool_duplicate_into_required_technology() -> None:
    ranked_candidate = RankedCandidate(
        rank=1,
        consultant_id="C-222",
        fit_score=65.0,
        reason_codes=["GAP_REQUIRED_SKILL_SNOWFLAKE"],
    )
    evaluation = DeterministicEvaluation(
        role_id="R-222",
        consultant_id="C-222",
        ranked_candidate=ranked_candidate,
        requirement_coverage=RequirementCoverage(
            required_skills=CoverageDimension(
                required_terms=["snowflake"],
                matched_terms=[],
                missing_terms=["snowflake"],
                coverage=0.0,
            ),
            required_tools=CoverageDimension(
                required_terms=["snowflake"],
                matched_terms=[],
                missing_terms=["snowflake"],
                coverage=0.0,
            ),
            required_certifications=CoverageDimension(),
        ),
    )

    advice = DefaultResumeUpskillAdvisor().advise(evaluation)

    snowflake_gaps = [gap for gap in advice.requirement_gaps if gap.requirement == "snowflake"]
    assert len(snowflake_gaps) == 1
    assert snowflake_gaps[0].requirement_type == "required_technology"
    assert snowflake_gaps[0].source_dimensions == ["required_skills", "required_tools"]

    snowflake_targets = [target for target in advice.upskill_targets if target.requirement == "snowflake"]
    assert len(snowflake_targets) == 1
    assert snowflake_targets[0].requirement_type == "required_technology"


def test_deterministic_scoring_emits_canonical_requirement_group_attribution() -> None:
    role = RoleRequirement(
        role_id="R-500",
        raw={},
        required_skills=["python", "snowflake"],
        required_tools=["snowflake", "databricks"],
        required_certs=["az-104"],
        required_domains=[],
        preferred_skills=[],
        required_years_experience=0,
        remote_or_onsite="Remote",
        location_state="",
        relocation_allowed=True,
        start_date="",
        must_have_constraints="",
        behavioral_importance={},
    )
    consultant = ConsultantProfile(
        consultant_id="C-500",
        raw={},
        normalized_skills=["python"],
        normalized_tools=["databricks"],
        normalized_certs=[],
        normalized_domains=[],
        years_experience=3,
        location_state="NC",
        remote_preference="Remote",
        availability_date="2026-08-01",
        work_authorization_status="US Citizen",
        behavioral_scores={},
    )
    packet = EvaluationPacket(
        role_id="R-500",
        consultant_id="C-500",
        consultant_profile=consultant,
        requirement_coverage=RequirementCoverage(
            required_skills=CoverageDimension(
                required_terms=["python", "snowflake"],
                matched_terms=["python"],
                missing_terms=["snowflake"],
                coverage=0.5,
            ),
            required_tools=CoverageDimension(
                required_terms=["snowflake", "databricks"],
                matched_terms=["databricks"],
                missing_terms=["snowflake"],
                coverage=0.5,
            ),
            required_certifications=CoverageDimension(
                required_terms=["az-104"],
                matched_terms=[],
                missing_terms=["az-104"],
                coverage=0.0,
            ),
        ),
        constraints=ConstraintResult(passes=True, violations=[]),
    )

    evaluations = DefaultDeterministicScoringAgent().rank(role, [packet], top_n=1)

    assert len(evaluations) == 1
    attribution = evaluations[0].score_attribution
    assert attribution.raw_weighted_dimensions
    assert "required_skills" in attribution.raw_weighted_dimensions
    assert "required_certs_tools" in attribution.raw_weighted_dimensions
    assert attribution.attribution_model == "canonical_groups_decompose_requirement_dimensions"
    assert attribution.canonical_scope_dimensions == ["required_skills", "required_certs_tools"]

    tech_group = next(
        group for group in attribution.canonical_requirement_groups if group.requirement_type == "required_technology"
    )
    assert tech_group.required_terms == ["snowflake"]
    assert tech_group.matched_terms == []
    assert tech_group.missing_terms == ["snowflake"]
    assert tech_group.source_dimensions == ["required_skills", "required_tools"]
    assert tech_group.allocated_weight > 0.0

    requirement_total = (
        attribution.raw_weighted_dimensions["required_skills"]
        + attribution.raw_weighted_dimensions["required_certs_tools"]
    )
    assert attribution.requirement_dimension_points_total == round(requirement_total, 4)
    rounding_gap = abs(
        attribution.canonical_weighted_points_total - attribution.requirement_dimension_points_total
    )
    assert rounding_gap <= 0.001
    assert abs(attribution.requirement_canonical_rounding_delta - rounding_gap) <= 0.001
    assert attribution.overall_fit_points_total >= attribution.requirement_dimension_points_total
