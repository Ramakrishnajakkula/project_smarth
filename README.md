---
title: Project Samarth API
emoji: 🌦️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Project Samarth — Minimal API Scaffold

This repo contains a minimal FastAPI scaffold with MongoDB wiring aligned to Python 3.8, MongoDB (Atlas M0), and free-tier services (Hugging Face for LLMs).

## What’s included

- FastAPI app with:
  - `/` health endpoint
  - `/db/ping` to verify MongoDB connectivity
  - `/query` placeholder (returns 501 until parser/router/LLM are added)
- MongoDB client helper (`src/db/mongo.py`)
- Config loader (`src/utils/config.py`) using `.env`
- Minimal `.env.example`
- Minimal `requirements.txt`
- Optional Mongo-backed cache for API responses (off by default)

## Quick start (Windows PowerShell)

```powershell
# 1) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt

# 3) Create .env from example and fill values
Copy-Item .env.example .env
# Edit .env and set at least:
#   MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/<db>
#   MONGODB_DB=samarth
# Optional for LLM answers (free):
#   HF_API_TOKEN=<your-huggingface-token>

# For local Mongo (optional), you can use Docker Desktop:
# docker run -d --name samarth-mongo -p 27017:27017 mongo:6
# Then set MONGODB_URI=mongodb://localhost:27017

# 4) Run the API
uvicorn src.api.main:app --reload

# 5) Test in browser
# http://127.0.0.1:8000/         -> health
# http://127.0.0.1:8000/db/ping  -> mongo ping
```

## API endpoints

After you generate processed CSVs (see Data processing below), the API serves them directly:

- Climate

  - GET `/climate/state-annual`
    - Query params: `state` (exact), `year` (int), `limit` (1-1000), `offset`
    - Returns: `[ { State, Year, Annual_Rainfall_mm } ]`
    - Example: http://127.0.0.1:8000/climate/state-annual?year=2009&limit=5
  - GET `/climate/subdivision-annual`
    - Query params: `subdivision` (exact), `year` (int), `limit`, `offset`
    - Returns: `[ { Subdivision, Year, Annual_Rainfall_mm } ]`
    - Example: http://127.0.0.1:8000/climate/subdivision-annual?limit=5

- Agriculture
  - GET `/agriculture/crop-apy-state-year`
    - Query params: `state` (exact), `crop` (exact), `year` (label like 2000-01), `limit`, `offset`
    - Returns: `[ { State, Year, Crop, Area_ha, Production_tonnes, Yield_t_per_ha } ]`
    - Example: http://127.0.0.1:8000/agriculture/crop-apy-state-year?crop=Rice&year=2000-01&limit=5

If a processed file is missing, endpoints return 404 with the filename.

### Discovery and stats

- GET `/datasets` — Lists available processed CSVs with id, kind, path, bytes, modified, and row counts.
- GET `/stats` — Returns basic counts like climate state_annual_rows and agriculture crop_apy_rows.

### Optional Mongo-backed cache

You can enable a tiny MongoDB-backed cache for API responses to speed up repeated queries:

```powershell
# In .env
CACHE_ENABLED=true
CACHE_TTL_SECONDS=600
CACHE_COLLECTION=cache
```

Notes:

- Cache is off by default. If MongoDB is unreachable or any cache error occurs, the API continues without caching.
- Keys are built from the endpoint path and normalized query params.

### Optional background logging of queries

Enable logging of `/query` requests to MongoDB:

```powershell
# In .env
LOG_QUERIES=true
LOG_QUERIES_COLLECTION=queries
LOG_QUERIES_ROWS_SAMPLE=20
```

Notes:

- Logging is off by default. If MongoDB isn’t reachable, the API ignores logging errors and still serves responses.

## Alternate dataset download (no per-dataset API keys)

If you have direct CSV/Parquet links (from any free source), add them to `data/datasets.manifest.yaml` under each dataset's `url` field. If a dataset page doesn’t provide a direct file URL, use `csv_alternative` or `alternative_url`. The downloader will try `url` → `csv_alternative` → `alternative_url` in that order and will skip HTML pages that aren’t direct files.

```powershell
# Edit the manifest and paste URLs for the datasets you have
notepad .\data\datasets.manifest.yaml

# Run the downloader (requires requests + pyyaml from requirements.txt)
python .\src\data_ingestion\manual_downloader.py

# Files will be saved under data/raw/<dataset_key>.<ext>
```

Suggested dataset keys to collect:

- agriculture_crop_production_state_year (State, Year, Crop, Production_tonnes)
- agriculture_crop_yield_state_year (State, Year, Crop, Yield_t_per_ha)
- agriculture_area_state_year (State, Year, Crop, Area_ha)
- climate_rainfall_state_year (State, Year, Rainfall_mm)
- climate_temperature_state_year (State, Year, Temp_C)

These are enough to enable comparison, trend, and correlation queries between rainfall and crop outputs.

## Data processing

Run these scripts to build the processed CSVs consumed by the API:

```powershell
# Climate
python .\src\data_ingestion\process_climate.py

# Agriculture
python .\src\data_ingestion\process_agriculture.py
```

Outputs:

- Climate
  - `data/processed/climate/rainfall_state_year.csv`
  - `data/processed/climate/rainfall_subdivision_long.csv`
  - `data/processed/climate/rainfall_subdivision_year.csv`
- Agriculture
  - `data/processed/agriculture/crop_apy_state_year.csv`

## Query answering (free-first)

POST `/query` accepts a JSON body `{ "q": "your question" }` and returns:

- If `HF_API_TOKEN` is set, uses Hugging Face Inference API (free-tier) to draft a short answer.
- Otherwise, returns a deterministic local fallback summary.

Get an HF token (free) here: https://huggingface.co/settings/tokens

Example:

```powershell
curl -s -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{ "q": "Show trend of rainfall in Kerala from 2009 to 2010" }'
```

### Prompt tips (UI and `/query`)

You can ask natural questions in these patterns:

- Trend: "trend", "over time", year ranges (e.g., 2010–2015) or relative periods ("last 5 years", "since 2005").
- Comparison: "compare A vs B", "across states/crops".
- Ranking: "top 5", "highest/lowest", "which state/crop …".
- Aggregations: "average/mean", "total/sum", "min", "max".
- Metrics & domain: rainfall (climate); yield, production, area (agriculture).
- Filters: specify states (Kerala, Punjab) and crops (Rice, Wheat) explicitly.
- Grouping hints: "across states/by state", "across crops/by crop".

Examples:

- "Average rainfall in Kerala over the last 5 years"
- "Top 5 states with highest rainfall in 2010"
- "Top 3 rice-producing states in 2015"
- "Compare rice yield across states in 2009"

## Next steps

- API: Deta Space (FastAPI)
- UI: Streamlit Community Cloud

## Notes

## Streamlit UI (Phase 5)

A simple Streamlit app is included to query the API from a friendly UI.

- Location: `ui/streamlit_app.py`
- Configuration: set API base via `API_BASE_URL` env var or Streamlit `secrets.toml` (`API_BASE_URL`), or edit it in the sidebar at runtime. Defaults to `http://127.0.0.1:8000`.
- Features:
  - Ask a natural language question (calls `/query`)
  - Shows answer, citations, datasets, parsed metadata, and row preview
  - Sample questions and per-session history
  - Basic error handling with retry in the UI

Run locally (ensure the FastAPI server is running):

1. Install requirements in your virtualenv (adds Streamlit)
2. Start the API server
3. Launch the UI with `streamlit run ui/streamlit_app.py`

Note: CORS is open for local dev. For remote deploys, set allowed origins as needed.

## Deployment (Free-tier)

See `deploy/DEPLOYMENT.md` for step-by-step instructions to deploy:

- API (FastAPI) to Deta Space
- UI (Streamlit) to Streamlit Community Cloud

Alternatives included: Render (free) and Koyeb (free, Dockerfile-based). You’ll set environment variables in the hosting dashboards. Ensure `MONGODB_URI` and `MONGODB_DB` are configured on the API host, and `API_BASE_URL` is set as a secret for the Streamlit app.

## MongoDB Atlas M0 (Phase 6)

You can use a free MongoDB Atlas M0 cluster or a local MongoDB.

1. Create an Atlas M0 cluster and a database user (read/write). Allow your IP.
2. Copy `.env.example` to `.env` and set:

- `MONGODB_URI` (your Atlas connection string)
- `MONGODB_DB` (e.g., `samarth`)

3. Optional: run the setup script to create collections and indexes:

- Ensures `queries` and `cache` collections exist
- Adds indexes for `queries.created_at`, `queries.answer_source`, text index on `q`
- Adds indexes for `cache.created_at` and optional TTL if `CACHE_TTL_SECONDS` is set

```powershell
# in your venv
python .\src\db\setup_atlas.py
```

If it prints "MongoDB setup complete", you’re good to go. The API’s `/db/ping` should return ok:true when the env is set.

- Keep costs zero: avoid paid API keys; OpenAI is optional and off by default.
- Python 3.8 compatible versions are pinned in `requirements.txt`.
  #   p r o j e c t _ s m a r t h 
   
   
#   q u i z _ b a c k e n d  
 