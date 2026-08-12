import { defaultPolicy, type PolicyToggles, type RoleOption, type RunRankingRequest, type RankingRunResponse } from "@/types/ranking";
import { apiClient } from "@/services/apiClient";
import { mockRoles, mockRun } from "@/data/mockData";

const useMockData = (import.meta.env.VITE_USE_MOCK_DATA ?? "true") === "true";

function normalizeRunResponse(run: Partial<RankingRunResponse>, request: RunRankingRequest): RankingRunResponse {
  return {
    milestone: run.milestone ?? "B",
    request_id: run.request_id ?? "",
    role_id: run.role_id ?? request.roleId,
    top_n: run.top_n ?? request.topN,
    retrieved_k: run.retrieved_k ?? request.retrieveK,
    total_candidates: run.total_candidates ?? 0,
    ranked_candidates: run.ranked_candidates ?? [],
    componentized_mode: run.componentized_mode ?? false,
    rank_comparisons: run.rank_comparisons ?? [],
    upskill_advice: run.upskill_advice ?? [],
    generated_at: run.generated_at ?? new Date().toISOString(),
    applied_policy: run.applied_policy ?? request.policy ?? defaultPolicy,
  };
}

export async function fetchRoles(): Promise<RoleOption[]> {
  if (useMockData) {
    return mockRoles;
  }
  return apiClient<RoleOption[]>("/roles");
}

export async function runRanking(request: RunRankingRequest): Promise<RankingRunResponse> {
  if (useMockData) {
    return normalizeRunResponse({
      ...mockRun,
      role_id: request.roleId,
      top_n: request.topN,
      retrieved_k: request.retrieveK,
      generated_at: new Date().toISOString(),
      applied_policy: request.policy ?? defaultPolicy,
    }, request);
  }

  const payload = {
    role_id: request.roleId,
    top_n: request.topN,
    retrieve_k: request.retrieveK,
    policy: request.policy,
  };

  const response = await apiClient<Partial<RankingRunResponse>>("/rank", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  return normalizeRunResponse(response, request);
}

export const policyLabels: Record<keyof PolicyToggles, string> = {
  locationMode: "Location Constraint",
  enforceOfficeSchedule: "Office Schedule Compatibility",
  allowRelocationPath: "Allow Relocation Path",
  startDateMode: "Start Date Constraint",
  authorizationMode: "Work Authorization",
  experienceMode: "Minimum Experience",
  certificationMode: "Certifications",
  domainMode: "Domain Experience",
};
