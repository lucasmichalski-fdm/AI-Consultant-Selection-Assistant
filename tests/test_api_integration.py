from pathlib import Path

from src.api.server import PolicyToggles, _to_ranking_policy
from src.pipeline import RankingPipeline
from src.scoring.policy import RankingPolicy


def test_to_ranking_policy_maps_all_fields() -> None:
    policy = _to_ranking_policy(
        PolicyToggles(
            locationMode="soft",
            enforceOfficeSchedule=False,
            allowRelocationPath=False,
            startDateMode="ignore",
            authorizationMode="hard",
            experienceMode="soft",
            certificationMode="hard",
            domainMode="ignore",
        )
    )

    assert policy.location_mode == "soft"
    assert policy.enforce_office_schedule is False
    assert policy.allow_relocation_path is False
    assert policy.start_date_mode == "ignore"
    assert policy.authorization_mode == "hard"
    assert policy.experience_mode == "soft"
    assert policy.certification_mode == "hard"
    assert policy.domain_mode == "ignore"


def test_pipeline_forwards_policy_to_ranker(monkeypatch) -> None:
    root = Path(__file__).resolve().parents[1]
    pipeline = RankingPipeline(project_root=root)

    captured: dict[str, RankingPolicy | None] = {"policy": None}

    def fake_rank_candidates(role, consultants, weights, policy=None):
        captured["policy"] = policy
        return []

    monkeypatch.setattr("src.pipeline.rank_candidates", fake_rank_candidates)

    sample_policy = RankingPolicy(location_mode="soft", experience_mode="ignore")
    result = pipeline.run_milestone_b_for_role("R-001", top_n=5, retrieve_k=10, policy=sample_policy)

    assert result.role_id == "R-001"
    assert captured["policy"] == sample_policy
