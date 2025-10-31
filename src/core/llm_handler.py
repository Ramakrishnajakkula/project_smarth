from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ..utils.config import settings

try:
    from huggingface_hub import InferenceClient  # type: ignore
except Exception:  # pragma: no cover - optional dep issues shouldn't break local fallback
    InferenceClient = None  # type: ignore


@dataclass
class LLMAnswer:
    answer: str
    source: str  # "huggingface" | "fallback"


def _build_prompt(parsed: dict, rows: list[dict], citations: list[dict]) -> str:
    # Keep it short and deterministic; use a few top rows only
    sample_rows = rows[:5]
    ds_names = ", ".join(sorted({c.get("dataset", "?") for c in citations})) or "(none)"
    prompt = [
        "You are a helpful data assistant.",
        "Use the provided parsed query and data rows to answer briefly and clearly.",
        "Answer guidelines:",
        "- Be concise (2-3 sentences).",
        "- If relevant, mention dataset names in parentheses inside the prose.",
        "- Crucially: append a final line exactly in the format 'Citations: <comma-separated dataset names>' using only this ground-truth list:",
        f"  Ground truth datasets: {ds_names}",
        "- Do NOT invent or add external sources.",
        "\nParsed:", str(parsed),
        "\nRows (sample):", str(sample_rows),
        "\nCitations:", str(citations),
        "\nNow produce the answer followed by the Citations line.",
    ]
    return "\n".join(prompt)


def _fallback_answer(parsed: dict, rows: list[dict], citations: list[dict]) -> LLMAnswer:
    # Simple deterministic summary without external calls
    intent = parsed.get("intent", "unknown")
    states = parsed.get("states") or []
    crops = parsed.get("crops") or []
    years = parsed.get("years") or []
    yrng = parsed.get("year_range")
    datasets = ", ".join({c.get("dataset", "?") for c in citations}) or "datasets"
    scope_bits = []
    if states:
        scope_bits.append(f"states: {', '.join(states[:3])}")
    if crops:
        scope_bits.append(f"crops: {', '.join(crops[:3])}")
    if years:
        scope_bits.append(f"years: {', '.join(map(str, years[:3]))}")
    if yrng:
        # Use ASCII hyphen to avoid console encoding issues
        scope_bits.append(f"range: {yrng[0]}-{yrng[1]}")
    scope = "; ".join(scope_bits) or "no specific filters"
    n = len(rows)
    msg = (
        f"Parsed intent: {intent}. Using {n} matching rows ({datasets}); scope: {scope}. "
        "Refer to the returned rows for details; you can refine filters for a tighter view.\n"
        f"Citations: {datasets or '(none)'}"
    )
    return LLMAnswer(answer=msg, source="fallback")


def answer(parsed: dict, rows: list[dict], citations: list[dict]) -> LLMAnswer:
    token = settings.hf_api_token.strip()
    if not token or InferenceClient is None:
        return _fallback_answer(parsed, rows, citations)

    try:
        client = InferenceClient(token=token)
        # A small, widely available instruction-tuned model is preferred. Keep it generic to avoid tight coupling.
        model = "HuggingFaceH4/zephyr-7b-beta"
        prompt = _build_prompt(parsed, rows, citations)
        # Keep max tokens small for free-tier friendliness
        resp = client.text_generation(model=model, prompt=prompt, max_new_tokens=128, temperature=0.3)
        text = resp if isinstance(resp, str) else str(resp)
        return LLMAnswer(answer=text.strip(), source="huggingface")
    except Exception:
        # Fall back gracefully on any network or API error
        return _fallback_answer(parsed, rows, citations)
