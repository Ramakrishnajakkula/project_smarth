from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Any, Dict, List, Optional, Tuple, Union

from .query_parser import ParsedQuery

ROOT = Path(__file__).resolve().parents[2]
AG_PROC = ROOT / "data" / "processed" / "agriculture"
CL_PROC = ROOT / "data" / "processed" / "climate"


def _read_csv(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        r = csv.DictReader(f)
        return list(r)


@dataclass
class RoutedResult:
    datasets: List[str]
    citations: List[Dict[str, str]]
    rows: List[Dict[str, Any]]


def _filter_years(row_year: Union[int, str], years: List[int], year_range: Optional[Tuple[int, int]]) -> bool:
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
    datasets: List[str] = []
    citations: List[Dict[str, str]] = []
    rows: List[Dict[str, Any]] = []
    # Helpers inside to keep function self-contained
    def _apply_relative_years(years: List[int], year_range: Optional[Tuple[int, int]], last_n_years: Optional[int], since_year: Optional[int], available_years: List[int]) -> Tuple[List[int], Optional[Tuple[int, int]]]:
        if years or year_range:
            return years, year_range
        if not available_years:
            return years, year_range
        max_year = max(available_years)
        min_year = min(available_years)
        if last_n_years and last_n_years > 0:
            start = max(min_year, max_year - last_n_years + 1)
            return years, (start, max_year)
        if since_year and since_year <= max_year:
            start = max(min_year, since_year)
            return years, (start, max_year)
        return years, year_range

    # -------- Climate: rainfall --------
    if (pq.domain == "climate") or ("rainfall" in pq.metrics):
        path = CL_PROC / "rainfall_state_year.csv"
        data = _read_csv(path)
        datasets.append("climate:rainfall_state_year")
        citations.append({"dataset": "rainfall_state_year", "path": str(path)})

        # Collect available years first
        avail_years: List[int] = []
        for d in data:
            try:
                avail_years.append(int(d.get("Year", 0)))
            except Exception:
                continue
        yrs, yrng = _apply_relative_years(pq.years, pq.year_range, pq.last_n_years, pq.since_year, avail_years)

        # If ranking without explicit group_by, default to state
        group_by = pq.group_by or ("state" if pq.intent in ("ranking", "comparison") else None)
        agg = pq.aggregation
        top_k = pq.top_k

        # Build filtered rows
        filtered: List[Dict[str, Any]] = []
        for d in data:
            s = d.get("State", "")
            y = d.get("Year", 0)
            if pq.states and s not in pq.states:
                continue
            if not _filter_years(y, yrs, yrng):
                continue
            filtered.append({
                "State": s,
                "Year": int(y) if str(y).isdigit() else y,
                "Annual_Rainfall_mm": float(d.get("Annual_Rainfall_mm", "0") or 0),
            })

        # Trend -> return time series
        if pq.intent == "trend" or group_by == "year":
            rows = sorted(filtered, key=lambda r: (r["State"], r["Year"]))
            return RoutedResult(datasets=datasets, citations=citations, rows=rows)

        # Ranking / Aggregation across states
        if group_by == "state":
            # Group values per state
            by_state: Dict[str, List[float]] = {}
            for r in filtered:
                by_state.setdefault(r["State"], []).append(r["Annual_Rainfall_mm"])
            agg_rows: List[Dict[str, Any]] = []
            for st, vals in by_state.items():
                if not vals:
                    continue
                if agg == "avg":
                    val = sum(vals) / max(1, len(vals))
                elif agg == "min":
                    val = min(vals)
                elif agg == "max":
                    val = max(vals)
                else:  # default sum
                    val = sum(vals)
                agg_rows.append({"State": st, "Value": val})
            # Sort desc for top/highest by default
            agg_rows.sort(key=lambda r: r["Value"], reverse=True)
            if top_k:
                agg_rows = agg_rows[: top_k]
            return RoutedResult(datasets=datasets, citations=citations, rows=agg_rows)

        # Otherwise, just return filtered rows
        return RoutedResult(datasets=datasets, citations=citations, rows=filtered)

    # -------- Agriculture: crop APY --------
    if (pq.domain == "agriculture") or any(m in pq.metrics for m in ["yield", "production", "area"]) or pq.crops:
        path = AG_PROC / "crop_apy_state_year.csv"
        data = _read_csv(path)
        datasets.append("agriculture:crop_apy_state_year")
        citations.append({"dataset": "crop_apy_state_year", "path": str(path)})

        # Determine available start years from labels like "2009-10"
        avail_years: List[int] = []
        for d in data:
            label = d.get("Year", "")
            try:
                avail_years.append(int(str(label).split("-")[0]))
            except Exception:
                continue
        yrs, yrng = _apply_relative_years(pq.years, pq.year_range, pq.last_n_years, pq.since_year, avail_years)

        # Choose numeric field by metric priority
        metric_field = "Yield_t_per_ha"
        if "production" in pq.metrics:
            metric_field = "Production_tonnes"
        elif "area" in pq.metrics:
            metric_field = "Area_ha"
        elif "yield" in pq.metrics:
            metric_field = "Yield_t_per_ha"

        # Default grouping: comparison/ranking across states
        group_by = pq.group_by or ("state" if pq.intent in ("ranking", "comparison") else None)
        agg = pq.aggregation
        top_k = pq.top_k

        filtered: List[Dict[str, Any]] = []
        for d in data:
            s = d.get("State", "")
            y_label = d.get("Year", "")
            crop = d.get("Crop", "")
            # Filters
            if pq.states and s not in pq.states:
                continue
            if pq.crops and crop not in pq.crops:
                continue
            # Year filtering using start year
            if yrs:
                if not any(str(yr) in str(y_label) for yr in yrs):
                    continue
            if yrng:
                try:
                    start_year = int(str(y_label).split("-")[0])
                except Exception:
                    continue
                if not (yrng[0] <= start_year <= yrng[1]):
                    continue
            try:
                val = float(d.get(metric_field, "0") or 0)
            except Exception:
                val = 0.0
            filtered.append({
                "State": s,
                "Year": y_label,
                "Crop": crop,
                metric_field: val,
            })

        # Trend -> return by year for first matching state/crop if specified; else all rows (may be large)
        if pq.intent == "trend" or group_by == "year":
            rows = sorted(filtered, key=lambda r: (r.get("State", ""), r.get("Crop", ""), r.get("Year", "")))
            return RoutedResult(datasets=datasets, citations=citations, rows=rows)

        # Group and aggregate across states (or crops)
        key_field = "State" if group_by == "state" else ("Crop" if group_by == "crop" else None)
        if key_field:
            grouped: Dict[str, List[float]] = {}
            for r in filtered:
                grouped.setdefault(r[key_field], []).append(r.get(metric_field, 0.0))
            agg_rows: List[Dict[str, Any]] = []
            for key, vals in grouped.items():
                if not vals:
                    continue
                if agg == "avg" or (agg is None and metric_field == "Yield_t_per_ha"):
                    # default to average for yield if not specified
                    val = sum(vals) / max(1, len(vals))
                elif agg == "min":
                    val = min(vals)
                elif agg == "max":
                    val = max(vals)
                else:
                    val = sum(vals)
                agg_rows.append({key_field: key, "Metric": metric_field, "Value": val})
            # Sort high-to-low by default
            agg_rows.sort(key=lambda r: r["Value"], reverse=True)
            if top_k:
                agg_rows = agg_rows[: top_k]
            return RoutedResult(datasets=datasets, citations=citations, rows=agg_rows)

        # Otherwise return filtered rows
        return RoutedResult(datasets=datasets, citations=citations, rows=filtered)

    # Fallback: return empty
    return RoutedResult(datasets=datasets, citations=citations, rows=rows)
