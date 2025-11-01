# Project Samarth — 2‑Minute Prototype Walkthrough (Video Script)

## 0:00–0:10 — Hook

- On screen: Title card “Project Samarth: Ask questions about climate and agriculture data”.
- Voiceover: “What if you could ask natural questions about India’s climate and agriculture data and get instant, trustworthy answers with citations? That’s exactly what Project Samarth does.”

## 0:10–0:30 — Problem → Solution

- On screen: Quick cut of CSVs, code, then the Streamlit UI.
- Voiceover: “Data is scattered in CSVs and hard to explore. Samarth unifies it with a FastAPI backend and a simple Streamlit UI. You type a question, and it returns a brief answer, a table of results, and the datasets it used.”

## 0:30–1:30 — Live Demo (4 quick queries)

1. Trend + Relative Years (Climate)

   - On screen: In the UI, type: “Average rainfall in Kerala over the last 5 years” → Click Ask.
   - Voiceover: “Here I ask for the average rainfall in Kerala over the last five years. You’ll see a concise answer and citations, plus the rows used. The parser understands ‘last 5 years’ and computes the range.”

2. Ranking / Top‑K (Climate)

   - On screen: Type: “Top 5 states with highest rainfall in 2010”.
   - Voiceover: “For rankings, just say ‘Top 5’. We group by state, aggregate rainfall, and return the top results with the climate dataset listed.”

3. Comparison (Agriculture)

   - On screen: Type: “Compare rice yield across states in 2009”.
   - Voiceover: “For agriculture, ask about yield, production, or area. Here we compare rice yield across states for 2009—perfect for side‑by‑side analysis.”

4. Trend by Region/Crop (Agriculture)
   - On screen: Type: “Show wheat yield trend in Maharashtra since 2005”.
   - Voiceover: “The system understands ‘since 2005’, filters the APY dataset, and returns a year‑by‑year series.”

## 1:30–1:45 — How It Works (under the hood)

- On screen: Diagram: UI → API (/query) → NLP Parser → Data Router → CSVs → Answer.
- Voiceover: “Under the hood, a lightweight NLP parser extracts intent, metrics, entities, years—including phrases like ‘top 5’ and ‘since 2005’. The data router reads processed CSVs, filters, groups, and aggregates. A small answer module summarizes results; if a Hugging Face token is set, it uses a free model; otherwise a deterministic fallback ensures reliability. Citations are always appended.”

## 1:45–2:00 — Deployments + Close

- On screen: Logos of Hugging Face Spaces and Streamlit Cloud; show /health.
- Voiceover: “The API runs as a Docker app on Hugging Face Spaces with a health check and correct $PORT binding. The Streamlit UI can run locally or on Streamlit Cloud—just set API_BASE_URL. Next steps include fuzzy matching, year‑over‑year growth, and more datasets. Project Samarth turns raw CSVs into answers—fast, transparent, and ready to extend.”

---

## Recording Tips (optional for the presenter)

- Keep cuts tight—each query ~15–20 seconds.
- Use the built‑in samples in the sidebar to avoid typing errors.
- Ensure API_BASE_URL points to your running API (local or Space).
- If using Spaces, confirm health at `/health` first.

## On‑Screen Labels (optional)

- “Understands: trend, comparison, ranking (top‑k), aggregation (avg/sum/min/max), relative years (‘last N’, ‘since Y’)”.
- “Citations from: climate:rainfall_state_year, agriculture:crop_apy_state_year”.
- “Free‑tier friendly: Hugging Face Spaces + Streamlit Cloud”.
