import { useQuery } from "@tanstack/react-query";
import { listSectors } from "../api/client";

/**
 * Fetches the list of GICS sectors with ticker counts.
 *
 * Returns:
 *   - data: SectorsResponse | undefined
 *   - isLoading: boolean (true on first fetch)
 *   - isError: boolean
 *   - error: Error | null
 *
 * TanStack Query handles caching, deduplication, and refetching automatically.
 * Multiple components can call useSectors() — only one network request fires.
 */
export function useSectors() {
  return useQuery({
    queryKey: ["sectors"],
    queryFn: listSectors,
  });
}
