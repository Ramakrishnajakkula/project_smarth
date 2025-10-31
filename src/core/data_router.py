from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Any

from .query_parser import ParsedQuery

ROOT = Path(__file__).resolve().parents[2]
AG_PROC = ROOT / "data" / "processed" / "agriculture"
CL_PROC = ROOT / "data" / "processed" / "climate"


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        r = csv.DictReader(f)
        return list(r)


@dataclass
class RoutedResult:
    datasets: list[str]
    citations: list[dict[str, str]]
    rows: list[dict[str, Any]]


def _filter_years(row_year: int | str, years: list[int], year_range: tuple[int, int] | None) -> bool:
    try:
        y = int(row_year)
    except Exception:
        return False
    if years and y not in years:
        return False
    if year_range and not (year_range[0] <= y <= year_range[1]):
        return False
    return True


def route_query(pq: ParsedQuery) -> RoutedResult:
    # Default empty
    datasets: list[str] = []
    citations: list[dict[str, str]] = []
    rows: list[dict[str, Any]] = []

    # Trend intent on rainfall by state
    if pq.intent == "trend" and ("rainfall" in pq.metrics or not pq.metrics):
        path = CL_PROC / "rainfall_state_year.csv"
        data = _read_csv(path)
        datasets.append("climate:rainfall_state_year")
        citations.append({
            "dataset": "rainfall_state_year",
            "path": str(path),
        })
        for d in data:
            s = d.get("State", "")
            y = d.get("Year", 0)
            if pq.states and s not in pq.states:
                continue
            if not _filter_years(y, pq.years, pq.year_range):
                continue
            rows.append({
                "State": s,
                "Year": int(y),
                "Annual_Rainfall_mm": float(d.get("Annual_Rainfall_mm", "0") or 0),
            })
        return RoutedResult(datasets=datasets, citations=citations, rows=rows)

    # Comparison intent on crop yield/production across states for a year
    if pq.intent == "comparison" and ("yield" in pq.metrics or "production" in pq.metrics or not pq.metrics) and pq.crops:
        path = AG_PROC / "crop_apy_state_year.csv"
        data = _read_csv(path)
        datasets.append("agriculture:crop_apy_state_year")
        citations.append({
            "dataset": "crop_apy_state_year",
            "path": str(path),
        })
        for d in data:
            s = d.get("State", "")
            y_label = d.get("Year", "")  # e.g., 2009-10
            crop = d.get("Crop", "")
            # If user specified discrete Gregorian years, approximate matching by prefix (e.g., 2009 matches 2009-10)
            if pq.years and not any(str(yr) in y_label for yr in pq.years):
                continue
            if pq.year_range:
                # include rows where starting year falls in range
                try:
                    start_year = int(y_label.split("-")[0])
                    if not (pq.year_range[0] <= start_year <= pq.year_range[1]):
                        continue
                except Exception:
                    continue
            if pq.states and s not in pq.states:
                continue
            if crop not in pq.crops:
                continue
            row = {
                "State": s,
                "Year": y_label,
                "Crop": crop,
                "Area_ha": float(d.get("Area_ha", "0") or 0),
                "Production_tonnes": float(d.get("Production_tonnes", "0") or 0),
                "Yield_t_per_ha": float(d.get("Yield_t_per_ha", "0") or 0),
            }
            rows.append(row)
        return RoutedResult(datasets=datasets, citations=citations, rows=rows)

    # Fallback: return empty with hint
    return RoutedResult(
        datasets=datasets,
        citations=citations,
        rows=rows,
    )
