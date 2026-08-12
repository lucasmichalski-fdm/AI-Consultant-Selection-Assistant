from pathlib import Path

from src.pipeline import RankingPipeline


def test_pipeline_snapshot_has_data() -> None:
    root = Path(__file__).resolve().parents[1]
    snapshot = RankingPipeline(project_root=root).run_milestone_a_snapshot()
    assert snapshot.roles_count > 0
    assert snapshot.consultants_count > 0


def test_pipeline_milestone_b_returns_ranked_candidates() -> None:
    root = Path(__file__).resolve().parents[1]
    result = RankingPipeline(project_root=root).run_milestone_b_for_role("R-001", top_n=5, retrieve_k=25)
    assert result.role_id == "R-001"
    assert len(result.ranked_candidates) == 5


def test_pipeline_milestone_b_componentized_mode_returns_advisory_outputs() -> None:
    root = Path(__file__).resolve().parents[1]
    result = RankingPipeline(project_root=root).run_milestone_b_for_role(
        "R-001",
        top_n=5,
        retrieve_k=25,
        use_component_pipeline=True,
    )
    assert result.role_id == "R-001"
    assert result.componentized_mode is True
    assert len(result.ranked_candidates) == 5
    assert isinstance(result.rank_comparisons, list)
    assert isinstance(result.upskill_advice, list)
    first_candidate = result.ranked_candidates[0]
    assert "score_attribution" in first_candidate
    assert "raw_weighted_dimensions" in first_candidate["score_attribution"]
    assert "canonical_requirement_groups" in first_candidate["score_attribution"]
