import { useQuery } from "@tanstack/react-query";

import { fetchRoles } from "@/services/rankingService";

export function useRoles() {
  return useQuery({
    queryKey: ["roles"],
    queryFn: fetchRoles,
  });
}
