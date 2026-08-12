"""Agent component interfaces for the consultant selection architecture."""

from src.agents.candidate_discover import (
    CandidateDiscover,
    DiscoveryRequest,
    DiscoveredCandidate,
    RetrievalBackedCandidateDiscover,
)
from src.agents.candidate_fit_evaluator import (
    CandidateFitEvaluator,
    ConfirmedEvidence,
    CoverageDimension,
    ConstraintResult,
    DeterministicCandidateFitEvaluator,
    EvaluationPacket,
    PotentialUnconfirmedEvidence,
    RequirementCoverage,
    RetrievalContext,
)
from src.agents.deterministic_scoring_agent import (
    CanonicalRequirementAttribution,
    DefaultDeterministicScoringAgent,
    DeterministicEvaluation,
    DeterministicScoreAttribution,
    DeterministicScoringAgent,
)
from src.agents.rank_comparison_agent import (
    DeterministicRankComparisonAgent,
    RankComparison,
    RankComparisonAgent,
)
from src.agents.resume_upskill_advisor import (
    DefaultResumeUpskillAdvisor,
    RequirementGap,
    ResumeUpskillAdvisor,
    UpskillTarget,
    UpskillAdvice,
)

__all__ = [
    "CandidateDiscover",
    "DiscoveryRequest",
    "DiscoveredCandidate",
    "RetrievalBackedCandidateDiscover",
    "CandidateFitEvaluator",
    "RetrievalContext",
    "ConfirmedEvidence",
    "CoverageDimension",
    "PotentialUnconfirmedEvidence",
    "RequirementCoverage",
    "ConstraintResult",
    "EvaluationPacket",
    "DeterministicCandidateFitEvaluator",
    "DeterministicScoringAgent",
    "DefaultDeterministicScoringAgent",
    "DeterministicEvaluation",
    "DeterministicScoreAttribution",
    "CanonicalRequirementAttribution",
    "RankComparisonAgent",
    "RankComparison",
    "DeterministicRankComparisonAgent",
    "ResumeUpskillAdvisor",
    "RequirementGap",
    "UpskillTarget",
    "UpskillAdvice",
    "DefaultResumeUpskillAdvisor",
]
