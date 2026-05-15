# StockGPT Learning Log

A running record of concepts, patterns, and skills developed while
building StockGPT. Updated weekly.

---

## Day 1 — Foundation: Backend, DuckDB, Universe Ingestion

### AI Engineering Strategy and Career

- **Competency map for AI engineering roles**: Tier 1 non-negotiables
  (agentic AI, RAG, prompt engineering, evals, observability), Tier 2
  differentiators (MCP, fine-tuning, vector databases), Tier 3 senior
  signals (system design, ADRs, cost optimization).
- **Barbell market structure**: high demand for AI engineers,
  saturation in the middle, DE background as moat not liability.
- **Project as vehicle**: StockGPT exists to develop competencies and
  signal them, not as an end in itself.
- **Resume timing discipline**: don't list a project before it has
  substance; calibrated descriptions at Week 4 vs Week 6.
- **V1 / V2 / V3 thinking**: ship a focused V1, evolve later; most
  projects die by trying to build V3 from the start.
- **Two-project portfolio strategy**: StockGPT for agents + MCP depth;
  separate small RAG lab to close the RAG gap if needed.

### System Architecture and Design

- **Three-layer architecture**: clients (React UI, MCP clients),
  backend (FastAPI agent loop + tools), data layer (DuckDB +
  knowledge base + cache).
- **Tool registry pattern**: narrow, typed Python functions as the
  agent's capabilities; tools as single source of truth, exposed
  through multiple entry points.
- **Direct function calls vs MCP**: when to use each. Option B
  (direct internal + MCP external) chosen for V1.
- **Curated knowledge base vs vector RAG**: YAML approach for
  futuristic-tech theme, with role tagging to avoid the "Google
  shows up for every query" failure mode.
- **Separation of core data from enrichment data**: universe loads
  reliably from Wikipedia; market caps degrade gracefully from
  Yahoo. A general production pattern.
- **Disposable data vs durable code**: code is the source of truth,
  the database is regeneratable cache, `.gitignore` excludes the
  DB file.

### Python and Modern Backend Development

- **FastAPI**: modern async Python web framework. Routes, decorators,
  lifespan, middleware, sub-routers. Why it replaced Flask for AI.
- **Pydantic**: runtime validation + static type hints together.
  BaseModel, Settings, response models, query parameter validation.
- **Async Python**: `async def` and why it matters for LLM workloads.
- **FastAPI vs Flask**: same family, different generations.
- **uvicorn and ASGI**: the runtime that serves FastAPI; framework
  vs server distinction.
- **Project layout**: `app/api/`, `app/agent/`, `app/tools/`, etc.
  Feature-vertical organization.
- **Python virtual environments**: why venv, what it isolates, why
  `.venv/bin/python` explicitly bypasses PATH issues.
- **Configuration via environment variables**: .env, .env.example,
  pydantic-settings, never committing secrets.
- **Context managers**: `with db_connection() as conn:` for guaranteed
  cleanup; `@contextmanager` decorator pattern.

### Data Engineering Concepts

- **Embedded vs server-based databases**: DuckDB (library) vs Postgres
  (server). No process running, just a file and a library.
- **DuckDB**: columnar storage, Parquet integration, pandas-first,
  the sweet spot for analytical workloads.
- **Schema design**: primary keys, indexes for anticipated query
  patterns, idempotent `CREATE TABLE IF NOT EXISTS`.
- **Upserts**: `INSERT OR REPLACE` for idempotent ingestion.
- **Web scraping patterns**: User-Agent headers, fetching HTML with
  httpx then parsing with pandas.
- **Rate limiting in upstream sources**: Yahoo 429s, delays, retries,
  graceful failure, deferral-to-better-source pattern.
- **Source data hierarchy**: distinguish reliable (Wikipedia
  constituent list) from unreliable (yfinance market caps).
- **DBeaver and database introspection**: connecting to a DuckDB file
  in read-only mode, SQL editor as a development tool.

### Software Engineering Practices

- **Architecture Decision Records (ADRs)**: Status / Context /
  Decision / Consequences format. Captures *why*, not just *what*.
  Wrote 3 today: monorepo, DuckDB, defer-market-caps.
- **Git fundamentals**: initial commit, `.gitignore` discipline,
  `git rm --cached` for files committed by mistake, commit message
  hygiene.
- **Why binary files don't go in git**: `.duckdb`, build artifacts,
  `.env`. Principle: regeneratable artifacts are not source.
- **Monorepo vs polyrepo**: ADR-0001 captures the reasoning.
- **Idempotency**: operations safe to run repeatedly. Schema
  creation, upserts, ingestion runs.
- **Graceful degradation**: when Yahoo rate-limits, system loads
  what it can and reports what failed.

### The Project's Architectural Choices (Concrete)

- **Why monorepo** (ADR-0001): single source of truth, simpler PRs.
- **Why DuckDB** (ADR-0002): columnar for analytics, no server,
  single file, Pandas-first.
- **Why defer market caps** (ADR-0003): Yahoo rate-limiting; FMP
  free tier will handle it in Week 3.
- **Why FastAPI over Flask**: async-first, Pydantic-integrated,
  auto-generated OpenAPI docs, modern AI-engineering standard.
- **Why pip + venv over uv**: pragmatic familiarity vs modern tooling.
- **Why YAML knowledge base over vector RAG** for the
  futuristic-tech theme: editorial control, explainable, simpler V1.
- **Why direct function calls + MCP externally** (Option B): avoids
  over-engineering the agent loop while still showcasing MCP.

### Operational Reality

- **mise / Python version managers** can shadow your venv. The fix:
  explicit `.venv/bin/python` invocations.
- **GitHub auth changed**: password auth is dead, need PAT or SSH.
- **Bash here-docs** (`cat > file <<'EOF' ... EOF`) for writing files
  from the terminal. Single-quoted `'EOF'` prevents shell expansion.
- **Wikipedia requires User-Agent**: production scrapers identify
  themselves. Anonymous = blocked.
- **Yahoo Finance has deprecated** unauthenticated API access;
  yfinance hits rate limits fast in 2026.
- **Datetime deprecations**: `datetime.utcnow()` deprecated;
  use `datetime.now(timezone.utc)`.

### AI / LLM Foundational Vocabulary (introduced, not yet built)

- **Agentic AI**: LLM loops that decompose problems, choose tools,
  reason over results.
- **Tool use / function calling**: how LLMs invoke typed external
  functions and synthesize results.
- **RAG (Retrieval-Augmented Generation)**: pulling external context
  into LLM prompts; what makes RAG good vs bad.
- **MCP (Model Context Protocol)**: Anthropic's open standard for
  connecting LLMs to external tools; "USB for AI" analogy.
- **Evals and LLM-as-judge**: measuring agent quality systematically.
- **Vector databases and embeddings**: at the concept level only.

### Stock Market and Finance Concepts

- **Market cap as a ranking metric**: why "top 100, 500-700"
  questions need it.
- **GICS sectors**: 11-category taxonomy used by S&P; now visible
  in the database.
- **Insider transactions and Form 4**: SEC filings disclosing
  executive trading.
- **13F filings**: quarterly hedge fund position disclosures
  (45-day lag).
- **Fundamental vs technical analysis**: different lenses; agent
  will support both.
- **Pre-revenue speculative stocks**: narrative-driven pricing,
  dilution risk.
- **Concentration risk**: 90% in a single theme creates correlated
  risk regardless of ticker count.

### Professional Practices

- **Honest scope tradeoffs**: what V1 will/won't do, explicit not
  overpromised.
- **Distinguishing claims from facts**: separating analysis from
  prediction.
- **Career-focused engineering decisions**: every architectural
  choice connects to interview signal.
- **Building log discipline**: ADRs, future blog post, commit
  messages as audit trail.

---

## Day 1 Concrete Outputs

**Code shipped:**
- Monorepo structure with backend/, frontend/, knowledge_base/,
  docs/, data/, evals/
- Typed FastAPI backend with Pydantic
- DuckDB schema with universe table and indexes
- Wikipedia scraping pipeline with proper User-Agent
- Typed REST API: /, /health, /universe, /universe/sectors
- 503 S&P 500 constituents loaded and queryable

**Documentation shipped:**
- ADR-0001: Monorepo structure
- ADR-0002: DuckDB for analytical storage
- ADR-0003: Defer market caps to a reliable source

**Real production problems solved:**
- Wikipedia 403 (User-Agent fix)
- Yahoo 429 rate limiting (separated core from enrichment)
- mise PATH shadowing venv (explicit .venv/bin/python)
- GitHub HTTPS auth deprecation (PAT/SSH path)
---

## Day 2 — React Frontend: Full-Stack Data Flow

### Frontend Stack and Tooling

- **Vite**: modern build tool replacing Create React App. 50ms hot reload,
  ESM-native, esbuild + Rollup under the hood. Industry default for React.
- **React + TypeScript template**: `--template react-ts` pre-configures
  types, React 18, ESLint. Saves 30 min of setup.
- **Node version managers**: mise / nvm / Homebrew can all manage Node;
  Vite 8+ requires Node 20.
- **npm package pinning**: `tailwindcss@3.4.13`, `@tanstack/react-query@5.59.0`
  for deterministic installs.

### TypeScript Practices

- **Interface vs type**: `interface` for object shapes, `type` for unions
  and aliases. Convention, not enforcement.
- **Mirroring backend Pydantic models**: TypeScript interfaces in
  `src/types/` mirror Pydantic models 1:1. Single source of truth.
- **Snake_case preserved across boundary**: avoid double-conversion of
  field names; let the wire format flow through.
- **`string | null` matches Optional[str]**: explicit nullability.
- **`number` for both ints and floats**: JS doesn't distinguish.

### Tailwind CSS

- **Utility-first**: compose styles via class names rather than writing CSS.
- **Build-time purging**: only classes used in your code ship to production.
- **Responsive prefixes**: `md:`, `lg:`, `xl:` for breakpoints.
- **State prefixes**: `hover:`, `focus:`, `disabled:` modify behavior.
- **Key idioms**: `max-w-6xl mx-auto px-4` (centered container),
  `flex items-center justify-between` (header layout),
  `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` (responsive grid).

### React Patterns

- **Functional components**: arrow functions returning JSX. Class
  components are legacy.
- **Hooks discipline**: every custom hook starts with `use`. React enforces
  this rule via lint.
- **`useState<T>(initial)`**: typed state. Type parameter is optional
  but explicit when state can be null/union.
- **Lifting state up**: parent owns state, children request changes via
  callbacks (`onSectorClick`). Standard React pattern.
- **Conditional rendering**: `{condition && (...)}` short-circuits.
- **Optional chaining for callbacks**: `onSectorClick?.(value)` avoids
  null check boilerplate.
- **Component composition**: small focused components beat large mixed ones.
  `SectorList`, `TickerList`, `App` each do one thing.

### TanStack Query (Server State Management)

- **`useQuery({queryKey, queryFn})`**: declarative data fetching.
- **`queryKey` as cache identifier**: arrays let you parameterize
  (e.g., `["universe", sector, limit]`).
- **Automatic cache deduplication**: multiple components calling the same
  hook share one network request.
- **`enabled: condition`**: conditional fetching. Hook does nothing when
  enabled is false.
- **`staleTime`**: how long data stays fresh in cache without refetching.
- **Built-in loading/error/empty states**: `isLoading`, `isError`, `error`,
  `data`. Every component handles all four.
- **`QueryClientProvider`**: wraps app, makes client available via context.

### API Client Architecture

- **Single source of truth**: all backend calls go through `src/api/client.ts`.
  No scattered `fetch()` calls.
- **Axios over fetch**: better defaults (auto JSON, interceptors, error
  handling). Minor preference; teams differ.
- **`axios.create()` instance**: shared config (baseURL, timeout, headers)
  defined once.
- **Generic types**: `axios.get<ResponseType>()` propagates types through.
- **Environment variables**: `import.meta.env.VITE_API_BASE_URL` for
  configurable backend URL. Variables must be `VITE_` prefixed.
- **Functions, not classes**: lightweight, easy to mock.

### Component Patterns

- **Loading / error / empty / success**: every data-fetching component
  handles all four states. Skip one, ship a silent bug.
- **`error instanceof Error`**: defensive type narrowing for `unknown`.
- **Props types inline**: small components don't need separate type files.
- **Accessible defaults**: `<button>` over `<div>` for clickable elements.
- **Pluralization**: `${count} ticker${count === 1 ? "" : "s"}`.
- **Em-dash for null values**: `value ?? "—"` is cleaner than empty cells.

### CORS and Cross-Origin Communication

- **Frontend (5173) and backend (8000) are separate origins**.
- **CORS middleware on FastAPI** explicitly allows the frontend origin.
- **Without CORS config**: browser blocks requests with no helpful error.
- The `allow_origins` list we set Day 1 was finally exercised today.

### Day 2 Concrete Outputs

**Code shipped:**
- React + Vite + TypeScript + Tailwind frontend scaffolded
- TanStack Query integrated for server state
- Typed API client with axios
- SectorList and TickerList components
- useSectors and useUniverse custom hooks
- Full-stack data flow: DuckDB -> FastAPI -> React UI

**Real production problems solved:**
- Node version mismatch (18 vs Vite 8 requirement) — upgraded via mise
- Vite scaffold prompt loop — cancelled second invocation
- CORS configuration validated by real browser request

---

## Day 3 — Agentic AI: First Agent Loop with Gemini

### LLM Provider Choice

- **API access ≠ subscription**: Claude Pro/Max plans are *chat* products;
  API access is billed separately through console.anthropic.com.
- **Free LLM options in 2026**: Google Gemini AI Studio is the most
  generous (1,500 req/day, no credit card, frontier-class Gemini 2.5 Flash).
  Groq is fastest, OpenRouter has variety, Cerebras has highest daily volume.
- **Model choice doesn't affect architecture**: same agent loop shape
  whether using Gemini, Claude, or GPT — only the client SDK differs.

### Agent Concept

- **An agent is a while loop around an LLM with tool use**: the LLM either
  returns a final answer or requests a tool call; on tool call, code
  executes the tool and feeds the result back; loop continues.
- **The LLM never executes tools**: it requests them. Your code runs them.
  Critical separation — LLM is outside the trust boundary.
- **Bounded iteration**: production agents cap at 5-10 turns. Unbounded
  loops can spin forever on confusing inputs and burn money.
- **Division of labor**: LLM provides natural-language understanding +
  synthesis; tools provide deterministic data. Don't make the LLM do
  math or rankings — give it tools that do them.

### Tool Design

- **Narrow scope**: one tool, one thing. `get_sector_summary` not `do_stuff`.
- **Typed parameters + return**: Pydantic models for return shapes.
- **Self-describing**: docstring is the contract with the LLM, not just
  for humans. Include purpose, when-to-use examples, constraints, args.
- **Constrain inputs in docstrings**: listing valid sector names prevents
  the LLM from hallucinating "Tech" instead of "Information Technology".
- **Read-only by default**: tools that mutate need more careful design.
- **Compose with small tools**: `list_sectors` + `get_sector_summary` better
  than one mega-tool. Agent chains them as needed.

### Agent Loop Architecture

- **Tool registry pattern**: name → function dict. Single source of truth.
  Agent loop doesn't import individual tools; it dispatches by name.
- **System prompt** sets persona and behavior; sent every turn.
- **Conversation history** (`contents`) grows each iteration: user question
  → assistant tool call → user tool response → assistant tool call → ...
  → assistant final answer.
- **Pydantic serialization** for tool results: LLM expects JSON, so
  `model.model_dump()` before sending back.
- **Error handling on tool execution**: pass errors back to the LLM as
  results; agent can recover by trying a different approach.

### Agent Observability

- **Trace dict** captures: tool calls (name, args, result/error), iteration
  count, final answer. Returned alongside the answer.
- **Why this matters**: debugging agent failures, eval rubrics, user trust
  (showing what the agent did), and senior-engineer signal in interviews.
- **Built from Day 1 of the agent**, not added later. Retrofitting
  observability is much harder than building it in.

### FastAPI Patterns for Agents

- **POST not GET**: agent calls have side effects (LLM tokens, traces).
- **Pydantic request validation**: `Field(min_length=1, max_length=500)`
  for guardrails on inputs.
- **HTTPException on agent failure**: graceful 500 response, not crash.
- **No streaming yet** — Day 3 keeps it simple with request/response.
  Streaming via SSE comes later.

### React Patterns for Agent UIs

- **`useMutation` not `useQuery`** for agent calls: actions with side
  effects, not cacheable reads.
- **`isPending` for loading state**: disable input, swap button label.
- **Textarea + Enter-to-submit + Shift+Enter for newline**: chat UI
  convention. Production-quality detail.
- **Collapsible trace display**: most users want the answer; power users
  and demos want the reasoning.

### Production-Pattern Security

- **API keys never leave `.env`**: never in chat, screenshots, error
  messages, commits, terminal pastes. Rotated immediately if exposed.
- **`.env` always gitignored, never committed**. Verify with
  `git log --all --full-history -- .env`.
- **Spending caps on API keys**: set monthly limit in provider console
  before first use as a safety net.

### Day 3 Concrete Outputs

**Code shipped:**
- Tool registry and first two tools (`get_sector_summary`, `list_sectors`)
- Agent loop with Gemini tool use, capped iterations, full trace
- POST /agent/ask endpoint with typed request/response
- Frontend ChatPanel with chat input, answer display, collapsible trace
- useAskAgent mutation hook
- Agent API client function

**End-to-end agentic AI working in browser**:
question → React → FastAPI → Gemini → tool dispatch → DuckDB → answer.

---

## Day 4 — Expanding Agent Capabilities

### Tool Design Patterns

- **Composing small tools over big ones**: kept tools narrow (one verb each).
  Search, lookup, compare. Agent chains them naturally when needed.
- **Graceful not-found handling**: get_ticker_details returns found=False
  rather than raising. Tools should tell the LLM what went wrong, not crash.
- **Multi-input tool with self-recovery hint**: compare_sectors returns
  both `comparisons` (success) AND `not_found` (failures). LLM can
  see "you used 'Tech' but it's not valid" and self-correct.
- **Input validation in tools**: `max(1, min(limit, 100))` clamps weird LLM
  inputs. Tools should be defensive against the LLM passing garbage.

### Gemini Tool Selection Behavior

- 5 tools in scope, agent chose correctly on all 4 test questions
- System prompt strategy hints meaningfully shaped behavior — without the
  hint, Gemini would likely have called get_sector_summary twice for
  comparisons instead of compare_sectors once
- 2 iterations per query (1 tool call + 1 synthesis) was consistent
- Search by "tech" found 15 companies across IT, Health Care, Industrials —
  agent grouped results clearly by sector in the synthesized answer

### Function Declaration Schema for Gemini

- Each tool needs name, description (docstring), and JSON Schema for params
- `required` array specifies which params are mandatory
- `type: "array"` with `items: {type: "string"}` for list parameters
- Empty `properties: {}` is valid for parameterless tools

### Reliability and Debugging

- **LLM APIs are not deterministic**: same query can succeed or fail
  transiently (rate limits, model load, network blips, edge cases)
- **Encountered first 500 on day 4**: "Find companies with tech in name"
  failed once, succeeded immediately after. Likely transient API issue.
- **Improved error logging**: route now logs full traceback on agent
  failures. Without this, debugging is nearly impossible — the original
  error path swallowed exceptions in HTTPException wrapping.
- **Lesson for production**: agents need retries, fallbacks, observability
  by default. Reliability work is real engineering, not optional polish.

### Concrete Outputs

- 3 new tools with Pydantic return models
- Tool registry expanded to 5 tools
- Gemini function declarations expanded
- System prompt with strategy hints
- Better error logging in API route
- End-to-end verified across 4 query types
