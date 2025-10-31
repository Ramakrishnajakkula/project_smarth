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


def _detect_metrics(text: str) -> list[str]:
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
    intent = _detect_intent(text)
    metrics = _detect_metrics(text)
    states, crops = _detect_entities_from_catalog(text)
    return ParsedQuery(
        text=text,
        intent=intent,
        states=states,
        crops=crops,
        years=years,
        year_range=year_range,
        metrics=metrics,
    )
