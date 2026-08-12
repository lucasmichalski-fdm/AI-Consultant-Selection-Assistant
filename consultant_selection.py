from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class JobDescription:
    required_skills: list[str]
    preferred_skills: list[str]
    required_certifications: list[str]
    behavior_requirements: dict[str, float]


@dataclass(frozen=True)
class Applicant:
    name: str
    skills: list[str]
    certifications: list[str]
    behavior_scores: dict[str, float]


@dataclass(frozen=True)
class ApplicantRanking:
    name: str
    score: float
    recommendation: str
    matched_required_skills: list[str]
    missing_required_skills: list[str]
    skill_gaps: list[str]
    explanation: str


def _to_normalized_set(values: Iterable[str]) -> set[str]:
    return {value.strip().lower() for value in values if value and value.strip()}


def rank_applicants(job_description: JobDescription, applicants: list[Applicant]) -> list[ApplicantRanking]:
    required_skills = _to_normalized_set(job_description.required_skills)
    preferred_skills = _to_normalized_set(job_description.preferred_skills)
    required_certifications = _to_normalized_set(job_description.required_certifications)

    ranked: list[ApplicantRanking] = []

    for applicant in applicants:
        applicant_skills = _to_normalized_set(applicant.skills)
        applicant_certifications = _to_normalized_set(applicant.certifications)

        matched_required_skills = sorted(required_skills & applicant_skills)
        missing_required_skills = sorted(required_skills - applicant_skills)

        matched_preferred_skills = preferred_skills & applicant_skills
        missing_preferred_skills = sorted(preferred_skills - applicant_skills)

        matched_certifications = required_certifications & applicant_certifications
        missing_certifications = sorted(required_certifications - applicant_certifications)

        required_skill_score = (
            (len(matched_required_skills) / len(required_skills)) * 50 if required_skills else 50
        )
        preferred_skill_score = (
            (len(matched_preferred_skills) / len(preferred_skills)) * 20 if preferred_skills else 20
        )
        certification_score = (
            (len(matched_certifications) / len(required_certifications)) * 20 if required_certifications else 20
        )

        behavior_scores = []
        for trait, min_required in job_description.behavior_requirements.items():
            actual_score = applicant.behavior_scores.get(trait, 0)
            if min_required <= 0:
                behavior_scores.append(1.0)
            else:
                behavior_scores.append(min(actual_score / min_required, 1.0))
        behavior_score = (sum(behavior_scores) / len(behavior_scores) * 10) if behavior_scores else 10

        total_score = round(required_skill_score + preferred_skill_score + certification_score + behavior_score, 2)

        if not missing_required_skills and not missing_certifications and total_score >= 80:
            recommendation = "Strong fit"
        elif total_score >= 60:
            recommendation = "Potential fit"
        else:
            recommendation = "Not recommended"

        skill_gaps = sorted(set(missing_required_skills + missing_preferred_skills + missing_certifications))
        explanation = (
            f"Matched required skills: {', '.join(matched_required_skills) or 'none'}; "
            f"Missing required skills: {', '.join(missing_required_skills) or 'none'}; "
            f"Missing certifications: {', '.join(missing_certifications) or 'none'}; "
            f"Recommendation: {recommendation}."
        )

        ranked.append(
            ApplicantRanking(
                name=applicant.name,
                score=total_score,
                recommendation=recommendation,
                matched_required_skills=matched_required_skills,
                missing_required_skills=missing_required_skills,
                skill_gaps=skill_gaps,
                explanation=explanation,
            )
        )

    return sorted(ranked, key=lambda item: item.score, reverse=True)
