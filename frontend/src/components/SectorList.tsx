import { useSectors } from "../hooks/useSectors";

interface SectorListProps {
  onSectorClick?: (sector: string) => void;
}

/**
 * Displays the list of GICS sectors with ticker counts.
 * Clicking a sector calls onSectorClick (parent component decides what to do).
 */
export function SectorList({ onSectorClick }: SectorListProps) {
  const { data, isLoading, isError, error } = useSectors();

  if (isLoading) {
    return (
      <div className="text-gray-500 text-sm">Loading sectors...</div>
    );
  }

  if (isError) {
    return (
      <div className="text-red-600 text-sm">
        Error loading sectors: {error instanceof Error ? error.message : "Unknown error"}
      </div>
    );
  }

  if (!data || data.sectors.length === 0) {
    return (
      <div className="text-gray-500 text-sm">No sectors found.</div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {data.sectors.map((s) => (
        <button
          key={s.sector}
          onClick={() => onSectorClick?.(s.sector)}
          className="text-left bg-white hover:bg-blue-50 border border-gray-200 rounded-lg px-4 py-3 transition-colors"
        >
          <div className="font-medium text-gray-900">{s.sector}</div>
          <div className="text-sm text-gray-500">{s.count} tickers</div>
        </button>
      ))}
    </div>
  );
}
