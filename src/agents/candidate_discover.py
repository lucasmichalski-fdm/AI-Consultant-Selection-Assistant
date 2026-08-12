"""Candidate discovery component interfaces and starter implementation."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.models import ConsultantProfile, RoleRequirement
from src.retrieval.candidate_retriever import retrieve_candidates


@dataclass
class DiscoveryRequest:
    """Batch discovery request from the application layer."""

    role: RoleRequirement
    consultants: list[ConsultantProfile]
    retrieve_k: int = 25


@dataclass
class DiscoveredCandidate:
    """Potentially relevant candidate with retrieval metadata."""

    consultant_id: str
    retrieval_score: float
    retrieval_reasons: list[str] = field(default_factory=list)
    consultant: ConsultantProfile | None = None


class CandidateDiscover:
    """Interface for high-recall candidate discovery."""

    def discover(self, request: DiscoveryRequest) -> list[DiscoveredCandidate]:
        raise NotImplementedError


class RetrievalBackedCandidateDiscover(CandidateDiscover):
    """Default discoverer backed by existing deterministic retrieval."""

    def discover(self, request: DiscoveryRequest) -> list[DiscoveredCandidate]:
        retrieved = retrieve_candidates(request.role, request.consultants, k=request.retrieve_k)
        total = len(retrieved) or 1

        discovered: list[DiscoveredCandidate] = []
        for idx, consultant in enumerate(retrieved, start=1):
            # Rank-derived relevance keeps this scaffold deterministic.
            retrieval_score = round((total - idx + 1) / total, 4)
            discovered.append(
                DiscoveredCandidate(
                    consultant_id=consultant.consultant_id,
                    retrieval_score=retrieval_score,
                    retrieval_reasons=["retrieval_top_k"],
                    consultant=consultant,
                )
            )
        return discovered
