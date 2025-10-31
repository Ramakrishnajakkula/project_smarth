from __future__ import annotations
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed" / "climate"

# Input files (produced by downloader)
RECENT_RAINFALL = RAW / "climate_rainfall_state_year.csv"
HISTORICAL_RAINFALL = RAW / "climate_rainfall_subdivision_historical.csv"

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
MONTH_MAP = {m: i + 1 for i, m in enumerate(MONTHS)}


def to_float(x):
    try:
        return float(str(x).strip())
    except Exception:
        return 0.0


def process_recent_state_annual():
    """Aggregate state rainfall to annual totals per state-year.
    Expected columns (flexible):
    - Either explicit year/month columns: state_name, year, month, actual
    - Or a date column to derive year: state_name, date (YYYY-MM-DD), actual
    Output: data/processed/climate/rainfall_state_year.csv
    """
    if not RECENT_RAINFALL.exists():
        print(f"Skip: not found {RECENT_RAINFALL}")
        return

    PROC.mkdir(parents=True, exist_ok=True)
    out_csv = PROC / "rainfall_state_year.csv"

    agg = {}  # (state, year) -> sum(actual)
    with open(RECENT_RAINFALL, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            state = (row.get("state_name") or row.get("State") or "").strip()
            # Try to read year directly, else derive from date
            year = (row.get("year") or row.get("Year") or "").strip()
            if not year:
                date_str = (row.get("date") or row.get("Date") or "").strip()
                if date_str:
                    # Accept formats like YYYY-MM-DD or DD/MM/YYYY; take first 4-digit year occurrence
                    # Common case in our dataset: YYYY-MM-DD
                    # Fallback: split by non-digits and pick a 4-digit token
                    y = ""
                    if len(date_str) >= 4 and date_str[0:4].isdigit():
                        y = date_str[0:4]
                    else:
                        for token in [t for t in date_str.replace("/", "-").split("-") if t]:
                            if len(token) == 4 and token.isdigit():
                                y = token
                                break
                    year = y

            actual = to_float(row.get("actual"))
            if not state or not year:
                continue
            key = (state, year)
            agg[key] = agg.get(key, 0.0) + actual

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["State", "Year", "Annual_Rainfall_mm"])
        for (state, year), total in sorted(agg.items()):
            w.writerow([state, year, f"{total:.3f}"])

    print(f"Saved: {out_csv} | rows: {len(agg)}")


def process_historical_subdivision_long():
    """Reshape wide subdivision rainfall (1901-2017) to long MONTH rows.
    Input columns: SUBDIVISION, YEAR, JAN..DEC, ANNUAL
    Output: data/processed/climate/rainfall_subdivision_long.csv
    and annual totals as rainfall_subdivision_year.csv
    """
    if not HISTORICAL_RAINFALL.exists():
        print(f"Skip: not found {HISTORICAL_RAINFALL}")
        return

    PROC.mkdir(parents=True, exist_ok=True)
    out_long = PROC / "rainfall_subdivision_long.csv"
    out_annual = PROC / "rainfall_subdivision_year.csv"

    # Long table
    with open(HISTORICAL_RAINFALL, "r", encoding="utf-8", errors="ignore") as f_in, \
         open(out_long, "w", newline="", encoding="utf-8") as f_out:
        r = csv.DictReader(f_in)
        w = csv.writer(f_out)
        w.writerow(["Subdivision", "Year", "Month", "Rainfall_mm"])
        for row in r:
            sub = (row.get("SUBDIVISION") or row.get("Subdivision") or "").strip()
            year = (row.get("YEAR") or row.get("Year") or "").strip()
            if not sub or not year:
                continue
            for m in MONTHS:
                val = row.get(m)
                if val is None:
                    continue
                mm = to_float(val)
                w.writerow([sub, year, MONTH_MAP[m], f"{mm:.3f}"])

    # Annual table
    agg = {}
    with open(out_long, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            key = (row["Subdivision"], row["Year"])
            agg[key] = agg.get(key, 0.0) + to_float(row["Rainfall_mm"])

    with open(out_annual, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Subdivision", "Year", "Annual_Rainfall_mm"])
        for (sub, year), total in sorted(agg.items()):
            w.writerow([sub, year, f"{total:.3f}"])

    print(f"Saved: {out_long}")
    print(f"Saved: {out_annual} | rows: {len(agg)}")


def main():
    process_recent_state_annual()
    process_historical_subdivision_long()


if __name__ == "__main__":
    main()
