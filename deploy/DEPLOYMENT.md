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
