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
    assert ranked[0].fit_score > ranked[1].fit_score
    assert ranked[0].score_components["required_skills"] >= 1.0
    assert "CONSTRAINT_FAIL_AUTHORIZATION" in ranked[1].risk_flags
