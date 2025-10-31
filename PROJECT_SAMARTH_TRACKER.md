# Project Samarth — Task & Progress Tracker

Status: WIP • Updated: 2025-10-29

This tracker breaks the plan in `PROJECT_SAMARTH_PLAN.md` into actionable tasks with checkboxes so you can track completion. Defaults adhere to: Python 3.8, MongoDB (Atlas M0), and free-tier-only services for APIs and deployment.

Constraints

- Python 3.8 only
- Database: MongoDB (Atlas M0 free) — no Postgres/SQLite
- Use free-tier services only (API keys, hosting, CI)

Legend

- [ ] Not started • [~] In progress • [x] Done
- Fill Owner and Due as you go: Owner(@me) Due(YYYY-MM-DD)

Links

- Plan: `PROJECT_SAMARTH_PLAN.md`

---

## Milestones

- [x] M1: Data ingestion & normalization complete (Owner: @me, Due: )
- [x] M2: Query parsing + intent + router working E2E (Owner: @me, Due: )
- [x] M3: LLM answering with citations (free LLM path) (Owner: @me, Due: )
- [x] M4: API (FastAPI) + Streamlit UI integrated (Owner: @me, Due: )
- [ ] M5: Deployed on free-tier (API on Deta Space; UI on Streamlit Cloud) (Owner: , Due: )
- [ ] M6: Tests, docs, and 2-min demo video (Owner: , Due: )

---

## Phase 0 — Project Setup

- [ ] Create repo scaffolding and virtualenv for Python 3.8 (Owner: , Due: )
- [ ] Add `requirements.txt` aligned to plan (no paid-only deps) (Owner: , Due: )
- [ ] Create `.env` from `.env.example` (no secrets in git) (Owner: , Due: )
- [ ] Configure logging directory `logs/` and rotate if needed (Owner: , Due: )
- [ ] Pre-commit hooks (black/ruff or flake8 optional) (Owner: , Due: )

---

## Phase 1 — Data Discovery & Integration

- [x] Identify agriculture datasets on data.gov.in + save links (Owner: @me, Due: )
- [x] Identify IMD climate datasets + save links (Owner: @me, Due: )
- [x] Implement `DataGovInFetcher` with API key support (free) (Owner: @me, Due: )
- [x] Implement CSV/Parquet download and local caching (Owner: @me, Due: ) — CSV + local caching done; Parquet deferred
- [x] Build `DataNormalizer` (state/crop normalization, units, metadata) (Owner: @me, Due: ) — processors added for agriculture and climate
- [ ] Define data schemas per dataset (columns, units) in docs (Owner: , Due: )
- [ ] Store processed outputs as Parquet in `data/processed` (Owner: , Due: )

Acceptance criteria

- Reproducible scripts fetch and normalize at least 2 agriculture + 1 climate dataset
- Outputs stored with metadata and consistent columns

---

## Phase 2 — Intelligent Q&A Core

- [x] Implement `QueryParser` (entities: states, crops, metrics, temporal) (Owner: @me, Due: )
- [x] Implement basic intent classifier (comparison, trend, correlation, ranking) (Owner: @me, Due: )
- [x] Implement `DataRouter` to filter processed data based on parsed query (Owner: @me, Due: )
- [x] Add citation tracking (dataset name + URL) (Owner: @me, Due: )

Acceptance criteria

- CLI test calls show parsed structure, intended datasets, and filtered frames

---

## Phase 3 — LLM Answering (Free-first)

- [x] Configure free LLM path: Hugging Face Inference API token (free-tier) OR local llama.cpp/transformers (Owner: @me, Due: ) — docs + .env.example updated
- [x] Implement `LLMHandler` compatible with HF Inference or local (Owner: @me, Due: ) — fallback implemented; HF path uses token
- [x] Prompt template with citation instructions (Owner: @me, Due: )
- [x] Extract citations from answer text (Owner: @me, Due: )
- [ ] Optional: keep OpenAI integration behind a feature flag (off by default) (Owner: , Due: )

Acceptance criteria

- Answers generated using only the free path, citing datasets reliably
  - Current: deterministic fallback answers when no HF token; HF answers when token is set

---

## Phase 4 — API (FastAPI)

- [x] Define Pydantic models for requests/responses (Owner: @me, Due: )
- [x] Implement `/query` that calls parser → router → LLM handler (Owner: @me, Due: )
- [x] Implement `/datasets` and `/stats` stubs (Owner: @me, Due: )
- [x] Background logging of queries to file or MongoDB (Owner: @me, Due: ) — optional, toggled via .env
- [x] CORS middleware for Streamlit UI (Owner: @me, Due: )

Acceptance criteria

- Local run returns answers with citations; health endpoint is healthy

---

## Phase 5 — Streamlit UI

- [x] Build “Ask Your Question” page and result display (Owner: @me, Due: )
- [x] Display citations and query metadata (Owner: @me, Due: )
- [x] Add sample question picker and history (Owner: @me, Due: )
- [ ] Style polish (CSS) and error states (Owner: , Due: )

Acceptance criteria

- UI calls local API and renders answer, citations, and metadata cleanly

---

## Phase 6 — Database: MongoDB (Atlas M0)

- [ ] Create free MongoDB Atlas M0 cluster (no card) (Owner: , Due: )
- [ ] Create database `samarth` and collections as needed (e.g., `queries`, `datasets`) (Owner: , Due: )
- [ ] Add `MONGODB_URI` and `MONGODB_DB` to `.env` (Owner: , Due: )
- [x] Implement minimal DB client (pymongo or motor) (Owner: @me, Due: ) — `src/db/mongo.py`
- [x] Persist query logs and optional cached results (Owner: @me, Due: ) — implemented behind .env flags

Acceptance criteria

- App connects to Atlas M0; basic read/write tested

---

## Phase 7 — Deployment (Free-tier)

- [ ] Deploy API to Deta Space (FastAPI) (Owner: , Due: )
- [ ] Set env vars in Deta Space: `MONGODB_URI`, `MONGODB_DB`, `HF_API_TOKEN`, `DATA_GOV_IN_API_KEY` (Owner: , Due: )
- [ ] Deploy UI to Streamlit Community Cloud (Owner: , Due: )
- [ ] Configure UI to call deployed API URL (Owner: , Due: )
- [ ] Alternative: Vercel serverless for Python endpoints (optional) (Owner: , Due: )

Acceptance criteria

- Public URLs (API + UI) work without paid services

---

## Phase 8 — CI/CD & Quality

- [ ] GitHub Actions: lint + tests on PRs (free) (Owner: , Due: )
- [ ] Add badges to README for tests/status (Owner: , Due: )
- [ ] Minimal load test or timing logs (Owner: , Due: )

---

## Phase 9 — Testing & Docs

- [ ] Unit tests: parser, router, API health (Owner: , Due: )
- [ ] Integration test: `/query` end-to-end (Owner: , Due: )
- [ ] README with setup/run/deploy instructions (Owner: , Due: )
- [ ] 2-minute Loom walkthrough script + recording (Owner: , Due: )

---

## Environment variables (reference)

```bash
# Free LLM (preferred)
HF_API_TOKEN=your-hf-token-or-empty
DATA_GOV_IN_API_KEY=your-data-gov-api-key

# MongoDB (Atlas M0 or local)
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>/<db>?retryWrites=true&w=majority
MONGODB_DB=samarth

# API/UI
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

Notes

- Prefer HF Inference API or local models to keep zero-cost; keep OpenAI optional.
- Deta Space and Streamlit Community Cloud cover fully-free deploy for API + UI.
- For local dev, Docker Compose includes a MongoDB service.
