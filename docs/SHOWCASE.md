# Project Samarth — Showcase

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](./requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Hugging Face Spaces](https://img.shields.io/badge/Hugging%20Face-Spaces-F9D37A?logo=huggingface&logoColor=000)](https://huggingface.co/spaces)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

A lightweight question‑answering system over Indian climate and agriculture datasets. Ask natural questions; get concise answers, rows, and citations.

- Live API: https://ramakrishna890-smarth-api.hf.space
- Live UI: https://projectsmarth-gavwqzxet6k77xyp2dzbfg.streamlit.app/

---

## 🎬 Demo Video

You can embed a demo video directly in this Markdown. Two easy options:

1) Upload MP4 to this repo at `docs/assets/video.mp4` (recommended for quick sharing)

```html
<!-- GitHub renders video reliably via the RAW URL (not the blob view). -->
<video controls preload="metadata" style="max-width:100%; border-radius:8px;">
  <source src="https://raw.githubusercontent.com/Ramakrishnajakkula/project_smarth/main/docs/assets/video.mp4" type="video/mp4" />
  Sorry, your browser doesn't support embedded videos.
</video>

If the embedded player doesn’t show up, open the RAW link directly:

- [View video (raw link)](https://raw.githubusercontent.com/Ramakrishnajakkula/project_smarth/main/docs/assets/video.mp4)
```

2) Or upload the MP4 via the GitHub web UI to get a CDN URL (user-images) and embed with HTML:

```html
<video src="https://user-images.githubusercontent.com/.../demo.mp4" controls style="max-width:100%; border-radius:8px;"></video>
```

## 🎬 Demo Video

Inline player (will render on GitHub if supported by your browser):

<video src="./assets/video.mp4" controls preload="metadata" style="max-width:100%; border-radius:8px;">
  Sorry, your browser doesn't support embedded videos.
</video>

If the inline player doesn’t appear, open or download it directly: [View video](./assets/video.mp4)

---

### How to embed (examples)

1) Local file (this repo)

```html
<video src="./assets/video.mp4" controls preload="metadata" style="max-width:100%; border-radius:8px;"></video>
```

2) GitHub CDN (user-images)

```html
<video src="https://user-images.githubusercontent.com/.../demo.mp4" controls style="max-width:100%; border-radius:8px;"></video>
```

> Tips:
> - Keep the video under ~25–50 MB for quick loads. For large files (>50–100 MB), consider Git LFS or the GitHub user-images CDN.
> - Some corporate networks block inline media; use the direct link above if the player doesn’t render.

---

## 🧭 What you can ask

- Trend: “trend”, “over time”, ranges (2010–2015) or relative (“last 5 years”, “since 2005”).
- Comparison: “compare A vs B”, “across states/crops”.
- Ranking: “top 5”, “highest/lowest”, “which state/crop …”.
- Aggregations: “average/mean”, “total/sum”, “min”, “max”.
- Metrics & domain: rainfall (climate); yield, production, area (agriculture).
- Filters: specify states (Kerala, Punjab) and crops (Rice, Wheat); hints like “by state/crop”.

Sample prompts:
- “Average rainfall in Kerala over the last 5 years”
- “Top 5 states with highest rainfall in 2010”
- “Compare rice yield across states in 2009”
- “Show wheat yield trend in Maharashtra since 2005”

---

## 🏗️ Architecture

```mermaid
graph LR
  subgraph Client
    UI[Streamlit App]
  end
  subgraph Compute
    API[(FastAPI on Hugging Face Spaces\nDocker container)]
    Parser[Query Parser (NLP)]
    Router[Data Router]
    LLM[(Hugging Face Inference API):::opt]
    Mongo[(MongoDB Atlas):::opt]
  end
  subgraph Data
    Climate[(CSV: data/processed/climate\n• rainfall_state_year.csv\n• rainfall_subdivision_year.csv)]
    Ag[(CSV: data/processed/agriculture\n• crop_apy_state_year.csv)]
  end

  UI -->|POST /query| API
  API --> Parser
  API --> Router
  Router --> Climate
  Router --> Ag
  API --> LLM
  API --> Mongo

  classDef opt fill:#eef,stroke:#88f,color:#000;
```

Key design points:
- Stateless API reads pre‑processed CSVs for predictable performance and zero vendor lock‑in.
- NLP extracts intent, years (including “last N” / “since”), metrics, entities, grouping, and top‑k.
- Router filters/aggregates and returns rows + citations. LLM summarization is optional.
- Health‑checked container binds to `$PORT` (7860 on HF Spaces) for reliable startup.

---

## 🗃️ Datasets

| Kind       | File | Description |
|------------|------|-------------|
| Climate    | `data/processed/climate/rainfall_state_year.csv` | State‑level annual rainfall (mm) by year |
| Climate    | `data/processed/climate/rainfall_subdivision_year.csv` | Subdivision‑level annual rainfall (mm) by year |
| Agriculture| `data/processed/agriculture/crop_apy_state_year.csv` | State‑level crop APY: Area (ha), Production (tonnes), Yield (t/ha) by year |

Notes:
- Files are in this repo and served directly by the API endpoints.
- If a file is missing, the corresponding endpoint returns a 404 with the filename.

---

## 🔌 API quickstart

- Health: `GET /health`
- Climate:
  - `GET /climate/state-annual?state=Kerala&year=2010&limit=5`
  - `GET /climate/subdivision-annual?subdivision=Karnataka&limit=5`
- Agriculture:
  - `GET /agriculture/crop-apy-state-year?crop=Rice&year=2009-10&limit=5`
- Natural language:
  - `POST /query` with `{ "q": "Average rainfall in Kerala over the last 5 years" }`

> Full schema and interactive docs at `/docs` when running locally.

---

## 🖥️ Run locally

```powershell
# 1) Create & activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install deps
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3) Start API
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --loop asyncio --http h11
# http://127.0.0.1:8000/health

# 4) Start UI (new terminal, same venv)
$env:API_BASE_URL = "http://127.0.0.1:8000"
python -m streamlit run ui/streamlit_app.py
# http://localhost:8501
```

---

## ☁️ Deploy

- API: Hugging Face Spaces (Docker)
  - Binds to `$PORT` (7860 by default on Spaces). Health check at `/health`.
- UI: Streamlit Community Cloud
  - Set secret `API_BASE_URL = https://<username>-<space>.hf.space`

> Alternative: Vercel (Docker) or Koyeb (Docker) for the API.

---

## ⚙️ Environment (optional)

- `.env` (API)
  - `MONGODB_URI` (optional)
  - `MONGODB_DB` (optional)
  - `HF_API_TOKEN` (optional, enables LLM summarization)
  - `CACHE_ENABLED`, `CACHE_TTL_SECONDS`, `CACHE_COLLECTION` (optional)

---

## 📸 Assets & Screenshots

- Drop screenshots under `docs/assets/` and reference them like:

```md
![UI Screenshot](./assets/screenshot_ui.png)
```

- Replace https://projectsmarth-gavwqzxet6k77xyp2dzbfg.streamlit.app/ above once your UI is live.
- Replace the video link or upload `docs/assets/video.mp4` to embed your demo.

---

## 📝 License & Credits

- Built with FastAPI, Streamlit, and Hugging Face Spaces.
- Data processing scripts under `src/data_ingestion/*` create the processed CSVs used by the API.
- This repo is designed for zero‑cost tiers and portability.
