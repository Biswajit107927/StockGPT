// Mirrors the backend's Pydantic models in app/api/universe.py
// If the backend response shape changes, update this file in lockstep.

export interface UniverseRow {
  ticker: string;
  company_name: string;
  sector: string | null;
  industry: string | null;
  market_cap: number | null;
  index_membership: string | null;
}

export interface UniverseResponse {
  count: number;
  rows: UniverseRow[];
}

export interface SectorCount {
  sector: string;
  count: number;
}

export interface SectorsResponse {
  sectors: SectorCount[];
}
