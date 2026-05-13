import { useUniverse } from "../hooks/useUniverse";

interface TickerListProps {
  sector: string;
}

/**
 * Displays the list of tickers for a given sector.
 * Renders loading / error / empty / success states.
 */
export function TickerList({ sector }: TickerListProps) {
  const { data, isLoading, isError, error } = useUniverse(sector);

  if (isLoading) {
    return (
      <div className="text-gray-500 text-sm">Loading tickers...</div>
    );
  }

  if (isError) {
    return (
      <div className="text-red-600 text-sm">
        Error loading tickers: {error instanceof Error ? error.message : "Unknown error"}
      </div>
    );
  }

  if (!data || data.rows.length === 0) {
    return (
      <div className="text-gray-500 text-sm">No tickers found.</div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="text-left px-4 py-2 font-medium text-gray-600">Ticker</th>
            <th className="text-left px-4 py-2 font-medium text-gray-600">Company</th>
            <th className="text-left px-4 py-2 font-medium text-gray-600">Industry</th>
          </tr>
        </thead>
        <tbody>
          {data.rows.map((row) => (
            <tr key={row.ticker} className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
              <td className="px-4 py-2 font-mono font-medium text-gray-900">{row.ticker}</td>
              <td className="px-4 py-2 text-gray-700">{row.company_name}</td>
              <td className="px-4 py-2 text-gray-500">{row.industry ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
        {data.count} ticker{data.count === 1 ? "" : "s"} shown
      </div>
    </div>
  );
}
