from src.config import ScoreWeights
from src.models import ConsultantProfile, RoleRequirement
from src.scoring.ranker import rank_candidates


def test_ranker_returns_deterministic_order() -> None:
    role = RoleRequirement(
        role_id="R-001",
        raw={},
        required_skills=["python", "sql"],
        required_certs=["az-104"],
        required_tools=["jira"],
        required_domains=["banking"],
        preferred_skills=["kubernetes"],
        required_years_experience=5,
        remote_or_onsite="Hybrid",
        location_state="NC",
        relocation_allowed=True,
        start_date="2026-09-01",
        must_have_constraints="US work authorization without sponsorship",
        behavioral_importance={"communication": 5.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 3.0, "leadership": 2.0},
    )
    consultants = [
        ConsultantProfile(
            consultant_id="C-010",
            raw={},
            normalized_skills=["python"],
            normalized_certs=[],
            normalized_tools=[],
            normalized_domains=["retail"],
            years_experience=3,
            location_state="CA",
            availability_date="2026-10-10",
            work_authorization_status="Visa - Sponsorship Required",
            behavioral_scores={"communication": 3.0, "problem_solving": 3.0, "teamwork": 3.0, "adaptability": 3.0, "leadership": 2.0},
        ),
        ConsultantProfile(
            consultant_id="C-002",
            raw={},
            normalized_skills=["python", "sql", "kubernetes"],
            normalized_certs=["az-104"],
            normalized_tools=["jira"],
            normalized_domains=["banking"],
            years_experience=7,
            location_state="NC",
            availability_date="2026-08-20",
            work_authorization_status="US Citizen",
            behavioral_scores={"communication": 4.5, "problem_solving": 4.2, "teamwork": 4.0, "adaptability": 3.8, "leadership": 3.5},
        ),
    ]
    ranked = rank_candidates(role, consultants, ScoreWeights())
    assert [r.consultant_id for r in ranked] == ["C-002", "C-010"]
    assert ranked[0].score_components["required_skills"] >= 1.0
    assert "CONSTRAINT_FAIL_AUTHORIZATION" in ranked[1].risk_flags


def test_ranker_prefers_location_aligned_candidate_when_skills_similar() -> None:
    role = RoleRequirement(
        role_id="R-101",
        raw={},
        required_skills=["python", "sql"],
        required_certs=[],
        required_tools=[],
        required_domains=["banking"],
        preferred_skills=[],
        required_years_experience=5,
        remote_or_onsite="Hybrid (2 days onsite)",
        location_state="NC",
        relocation_allowed=False,
        start_date="2026-09-01",
        must_have_constraints="None",
        behavioral_importance={"communication": 5.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 3.0, "leadership": 2.0},
    )

    aligned = ConsultantProfile(
        consultant_id="C-100",
        raw={},
        normalized_skills=["python", "sql"],
        normalized_certs=[],
        normalized_tools=[],
        normalized_domains=["banking"],
        years_experience=7,
        location_state="NC",
        remote_preference="Hybrid",
        availability_date="2026-08-20",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 4.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 4.0, "leadership": 3.0},
    )
    misaligned = ConsultantProfile(
        consultant_id="C-101",
        raw={},
        normalized_skills=["python", "sql"],
        normalized_certs=[],
        normalized_tools=[],
        normalized_domains=["banking"],
        years_experience=7,
        location_state="CA",
        remote_preference="Remote Only",
        availability_date="2026-08-20",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 4.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 4.0, "leadership": 3.0},
    )

    ranked = rank_candidates(role, [misaligned, aligned], ScoreWeights())

    assert ranked[0].consultant_id == "C-100"
    assert "CONSTRAINT_FAIL_LOCATION" in ranked[1].risk_flags


def test_ranker_treats_nyc_metro_states_as_location_compatible() -> None:
    role = RoleRequirement(
        role_id="R-102",
        raw={},
        required_skills=["python"],
        required_certs=[],
        required_tools=[],
        required_domains=[],
        preferred_skills=[],
        required_years_experience=1,
        remote_or_onsite="Hybrid (2 days onsite)",
        location_state="NY",
        relocation_allowed=False,
        start_date="2026-09-01",
        must_have_constraints="None",
        behavioral_importance={"communication": 1.0, "problem_solving": 1.0, "teamwork": 1.0, "adaptability": 1.0, "leadership": 1.0},
    )
    consultant = ConsultantProfile(
        consultant_id="C-200",
        raw={},
        normalized_skills=["python"],
        normalized_domains=[],
        years_experience=2,
        location_state="NJ",
        remote_preference="Hybrid",
        availability_date="2026-08-20",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 4.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 4.0, "leadership": 4.0},
    )

    ranked = rank_candidates(role, [consultant], ScoreWeights())

    assert ranked[0].consultant_id == "C-200"
    assert "CONSTRAINT_FAIL_LOCATION" not in ranked[0].risk_flags
    assert ranked[0].score_components["availability_location"] > 0.5


def test_ranker_prefers_local_candidate_over_relocation_path() -> None:
    role = RoleRequirement(
        role_id="R-103",
        raw={},
        required_skills=["python", "sql"],
        required_certs=[],
        required_tools=[],
        required_domains=["banking"],
        preferred_skills=[],
        required_years_experience=5,
        remote_or_onsite="Onsite (3 days/week)",
        location_state="TX",
        relocation_allowed=True,
        start_date="2026-09-01",
        must_have_constraints="None",
        behavioral_importance={"communication": 3.0, "problem_solving": 3.0, "teamwork": 3.0, "adaptability": 3.0, "leadership": 3.0},
    )

    local_candidate = ConsultantProfile(
        consultant_id="C-300",
        raw={},
        normalized_skills=["python", "sql"],
        normalized_certs=[],
        normalized_tools=[],
        normalized_domains=["banking"],
        years_experience=7,
        location_state="TX",
        remote_preference="Onsite OK",
        availability_date="2026-08-20",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 4.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 4.0, "leadership": 4.0},
    )
    relocating_candidate = ConsultantProfile(
        consultant_id="C-301",
        raw={},
        normalized_skills=["python", "sql"],
        normalized_certs=[],
        normalized_tools=[],
        normalized_domains=["banking"],
        years_experience=7,
        location_state="CA",
        remote_preference="Onsite OK",
        willing_to_relocate=True,
        availability_date="2026-08-20",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 4.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 4.0, "leadership": 4.0},
    )

    ranked = rank_candidates(role, [relocating_candidate, local_candidate], ScoreWeights())

    assert ranked[0].consultant_id == "C-300"
    assert "LOCATION_RELOCATION_PATH" in ranked[1].reason_codes


def test_ranker_two_pass_keeps_higher_fit_but_moves_ineligible_after_eligible() -> None:
    role = RoleRequirement(
        role_id="R-104",
        raw={},
        required_skills=["python", "sql"],
        required_certs=[],
        required_tools=[],
        required_domains=["banking"],
        preferred_skills=[],
        required_years_experience=5,
        remote_or_onsite="Hybrid (2 days onsite)",
        location_state="NC",
        relocation_allowed=False,
        start_date="2026-09-01",
        must_have_constraints="US work authorization without sponsorship",
        behavioral_importance={"communication": 2.0, "problem_solving": 2.0, "teamwork": 2.0, "adaptability": 2.0, "leadership": 2.0},
    )

    ineligible_high_fit = ConsultantProfile(
        consultant_id="C-401",
        raw={},
        normalized_skills=["python", "sql"],
        normalized_domains=["banking"],
        years_experience=8,
        location_state="CA",
        remote_preference="Remote Only",
        availability_date="2026-08-15",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 4.5, "problem_solving": 4.5, "teamwork": 4.5, "adaptability": 4.5, "leadership": 4.5},
    )

    eligible_lower_fit = ConsultantProfile(
        consultant_id="C-402",
        raw={},
        normalized_skills=["python"],
        normalized_domains=["banking"],
        years_experience=5,
        location_state="NC",
        remote_preference="Hybrid",
        availability_date="2026-08-20",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 3.0, "problem_solving": 3.0, "teamwork": 3.0, "adaptability": 3.0, "leadership": 3.0},
    )

    ranked = rank_candidates(role, [ineligible_high_fit, eligible_lower_fit], ScoreWeights())

    assert ranked[0].consultant_id == "C-402"
    assert ranked[0].eligibility_status == "passed"
    assert ranked[0].eligibility_basis == "hard_constraints_only"
    assert ranked[0].ranking_tier == 0
    assert "CONSTRAINT_FAIL_LOCATION" in ranked[1].risk_flags
    assert ranked[1].eligibility_status == "failed"
    assert ranked[1].ranking_tier == 1
    assert ranked[0].ranking_key[0] < ranked[1].ranking_key[0]
    assert ranked[1].fit_score > ranked[0].fit_score


def test_ranker_extracts_required_skills_from_resume_and_project_evidence() -> None:
    role = RoleRequirement(
        role_id="R-201",
        raw={},
        required_skills=["airflow", "snowflake"],
        required_certs=[],
        required_tools=[],
        required_domains=["healthcare"],
        preferred_skills=[],
        required_years_experience=1,
        remote_or_onsite="Remote",
        location_state="TN",
        relocation_allowed=False,
        start_date="2026-09-01",
        must_have_constraints="Prior healthcare data experience is mandatory.",
        behavioral_importance={"communication": 1.0, "problem_solving": 1.0, "teamwork": 1.0, "adaptability": 1.0, "leadership": 1.0},
    )

    consultant = ConsultantProfile(
        consultant_id="C-500",
        raw={
            "project_experience_summary": "Built Spark and Airflow pipelines feeding a Snowflake warehouse.",
            "resume_text": "Delivered healthcare analytics data pipelines.",
        },
        normalized_skills=["spark"],
        normalized_domains=["healthcare"],
        years_experience=5,
        location_state="TN",
        remote_preference="Remote Preferred",
        availability_date="2026-08-10",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 4.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 4.0, "leadership": 4.0},
    )

    ranked = rank_candidates(role, [consultant], ScoreWeights())

    assert ranked[0].score_components["required_skills"] == 1.0
    assert "GAP_REQUIRED_SKILL_AIRFLOW" not in ranked[0].reason_codes
    assert "GAP_REQUIRED_SKILL_SNOWFLAKE" not in ranked[0].reason_codes


def test_ranker_adds_review_potential_signals_without_marking_requirement_met() -> None:
    role = RoleRequirement(
        role_id="R-202",
        raw={},
        required_skills=["airflow"],
        required_certs=["aws certified"],
        required_tools=["snowflake"],
        required_domains=[],
        preferred_skills=[],
        required_years_experience=1,
        remote_or_onsite="Remote",
        location_state="TN",
        relocation_allowed=False,
        start_date="2026-09-01",
        must_have_constraints="None",
        behavioral_importance={"communication": 1.0, "problem_solving": 1.0, "teamwork": 1.0, "adaptability": 1.0, "leadership": 1.0},
    )

    consultant = ConsultantProfile(
        consultant_id="C-501",
        raw={
            "project_experience_summary": "Implemented workflow orchestration with Prefect and designed modern warehouse models.",
            "resume_text": "Completed cloud certification prep and earned a provider badge.",
        },
        normalized_skills=["python"],
        normalized_tools=["prefect"],
        years_experience=4,
        location_state="TN",
        remote_preference="Remote Preferred",
        availability_date="2026-08-10",
        work_authorization_status="US Citizen",
        behavioral_scores={"communication": 4.0, "problem_solving": 4.0, "teamwork": 4.0, "adaptability": 4.0, "leadership": 4.0},
    )

    ranked = rank_candidates(role, [consultant], ScoreWeights())

    assert ranked[0].score_components["required_skills"] == 0.0
    assert "GAP_REQUIRED_SKILL_AIRFLOW" in ranked[0].reason_codes
    assert "REVIEW_POTENTIAL_SKILL_AIRFLOW" in ranked[0].reason_codes
    assert "REVIEW_POTENTIAL_TOOL_SNOWFLAKE" in ranked[0].reason_codes
    assert "REVIEW_POTENTIAL_CERT_AWS_CERTIFIED" in ranked[0].reason_codes
