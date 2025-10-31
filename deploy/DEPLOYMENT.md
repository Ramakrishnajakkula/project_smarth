# Deployment (Free-tier)

This guide shows how to deploy:

- API (FastAPI) to Deta Space (free)
- UI (Streamlit) to Streamlit Community Cloud (free)

Prerequisites

- A MongoDB Atlas M0 cluster and a database user
- The API reachable locally (uvicorn) and the UI working locally (streamlit)
- This repository on GitHub (recommended) or ZIP upload

---

## 1) Deploy API to Deta Space

Deta Space runs your app as a microservice and exposes a public URL.

1. Sign in at https://deta.space/ and create a new project.
2. Add a new Micro from your GitHub repo (or upload manually). Use this repo root.
3. Set the run command for the Micro:
   - `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables in the Micro settings:
   - `MONGODB_URI` = your Atlas URI (required)
   - `MONGODB_DB` = `samarth` (or your DB name)
   - `HF_API_TOKEN` (optional)
   - `DATA_GOV_IN_API_KEY` (optional)
   - `CACHE_ENABLED` = `true` (optional)
   - `CACHE_TTL_SECONDS` = `600` (optional)
   - `LOG_QUERIES` = `true` (optional)
5. Health check (optional but recommended): path `/`.
6. Deploy the Micro. Once live, note the public API URL (e.g., `https://<your-micro>.deta.dev`).
7. Sanity check:
   - `GET /` returns health
   - `GET /db/ping` returns `{ ok: true }`
   - `POST /query` returns a valid response

Tips

- CORS is open in the API for local dev and ease of integration. Restrict origins later if needed.
- If you change the code, re-deploy from Deta Space; consider connecting to GitHub for auto-deploys.

---

### 1A) Alternative: Deploy API to Render (Free Web Service)

Render provides a free web service that can run a Python web server. You can deploy manually or via the included `deploy/render.yaml`.

Option A — One-click via render.yaml

1. Push this repo to GitHub.
2. In Render, create a new "Blueprint" from your repo; it will detect `deploy/render.yaml`.
3. Set required environment variables in the Render Dashboard under the service:
   - `MONGODB_URI` (required)
   - `MONGODB_DB` (default `samarth`)
   - Optional: `HF_API_TOKEN`, `DATA_GOV_IN_API_KEY`, `CACHE_ENABLED`, `CACHE_TTL_SECONDS`, `LOG_QUERIES`
4. Deploy. Render will run:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
5. When live, note the public URL and test `/`, `/db/ping`, and `/query`.

Option B — Manual Web Service

1. Create a "Web Service" from your GitHub repo.
2. Runtime: Python; Build command: `pip install -r requirements.txt`.
3. Start command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`.
4. Set env vars as above; deploy and test.

Notes

- Include your processed CSVs in the repository (under `data/processed/...`) or add a startup step to generate them. Free tiers typically don’t offer persistent disks.
- If the UI is on Streamlit Cloud, set its `API_BASE_URL` secret to the Render URL.

---

### 1B) Alternative: Deploy API to Koyeb (Free)

Koyeb can run your API from a Dockerfile on a free plan.

1. Ensure the repository includes the provided `Dockerfile` at the root.
2. Push the repo to GitHub (or connect your GitHub account in Koyeb).
3. In Koyeb, create a new Service → "Deploy from GitHub" and select this repo.
4. Build strategy: Dockerfile; Build & run should auto-detect the Dockerfile.
5. Set environment variables:
   - `MONGODB_URI` (required)
   - `MONGODB_DB` (e.g., `samarth`)
   - Optional: `HF_API_TOKEN`, `DATA_GOV_IN_API_KEY`, `CACHE_ENABLED`, `CACHE_TTL_SECONDS`, `LOG_QUERIES`
6. Deploy. Koyeb will build the container and run `uvicorn` using the Dockerfile `CMD`.
7. When live, test your public URL for `/`, `/db/ping`, and `/query`.

Notes

- The image bundles `data/processed/...` from the repo so the CSV endpoints work on first boot.
- If you regenerate processed files at build time, ensure the Dockerfile copies them into the image.
- If you later restrict CORS, add your Streamlit domain to allowed origins.

---

### 1C) Alternative: Deploy API to Hugging Face Spaces (Docker, Free)

Hugging Face Spaces can run a Dockerized API for free (no card required).

1. Ensure the repo contains the provided `Dockerfile` at the root (already added).
2. Create a new Space at https://huggingface.co/spaces → Select "Docker" for the SDK.
3. Connect this GitHub repo or upload the files.
4. In the Space Settings → Secrets, add:
   - `MONGODB_URI` (required)
   - `MONGODB_DB` (e.g., `samarth`)
   - Optional: `HF_API_TOKEN`, `DATA_GOV_IN_API_KEY`, `CACHE_ENABLED`, `CACHE_TTL_SECONDS`, `LOG_QUERIES`
5. Deploy the Space. The Dockerfile starts `uvicorn` binding to `${PORT}` exposed by Spaces.
6. Test the Space URL (`/`, `/db/ping`, `/query`).

Notes

- The Docker image includes `data/processed/...` from the repository for the CSV endpoints.
- If you regenerate processed files during build, ensure the Dockerfile copies them.
- Spaces may sleep; first request can be slower (cold start).

---

### 1D) Note on Vercel (Hobby)

Vercel’s Hobby tier is free, but may prompt for payment verification depending on region/features. Running FastAPI on Vercel typically uses Python Serverless Functions and may require restructuring the project into `api/*.py` handlers or using a custom adapter. If you prefer Vercel, we can add a minimal serverless handler (and `vercel.json`) in a follow-up, but for a no-card path, prefer Deta Space or Hugging Face Spaces.

---

## 2) Deploy Streamlit UI to Streamlit Community Cloud

1. Push this repo to GitHub if you haven't already.
2. Go to https://share.streamlit.io/ and create a new app.
3. Choose your repo, branch (e.g., `main`), and app path:
   - `ui/streamlit_app.py`
4. In the app settings -> Secrets, add:
   ```toml
   API_BASE_URL = "https://<your-micro>.deta.dev"
   ```
5. Deploy the app. Open the URL Streamlit gives you.
6. Test by asking a question. The UI calls your Deta Space API.

Notes

- Requirements are in the root `requirements.txt` and include `streamlit`, `fastapi`, `uvicorn`, etc.
- You can also set `API_BASE_URL` as an environment variable locally.

---

## 3) Alternative hosting (optional)

If Deta Space isn't available, consider Render (free web service), Railway (free trial), or other free-tier PaaS:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
- Expose port `$PORT`
- Environment variables: same as above (`MONGODB_URI`, etc.)

---

## 4) Post-deploy checks

- `/` returns healthy status with timestamp.
- `/db/ping` returns ok:true (if MongoDB env vars are set correctly).
- `/datasets` lists processed CSVs (ensure you've run processors and included files).
- `/query` returns parsed info, rows, answer, and citations.
- Streamlit UI renders answer, citations, datasets, parsed metadata, and rows.

---

## Troubleshooting

- 404 on endpoints: confirm run command and app path (`src.api.main:app`).
- MongoDB errors: verify `MONGODB_URI` and IP access list in Atlas, and `MONGODB_DB` name.
- CORS errors in UI: API has permissive CORS by default; if you changed it, include your Streamlit domain.
- Slow first request: cold starts are normal in free tiers; subsequent requests are faster.
