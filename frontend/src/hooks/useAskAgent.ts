import { useMutation } from "@tanstack/react-query";
import { askAgent } from "../api/client";
import type { AskRequest, AskResponse } from "../types/agent";

/**
 * Hook for asking the agent a question.
 *
 * Uses useMutation (not useQuery) because asking the agent is a one-shot
 * write-like action with side effects (LLM tokens consumed, traces logged),
 * not a cacheable read.
 *
 * Returns mutate() which fires the request, plus state flags.
 */
export function useAskAgent() {
  return useMutation<AskResponse, Error, AskRequest>({
    mutationFn: askAgent,
  });
}
