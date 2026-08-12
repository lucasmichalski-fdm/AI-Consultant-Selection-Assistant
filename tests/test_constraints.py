from src.models import ConsultantProfile, RoleRequirement
from src.scoring.constraints import evaluate_constraints


def test_constraints_pass_when_core_rules_met() -> None:
    role = RoleRequirement(
        role_id="R-001",
        raw={},
        required_years_experience=5,
        start_date="2026-09-01",
        remote_or_onsite="Hybrid (3 days onsite)",
        location_state="NC",
        relocation_allowed=True,
        must_have_constraints="US work authorization without sponsorship",
    )
    consultant = ConsultantProfile(
        consultant_id="C-001",
        raw={},
        years_experience=6,
        availability_date="2026-08-15",
        location_state="NC",
        willing_to_relocate=False,
        work_authorization_status="US Citizen",
    )
    passes, violations = evaluate_constraints(role, consultant)
    assert passes is True
    assert violations == []


def test_constraints_fail_on_multiple_rules() -> None:
    role = RoleRequirement(
        role_id="R-002",
        raw={},
        required_years_experience=7,
        start_date="2026-09-01",
        remote_or_onsite="Onsite",
        location_state="TX",
        relocation_allowed=False,
        must_have_constraints="US work authorization without sponsorship",
    )
    consultant = ConsultantProfile(
        consultant_id="C-002",
        raw={},
        years_experience=4,
        availability_date="2026-10-01",
        location_state="CA",
        willing_to_relocate=False,
        work_authorization_status="Visa - Sponsorship Required",
    )
    passes, violations = evaluate_constraints(role, consultant)
    assert passes is False
    assert "CONSTRAINT_FAIL_EXPERIENCE_MIN" in violations
    assert "CONSTRAINT_FAIL_START_DATE" in violations
    assert "CONSTRAINT_FAIL_LOCATION" in violations
    assert "CONSTRAINT_FAIL_AUTHORIZATION" in violations


def test_constraints_fail_when_remote_only_candidate_for_onsite_role() -> None:
    role = RoleRequirement(
        role_id="R-003",
        raw={},
        required_years_experience=3,
        start_date="2026-09-01",
        remote_or_onsite="Hybrid (2 days onsite)",
        location_state="NY",
        relocation_allowed=False,
        must_have_constraints="None",
    )
    consultant = ConsultantProfile(
        consultant_id="C-003",
        raw={},
        years_experience=6,
        availability_date="2026-08-20",
        location_state="NY",
        willing_to_relocate=False,
        remote_preference="Remote Only",
        work_authorization_status="US Citizen",
    )
    passes, violations = evaluate_constraints(role, consultant)
    assert passes is False
    assert "CONSTRAINT_FAIL_LOCATION" in violations
