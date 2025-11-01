from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
import csv
from typing import List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
AG_PROC = ROOT / "data" / "processed" / "agriculture"
CL_PROC = ROOT / "data" / "processed" / "climate"


@dataclass
class ParsedQuery:
    text: str
    intent: str = "unknown"  # trend | comparison | correlation | ranking | unknown
    states: List[str] = field(default_factory=list)
    crops: List[str] = field(default_factory=list)
    years: List[int] = field(default_factory=list)  # discrete years
    year_range: Optional[Tuple[int, int]] = None  # (start, end)
    metrics: List[str] = field(default_factory=list)  # rainfall | area | production | yield
    # Extended NLP fields
    aggregation: Optional[str] = None  # avg|sum|min|max
    top_k: Optional[int] = None  # e.g., top 5
    group_by: Optional[str] = None  # state|crop|year
    domain: Optional[str] = None  # climate|agriculture
    last_n_years: Optional[int] = None  # "last 5 years"
    since_year: Optional[int] = None  # "since 2005"


def _read_unique_values(path: Path, col: str) -> Set[str]:
    vals: Set[str] = set()
    if not path.exists():
        return vals
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        r = csv.DictReader(f)
        for row in r:
            v = (row.get(col) or "").strip()
            if v:
                vals.add(v)
    return vals


def _known_states() -> Set[str]:
    return _read_unique_values(CL_PROC / "rainfall_state_year.csv", "State")


def _known_crops() -> Set[str]:
    return _read_unique_values(AG_PROC / "crop_apy_state_year.csv", "Crop")


def _detect_intent(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["trend", "over time", "year by year"]):
        return "trend"
    if any(w in t for w in ["compare", "comparison", "vs", "versus", "between"]):
        return "comparison"
    if any(w in t for w in ["correlat", "relationship"]):
        return "correlation"
    if any(w in t for w in ["top", "rank", "highest", "lowest"]):
        return "ranking"
    return "unknown"


def _detect_metrics(text: str) -> List[str]:
    t = text.lower()
    metrics: List[str] = []
    if "rain" in t:
        metrics.append("rainfall")
    if any(w in t for w in ["yield", "productivity"]):
        metrics.append("yield")
    if any(w in t for w in ["area", "sown"]):
        metrics.append("area")
    if any(w in t for w in ["production", "output", "tonne"]):
        metrics.append("production")
    return metrics


def _detect_years(text: str) -> Tuple[List[int], Optional[Tuple[int, int]]]:
    # Find 4-digit years
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]
    # Detect ranges like 2009-2012 or 2009 to 2012
    m = re.search(r"(19\d{2}|20\d{2})\s*[-to]+\s*(19\d{2}|20\d{2})", text)
    year_range = None
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a <= b:
            year_range = (a, b)
        else:
            year_range = (b, a)
    return years, year_range


def _detect_relative_years(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Detect phrases like 'last 5 years' and 'since 2005'.

    Returns (last_n_years, since_year).
    """
    t = text.lower()
    last_n: Optional[int] = None
    since_y: Optional[int] = None
    m = re.search(r"last\s+(\d{1,2})\s+years", t)
    if m:
        try:
            last_n = int(m.group(1))
        except Exception:
            last_n = None
    m2 = re.search(r"since\s+(19\d{2}|20\d{2})", t)
    if m2:
        try:
            since_y = int(m2.group(1))
        except Exception:
            since_y = None
    return last_n, since_y


def _detect_group_by(text: str, intent: str) -> Optional[str]:
    t = text.lower()
    if any(p in t for p in ["across states", "by state", "state-wise", "statewise"]):
        return "state"
    if any(p in t for p in ["across crops", "by crop", "crop-wise", "cropwise"]):
        return "crop"
    if intent == "trend":
        return "year"
    return None


def _detect_aggregation(text: str) -> Optional[str]:
    t = text.lower()
    if any(w in t for w in ["average", "avg", "mean"]):
        return "avg"
    if any(w in t for w in ["total", "sum", "overall"]):
        return "sum"
    if any(w in t for w in ["minimum", "min", "lowest"]):
        return "min"
    if any(w in t for w in ["maximum", "max", "highest"]):
        return "max"
    return None


def _detect_topk(text: str) -> Optional[int]:
    t = text.lower()
    m = re.search(r"(?:top|highest|lowest)\s+(\d{1,3})", t)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    # 'which' questions often imply top 1
    if t.startswith("which ") or "which state" in t or "which crop" in t:
        return 1
    return None


def _detect_domain(text: str, metrics: List[str]) -> Optional[str]:
    t = text.lower()
    if "rain" in t:
        return "climate"
    if any(m in (metrics or []) for m in ["yield", "production", "area"]):
        return "agriculture"
    # default unknown -> None
    return None


def _detect_entities_from_catalog(text: str) -> Tuple[List[str], List[str]]:
    states_list = sorted(_known_states(), key=len, reverse=True)
    crops_list = sorted(_known_crops(), key=len, reverse=True)
    states: List[str] = []
    crops: List[str] = []
    tl = text.lower()
    for s in states_list:
        if s and s.lower() in tl:
            states.append(s)
    for c in crops_list:
        if c and c.lower() in tl:
            crops.append(c)
    return states, crops


def parse_query(text: str) -> ParsedQuery:
    years, year_range = _detect_years(text)
    last_n_years, since_year = _detect_relative_years(text)
    intent = _detect_intent(text)
    metrics = _detect_metrics(text)
    states, crops = _detect_entities_from_catalog(text)
    aggregation = _detect_aggregation(text)
    top_k = _detect_topk(text)
    group_by = _detect_group_by(text, intent)
    domain = _detect_domain(text, metrics)
    return ParsedQuery(
        text=text,
        intent=intent,
        states=states,
        crops=crops,
        years=years,
        year_range=year_range,
        metrics=metrics,
        aggregation=aggregation,
        top_k=top_k,
        group_by=group_by,
        domain=domain,
        last_n_years=last_n_years,
        since_year=since_year,
    )
