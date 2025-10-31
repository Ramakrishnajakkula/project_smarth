import os
import sys
from pathlib import Path
import requests
import csv
import re
from urllib.parse import urljoin, urlparse
import yaml
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "datasets.manifest.yaml"
RAW_DIR = ROOT / "data" / "raw"

# Load environment variables from .env if present (for DATA_GOV_IN_API_KEY)
load_dotenv()


def load_manifest(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def filename_for(entry: dict) -> Path:
    fmt = entry.get("format", "csv").lower()
    key = entry["key"]
    # Default extension by format
    ext = {
        "csv": ".csv",
        "parquet": ".parquet",
        "zip": ".zip",
        "json": ".json",
    }.get(fmt, ".dat")
    return RAW_DIR / f"{key}{ext}"


def is_probably_file_url(url: str) -> bool:
    lower = url.lower()
    return any(lower.endswith(ext) for ext in (".csv", ".parquet", ".zip", ".json"))


def choose_download_url(entry: dict) -> Optional[str]:
    """Prefer direct file URLs. Fallback order: csv_alternative -> url -> alternative_url -> backup_url."""
    for field in ("csv_alternative", "url", "alternative_url", "backup_url"):
        u = (entry.get(field) or "").strip()
        if not u:
            continue
        # Prefer links that look like direct files
        if is_probably_file_url(u):
            return u
    # If none looked like files, return the first non-empty as last resort
    for field in ("csv_alternative", "url", "alternative_url", "backup_url"):
        u = (entry.get(field) or "").strip()
        if u:
            return u
    return None


def resolve_ckan_download(url: str) -> Optional[str]:
    """If the URL is a CKAN resource page (no direct file), try to find a /download/.csv link on the page."""
    try:
        headers = {"User-Agent": "ProjectSamarth/1.0 (+https://github.com/)"}
        resp = requests.get(url, timeout=60, headers=headers)
        resp.raise_for_status()
        if "text/html" not in resp.headers.get("Content-Type", "").lower():
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        # Look for anchors that contain 'download' in href or end with a known extension
        candidates = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            href_lower = href.lower()
            if "/download/" in href_lower or href_lower.endswith((".csv", ".zip", ".json", ".parquet")):
                candidates.append(urljoin(url, href))
        # Prefer CSV, then Parquet/ZIP/JSON
        for ext in (".csv", ".parquet", ".zip", ".json"):
            for c in candidates:
                if c.lower().endswith(ext):
                    return c
        # If nothing ends with extension, return first candidate if any
        if candidates:
            return candidates[0]
    except Exception:
        return None
    return None


def download_file(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "ProjectSamarth/1.0 (+https://github.com/)"}
    with requests.get(url, stream=True, timeout=90, headers=headers) as r:
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "").lower()
        if "text/html" in ctype and not is_probably_file_url(url):
            raise ValueError(
                "URL appears to be a web page, not a direct file. "
                "Please provide a direct CSV/Parquet link (use csv_alternative/alternative_url)."
            )
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def fetch_datagov_api(api_endpoint: str, api_key: str, dest: Path, per_page: int = 1000, max_pages: int = 1000):
    """Fetch paginated JSON records from data.gov.in API and save as CSV."""
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": per_page,
        "offset": 0,
    }
    headers = {"User-Agent": "ProjectSamarth/1.0 (+https://github.com/)"}

    dest.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    total = 0

    for page in range(max_pages):
        params["offset"] = page * per_page
        resp = requests.get(api_endpoint, params=params, timeout=90, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        records = data.get("records") or data.get("data") or []
        if not records:
            break

        # Initialize CSV writer on first page
        if writer is None:
            fieldnames = sorted({k for rec in records for k in rec.keys()})
            f = open(dest, "w", newline="", encoding="utf-8")
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

        for rec in records:
            writer.writerow(rec)
            total += 1

        # Be polite to API
        time.sleep(0.2)

        # Stop early if last page (if fewer than per_page returned)
        if len(records) < per_page:
            break

    if writer is not None:
        writer.writerows([])  # flush
        writer = None

    if total == 0:
        raise RuntimeError("No records returned from data.gov.in API; check api_endpoint and API key.")


def main():
    if not MANIFEST.exists():
        print(f"Manifest not found at {MANIFEST}")
        sys.exit(1)

    doc = load_manifest(MANIFEST)
    datasets = doc.get("datasets", [])
    if not datasets:
        print("No datasets found in manifest.")
        sys.exit(0)

    total = 0
    for entry in datasets:
        key = entry.get("key")
        url = choose_download_url(entry)
        key = entry.get("key")
        if not url:
            print(f"- Skipping {key}: no usable URL found (set url/csv_alternative/alternative_url)")
            # Try API fallback if provided and API key available
            api_ep = (entry.get("api_endpoint") or "").strip()
            api_key = os.getenv("DATA_GOV_IN_API_KEY")
            if api_ep and api_key:
                dest = filename_for(entry)
                try:
                    print(f"  Falling back to data.gov.in API for {key} -> {dest}")
                    fetch_datagov_api(api_ep, api_key, dest)
                    total += 1
                    continue
                except Exception as ee:
                    print(f"  API fallback failed for {key}: {ee}")
            continue
        dest = filename_for(entry)
        try:
            # If CKAN resource page without direct file, try to resolve to download link
            if (not is_probably_file_url(url)) and ("ckandev.indiadataportal.com" in urlparse(url).netloc):
                resolved = resolve_ckan_download(url)
                if resolved:
                    print(f"- Resolved CKAN link for {key}: {resolved}")
                    url = resolved
            # If final URL looks like a direct file, adjust destination extension accordingly
            if is_probably_file_url(url):
                parsed = urlparse(url)
                path = parsed.path.lower()
                for ext in (".csv", ".parquet", ".zip", ".json"):
                    if path.endswith(ext):
                        dest = dest.with_suffix(ext)
                        break
            print(f"- Downloading {key} from {url} -> {dest}")
            download_file(url, dest)
            total += 1
        except Exception as e:
            print(f"  Error downloading {key}: {e}")
            # Try API fallback on failure
            api_ep = (entry.get("api_endpoint") or "").strip()
            api_key = os.getenv("DATA_GOV_IN_API_KEY")
            if api_ep and api_key:
                try:
                    print(f"  Falling back to data.gov.in API for {key} -> {dest}")
                    fetch_datagov_api(api_ep, api_key, dest)
                    total += 1
                except Exception as ee:
                    print(f"  API fallback failed for {key}: {ee}")

    print(f"Done. Downloaded {total} files to {RAW_DIR}")


if __name__ == "__main__":
    main()
