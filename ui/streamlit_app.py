from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import requests
import streamlit as st


def get_api_base_url() -> str:
    """Resolve API base URL safely without requiring secrets.toml.

    Priority: session_state override > env var > Streamlit secrets > default localhost.
    Guard against missing secrets file and non-streamlit execution.
    """
    # 1) Session override if present
    try:
        if "api_base_url" in st.session_state and st.session_state.api_base_url:
            return st.session_state.api_base_url  # type: ignore[no-any-return]
    except Exception:
        # Session state may not function outside `streamlit run`.
        pass

    # 2) Environment variable
    url = os.getenv("API_BASE_URL")

    # 3) Streamlit secrets (optional, may raise if secrets.toml is missing)
    if not url:
        try:
            secrets = getattr(st, "secrets", None)
            if secrets:
                url = secrets.get("API_BASE_URL", None)  # type: ignore[call-arg]
        except Exception:
            url = None

    # 4) Default
    if not url:
        url = "http://127.0.0.1:8000"

    # Persist into session state if available
    try:
        st.session_state.api_base_url = url
    except Exception:
        pass
    return url


def call_query_api(base_url: str, q: str, timeout: int = 20) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/query"
    resp = requests.post(url, json={"q": q}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def parse_answer_citations(answer_text: str) -> List[str]:
    # Expect a trailing line like: "Citations: ds1, ds2"
    lines = [l.strip() for l in answer_text.splitlines() if l.strip()]
    for line in reversed(lines):
        if line.lower().startswith("citations:"):
            items = line.split(":", 1)[1].strip()
            if items and items != "(none)":
                return [x.strip() for x in items.split(",") if x.strip()]
            return []
    return []


def render_result(data: Dict[str, Any]):
    # Top: natural-language answer
    st.subheader("Answer")
    st.markdown(data.get("answer", "_No answer returned._"))

    # Citations (from both structured and parsed from answer for redundancy)
    st.subheader("Citations")
    parsed_cites = parse_answer_citations(data.get("answer", ""))
    structured_cites = [c.get("dataset", "?") for c in data.get("citations", [])]
    merged = list(dict.fromkeys([*parsed_cites, *structured_cites]))  # de-dup, preserve order
    if merged:
        st.write(", ".join(merged))
    else:
        st.write("(none)")

    # Metadata columns
    c1, c2, c3 = st.columns(3)
    c1.metric("Answer source", data.get("answer_source", "-"))
    c2.metric("Datasets", len(data.get("datasets", [])))
    c3.metric("Rows returned", len(data.get("rows", [])))

    with st.expander("Parsed query"):
        st.json(data.get("parsed", {}))

    with st.expander("Datasets"):
        if data.get("datasets"):
            for ds in data["datasets"]:
                st.write(f"- {ds}")
        else:
            st.write("(none)")

    with st.expander("Rows (preview)"):
        rows = data.get("rows", [])
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.write("No rows.")


def main():
    st.set_page_config(page_title="Project Samarth UI", layout="wide")
    st.title("Project Samarth — Ask Your Question")

    # Sidebar: configuration and samples
    with st.sidebar:
        st.header("Configuration")
        base_url = st.text_input("API Base URL", value=get_api_base_url(), help="FastAPI endpoint root.")
        # persist to session state when possible
        try:
            st.session_state.api_base_url = base_url.strip() or "http://127.0.0.1:8000"
        except Exception:
            pass

        st.markdown("---")
        st.header("Samples")
        samples = [
            # Trend
            "Show trend of rainfall in Kerala from 2009 to 2012",
            "Show wheat yield trend in Maharashtra since 2005",
            # Comparison
            "Compare rainfall in Karnataka vs Kerala between 2012 and 2016",
            "Compare rice yield across states in 2009",
            # Ranking / Top-K
            "Top 5 states with highest rainfall in 2010",
            "Top 5 rice-producing states in 2015",
            "Which state had the highest rainfall in 2010",
            # Aggregations
            "Average rainfall in Kerala over the last 5 years",
            "Total wheat production in Punjab from 2012 to 2014",
        ]
        sample_q = st.selectbox("Pick a sample question", options=["(none)"] + samples, index=0)
        if sample_q != "(none)":
            st.session_state.input_q = sample_q
        with st.expander("Prompt tips"):
            st.markdown(
                """
                - Trend: “trend”, “over time”, or year ranges (e.g., 2010–2015) or relative periods (e.g., “last 5 years”, “since 2005”).
                - Comparison: “compare A vs B”, “across states/crops”.
                - Ranking: “top 5”, “highest/lowest”, “which state/crop …”.
                - Aggregations: “average/mean”, “total/sum”, “min”, “max”.
                - Metrics & domain: rainfall (climate); yield, production, area (agriculture).
                - Filters: name states (e.g., Kerala, Punjab) and crops (e.g., Rice, Wheat) explicitly.
                - Grouping hints: “across states/by state”, “across crops/by crop”.
                """
            )
        st.markdown("---")
        st.header("History")
        history: List[Dict[str, Any]] = st.session_state.get("history", [])
        if history:
            for h in history[-10:][::-1]:
                st.write(f"- {h['ts']}: {h['q']}")
        else:
            st.caption("No history yet.")

    # Main input area
    # Display resolved API URL without requiring session state
    st.caption(f"API: {base_url.strip() or 'http://127.0.0.1:8000'}")
    q = st.text_area(
        "Your question",
        key="input_q",
        height=80,
        placeholder="Examples: Top 5 states with highest rainfall in 2010; Average rainfall in Kerala last 5 years; Compare rice yield across states in 2009",
    )
    cols = st.columns([1, 1, 6])
    ask = cols[0].button("Ask")
    clear = cols[1].button("Clear")

    if clear:
        st.session_state.pop("input_q", None)
        st.experimental_rerun()

    if ask:
        if not q or not q.strip():
            st.warning("Please enter a question.")
            return
        try:
            with st.spinner("Asking API..."):
                start = time.time()
                data = call_query_api(base_url.strip() or "http://127.0.0.1:8000", q.strip())
                dur_ms = int((time.time() - start) * 1000)
            st.success(f"Done in {dur_ms} ms")
            render_result(data)
            # Append to history
            history = st.session_state.get("history", [])
            history.append({"q": q.strip(), "ts": time.strftime("%H:%M:%S")})
            st.session_state.history = history
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
        except Exception as e:
            st.exception(e)


if __name__ == "__main__":
    main()
