import { create } from "zustand";

import { defaultPolicy, type PolicyMode, type PolicyToggles } from "@/types/ranking";

interface PolicyStore {
  policy: PolicyToggles;
  setMode: (field: keyof PolicyToggles, value: PolicyMode) => void;
  setFlag: (field: keyof PolicyToggles, value: boolean) => void;
  reset: () => void;
}

export const usePolicyStore = create<PolicyStore>((set) => ({
  policy: defaultPolicy,
  setMode: (field, value) =>
    set((state) => ({
      policy: {
        ...state.policy,
        [field]: value,
      },
    })),
  setFlag: (field, value) =>
    set((state) => ({
      policy: {
        ...state.policy,
        [field]: value,
      },
    })),
  reset: () => set({ policy: defaultPolicy }),
}));
