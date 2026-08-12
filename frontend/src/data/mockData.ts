import type { RankingRunResponse, RoleOption } from "@/types/ranking";

export const mockRoles: RoleOption[] = [
  { id: "R-003", title: "Data Engineer - Clinical Analytics", location: "Nashville, TN", mode: "Hybrid (2 days onsite)" },
  { id: "R-005", title: "DevOps Engineer - Platform Reliability", location: "Houston, TX", mode: "Onsite (3 days/week)" },
  { id: "R-020", title: "Software Developer in Test - Field Ops", location: "Dallas, TX", mode: "Onsite (3 days/week)" },
];

export const mockRun: Omit<RankingRunResponse, "generated_at" | "applied_policy"> = {
  milestone: "B",
  request_id: "mock-request-id",
  role_id: "R-003",
  top_n: 5,
  retrieved_k: 25,
  total_candidates: 240,
  ranked_candidates: [
    {
      rank: 1,
      consultant_id: "C-035",
      fit_score: 40,
      score_components: {
        required_skills: 0.5,
        required_certs_tools: 0.5,
        domain: 1,
        preferred_skills: 0.6667,
        experience: 1,
        behavioral: 0.7211,
        availability_location: 0.79,
        prior_rating: 0.94,
      },
      reason_codes: [
        "REQ_SKILLS_WEAK",
        "GAP_REQUIRED_SKILL_AIRFLOW",
        "GAP_REQUIRED_SKILL_PYTHON",
        "DOMAIN_STRONG_FIT",
        "EXP_MEETS_TARGET",
        "LOCATION_RELOCATION_PATH",
      ],
      risk_flags: [],
    },
    {
      rank: 2,
      consultant_id: "C-146",
      fit_score: 40,
      score_components: {
        required_skills: 0.5,
        required_certs_tools: 0.5,
        domain: 0,
        preferred_skills: 0.3333,
        experience: 1,
        behavioral: 0.6889,
        availability_location: 0.7112,
        prior_rating: 0.5,
      },
      reason_codes: ["REQ_SKILLS_WEAK", "LOCATION_RELOCATION_PATH"],
      risk_flags: [],
    },
  ],
};
