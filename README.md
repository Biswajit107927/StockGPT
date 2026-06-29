# 📈 StockGPT
![CI](https://github.com/Biswajit107927/StockGPT/actions/workflows/ci.yml/badge.svg)

An AI-powered research agent for stock market analysis. Ask questions in natural language — get real-time data, charts, and insights powered by Google Gemini with automatic fallback to Groq Llama 3.3.

## 🧠 How It Works

```
User Question
      │
      ▼
┌─────────────────┐
│  Gemini 2.5     │  ← Primary LLM (native function-calling)
│  Flash          │  ← Fallback: Groq Llama 3.3 70B
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Tool Router    │  ← Agent decides which tools to call
└─────────────────┘
      │
      ├── get_stock_price()      → yfinance (real-time quotes)
      ├── get_stock_history()    → yfinance (OHLCV time series)
      ├── get_company_info()     → yfinance (fundamentals, sector, PE)
      ├── search_news()          → DuckDuckGo (latest headlines)
      └── calculate()            → Safe math evaluation
      │
      ▼
┌─────────────────┐
│  Self-Correction│  ← Agent retries with refined params on failure
└─────────────────┘
      │
      ▼
   Response + Citations
```

The agent uses **Gen 3 architecture** — native function-calling (no regex parsing), self-correction on tool failures, and structured output with source attribution.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11+) |
| AI Agent | Google Gemini 2.5 Flash (primary) + Groq Llama 3.3 70B (fallback) |
| Tool Framework | Native function-calling (no LangChain) |
| Data Store | DuckDB (conversation history + cached queries) |
| Market Data | yfinance (real-time + historical) |
| Frontend | React + TypeScript + Vite |
| Containerization | Docker Compose |

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Biswajit107927/StockGPT.git
cd StockGPT

# Set up environment
cp .env.example .env
# Add your GOOGLE_API_KEY and/or GROQ_API_KEY to .env

# Run with Docker
docker-compose up
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

### Run without Docker

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 📂 Project Structure

```
StockGPT/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + routes
│   │   ├── agent.py         # Gemini agent with function-calling
│   │   ├── tools/           # 5 tools (price, history, info, news, calc)
│   │   └── models.py        # Pydantic schemas
│   ├── tests/               # Eval harness for response quality
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main chat interface
│   │   └── components/      # UI components
│   └── package.json
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── learning/            # Design journal
├── docker-compose.yml
└── .env.example
```

## 🔧 Agent Tools

| Tool | Input | Output |
|------|-------|--------|
| `get_stock_price` | ticker symbol | Current price, change %, volume |
| `get_stock_history` | ticker, period, interval | OHLCV DataFrame |
| `get_company_info` | ticker | Market cap, PE, sector, summary |
| `search_news` | query | Top 5 recent headlines with URLs |
| `calculate` | math expression | Evaluated result (safe eval) |

## 🏗️ Architecture Decisions

Key design choices documented in `docs/adr/`:

- **Why Gemini over OpenAI** — Native function-calling with structured output, generous free tier for development
- **Why no LangChain** — Direct SDK gives full control over retry logic and tool routing; fewer dependencies
- **Why DuckDB** — Embedded, zero-config, SQL-native — perfect for caching stock queries and conversation history
- **Why dual-LLM fallback** — Gemini for quality, Groq for speed when Gemini rate-limits

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

The eval harness tests response quality across categories:
- Factual accuracy (price lookups)
- Multi-tool orchestration (compare two stocks)
- Edge cases (invalid tickers, future dates)

## 📄 License

MIT
