import { useState } from "react";
import { SectorList } from "./components/SectorList";
import { TickerList } from "./components/TickerList";
import { ChatPanel } from "./components/ChatPanel";

function App() {
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">StockGPT</h1>
          <p className="text-sm text-gray-500">Agentic AI for stock market research</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Ask</h2>
          <ChatPanel />
        </section>

        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Sectors</h2>
          <SectorList onSectorClick={setSelectedSector} />
        </section>

        {selectedSector && (
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-gray-900">{selectedSector}</h2>
              <button
                onClick={() => setSelectedSector(null)}
                className="text-sm text-gray-500 hover:text-gray-900"
              >
                Clear
              </button>
            </div>
            <TickerList sector={selectedSector} />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;