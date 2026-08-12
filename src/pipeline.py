"""Milestone A pipeline skeleton.

Milestone A focuses on data loading and normalization, not full ranking.
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from uuid import uuid4

from src.agents import (
    DefaultDeterministicScoringAgent,
    DefaultResumeUpskillAdvisor,
    DeterministicCandidateFitEvaluator,
    DeterministicRankComparisonAgent,
    DiscoveryRequest,
    RetrievalBackedCandidateDiscover,
    RetrievalContext,
)
from src.config import ScoreWeights, Settings, load_settings
from src.io.data_loader import load_consultants_csv, load_roles_csv
from src.io.normalizer import normalize_consultant_record, normalize_role_record
from src.retrieval.candidate_retriever import retrieve_candidates
from src.scoring.ranker import rank_candidates


@dataclass
class PipelineSnapshot:
    """Small payload useful for validating data readiness."""

    roles_count: int
    consultants_count: int
    sample_role_id: str | None
    sample_consultant_id: str | None


@dataclass
class RoleRankingResult:
    """Milestone B output for one requested role."""

    request_id: str
    role_id: str
    top_n: int
    retrieved_k: int
    total_candidates: int
    ranked_candidates: list[dict]
    componentized_mode: bool = False
    rank_comparisons: list[dict] = field(default_factory=list)
    upskill_advice: list[dict] = field(default_factory=list)


class RankingPipeline:
    """Orchestrator placeholder for later milestones."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.settings: Settings = load_settings()
        self.weights = ScoreWeights()
        self.candidate_discover = RetrievalBackedCandidateDiscover()
        self.candidate_fit_evaluator = DeterministicCandidateFitEvaluator()
        self.deterministic_scoring_agent = DefaultDeterministicScoringAgent(self.weights)
        self.rank_comparison_agent = DeterministicRankComparisonAgent()
        self.resume_upskill_advisor = DefaultResumeUpskillAdvisor()

    def _load_normalized_data(self) -> tuple[list, list]:
        dataset_dir = self.project_root / "dataset"
        roles = [normalize_role_record(r) for r in load_roles_csv(dataset_dir / "role_requirements_train.csv")]
        consultants = [
            normalize_consultant_record(c)
            for c in load_consultants_csv(dataset_dir / "consultant_profiles_train.csv")
        ]
        return roles, consultants

    @staticmethod
    def _resolve_role(roles: list, role_id: str):
        for role in roles:
            if role.role_id == role_id:
                return role
        raise ValueError(f"Role not found: {role_id}")

    def run_milestone_a_snapshot(self) -> PipelineSnapshot:
        """Load, normalize, and return counts to verify baseline wiring."""

        roles, consultants = self._load_normalized_data()

        return PipelineSnapshot(
            roles_count=len(roles),
            consultants_count=len(consultants),
            sample_role_id=roles[0].role_id if roles else None,
            sample_consultant_id=consultants[0].consultant_id if consultants else None,
        )

    def run_milestone_b_for_role(
        self,
        role_id: str,
        top_n: int | None = None,
        retrieve_k: int | None = None,
        use_component_pipeline: bool | None = None,
    ) -> RoleRankingResult:
        """Run deterministic retrieval + ranking for one role."""

        roles, consultants = self._load_normalized_data()
        role = self._resolve_role(roles, role_id)

        actual_top_n = top_n if top_n is not None else self.settings.top_n
        actual_retrieve_k = retrieve_k if retrieve_k is not None else self.settings.retrieve_k
        component_mode = (
            use_component_pipeline
            if use_component_pipeline is not None
            else self.settings.component_pipeline_enabled
        )

        if component_mode:
            return self._run_milestone_b_componentized(role, consultants, actual_top_n, actual_retrieve_k)

        retrieved = retrieve_candidates(role, consultants, k=actual_retrieve_k)
        ranked = rank_candidates(role, retrieved, self.weights)
        top_ranked = ranked[:actual_top_n]

        return RoleRankingResult(
            request_id=str(uuid4()),
            role_id=role_id,
            top_n=actual_top_n,
            retrieved_k=len(retrieved),
            total_candidates=len(consultants),
            ranked_candidates=[asdict(candidate) for candidate in top_ranked],
            componentized_mode=False,
        )

    def _run_milestone_b_componentized(self, role, consultants, top_n: int, retrieve_k: int) -> RoleRankingResult:
        """Run Milestone B using the componentized agent architecture."""

        discovered = self.candidate_discover.discover(
            DiscoveryRequest(role=role, consultants=consultants, retrieve_k=retrieve_k)
        )

        packets = []
        for candidate in discovered:
            if candidate.consultant is None:
                continue
            packet = self.candidate_fit_evaluator.evaluate(
                role=role,
                consultant=candidate.consultant,
                retrieval_context=RetrievalContext(
                    retrieval_score=candidate.retrieval_score,
                    retrieval_reasons=candidate.retrieval_reasons,
                ),
            )
            packets.append(packet)

        evaluations = self.deterministic_scoring_agent.rank(role, packets, top_n=top_n)
        comparisons = self.rank_comparison_agent.compare(evaluations)

        advice = [self.resume_upskill_advisor.advise(evaluation) for evaluation in evaluations]

        return RoleRankingResult(
            request_id=str(uuid4()),
            role_id=role.role_id,
            top_n=top_n,
            retrieved_k=len(discovered),
            total_candidates=len(consultants),
            ranked_candidates=[
                {
                    **asdict(evaluation.ranked_candidate),
                    "score_attribution": asdict(evaluation.score_attribution),
                }
                for evaluation in evaluations
            ],
            componentized_mode=True,
            rank_comparisons=[asdict(item) for item in comparisons],
            upskill_advice=[asdict(item) for item in advice],
        )
