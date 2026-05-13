import { useQuery } from "@tanstack/react-query";
import { listUniverse } from "../api/client";

/**
 * Fetches tickers from the universe, optionally filtered by sector.
 *
 * Pass `enabled: false` semantics via the `sector` parameter being null —
 * the hook returns idle state without fetching.
 *
 * Cache key includes the sector so different sectors are cached separately.
 */
export function useUniverse(sector: string | null, limit: number = 100) {
  return useQuery({
    queryKey: ["universe", sector, limit],
    queryFn: () => listUniverse({ sector: sector ?? undefined, limit }),
    enabled: sector !== null,
  });
}
