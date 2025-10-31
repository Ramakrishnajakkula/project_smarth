from __future__ import annotations
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed" / "agriculture"

SOURCE_FILE = RAW / "agriculture_crop_production_state_year.csv"


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def process_csv(csv_path: Path):
    if not csv_path.exists():
        raise FileNotFoundError(f"Source not found: {csv_path}")

    agg = {}  # (State, Year, Crop) -> [area_sum, production_sum]

    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        # Normalize header keys to lowercase for resilience
        fieldnames = [fn.strip().lower() for fn in reader.fieldnames or []]

        for row in reader:
            # Create lowercase key dict (handle None keys safely)
            row_l = { (k.strip().lower() if k else k): v for k, v in row.items() }

            # Possible column names based on observed dataset
            state = row_l.get("state_name") or row_l.get("state")
            year = row_l.get("crop_year") or row_l.get("year")
            crop = row_l.get("crop_name") or row_l.get("crop")

            if not state or not year or not crop:
                continue

            # Area/production columns
            # Dataset uses 'area' and 'production' values with separate unit columns
            area = safe_float(row_l.get("area"))
            production = safe_float(row_l.get("production"))

            key = (state.strip(), str(year).strip(), crop.strip())
            if key not in agg:
                agg[key] = [0.0, 0.0]
            agg[key][0] += area
            agg[key][1] += production

    # Write processed CSV
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out_csv = PROCESSED / "crop_apy_state_year.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["State", "Year", "Crop", "Area_ha", "Production_tonnes", "Yield_t_per_ha"])
        for (state, year, crop), (area_sum, prod_sum) in sorted(agg.items()):
            yield_val = (prod_sum / area_sum) if area_sum > 0 else ""
            writer.writerow([state, year, crop, f"{area_sum:.3f}", f"{prod_sum:.3f}", f"{yield_val:.6f}" if yield_val != "" else ""])

    print(f"Saved processed CSV: {out_csv} | rows: {len(agg)}")


def main():
    process_csv(SOURCE_FILE)


if __name__ == "__main__":
    main()
