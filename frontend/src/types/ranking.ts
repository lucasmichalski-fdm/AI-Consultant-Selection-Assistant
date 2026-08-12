export type PolicyMode = "hard" | "soft" | "ignore";

export interface PolicyToggles {
  locationMode: PolicyMode;
  enforceOfficeSchedule: boolean;
  allowRelocationPath: boolean;
  startDateMode: PolicyMode;
  authorizationMode: PolicyMode;
  experienceMode: PolicyMode;
  certificationMode: PolicyMode;
  domainMode: PolicyMode;
}

export interface RunRankingRequest {
  roleId: string;
  topN: number;
  retrieveK: number;
  componentized: boolean;
  policy: PolicyToggles;
}

export interface RankedCandidate {
  rank: number;
  consultant_id: string;
  fit_score: number;
  eligibility_status?: string;
  eligibility_basis?: string;
  eligibility_explanation?: string;
  ranking_tier?: number;
  risk_tier?: number;
  ranking_key?: Array<string | number>;
  ranking_key_semantics?: string;
  score_components: Record<string, number>;
  score_attribution?: Record<string, unknown>;
  reason_codes: string[];
  risk_flags: string[];
}

export interface RankComparison {
  [key: string]: unknown;
}

export interface RequirementGap {
  requirement: string;
  requirement_type: string;
  mandatory?: boolean;
  mandatory_scope?: string;
  gates_eligibility?: boolean;
  gap_status?: string;
  source_dimensions?: string[];
}

export interface UpskillTarget {
  requirement: string;
  requirement_type: string;
  gap_status?: string;
  estimated_weeks_low?: number;
  estimated_weeks_high?: number;
}

export interface UpskillAdvice {
  consultant_id?: string;
  role_id?: string;
  requirement_gaps?: RequirementGap[];
  upskill_targets?: UpskillTarget[];
}

export interface RankingRunResponse {
  milestone: string;
  request_id: string;
  role_id: string;
  top_n: number;
  retrieved_k: number;
  total_candidates: number;
  ranked_candidates: RankedCandidate[];
  componentized_mode?: boolean;
  rank_comparisons?: RankComparison[];
  upskill_advice?: UpskillAdvice[];
  generated_at: string;
  applied_policy: PolicyToggles;
}

export interface RoleOption {
  id: string;
  title: string;
  location: string;
  mode: string;
}

export const defaultPolicy: PolicyToggles = {
  locationMode: "hard",
  enforceOfficeSchedule: true,
  allowRelocationPath: true,
  startDateMode: "hard",
  authorizationMode: "hard",
  experienceMode: "hard",
  certificationMode: "soft",
  domainMode: "soft",
};
