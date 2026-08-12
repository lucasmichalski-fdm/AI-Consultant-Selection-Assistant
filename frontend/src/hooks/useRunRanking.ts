import { useMutation } from "@tanstack/react-query";

import { runRanking } from "@/services/rankingService";
import type { RunRankingRequest } from "@/types/ranking";

export function useRunRanking() {
  return useMutation({
    mutationFn: (request: RunRankingRequest) => runRanking(request),
  });
}
