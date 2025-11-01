from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from ..utils.config import settings
from ..db.mongo import ping as mongo_ping, get_collection
from pathlib import Path
import csv
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from ..core.query_parser import parse_query
from ..core.data_router import route_query
from ..core.llm_handler import answer as llm_answer
import os

app = FastAPI(
    title="Project Samarth API",
    description="Minimal FastAPI scaffold with MongoDB ping",
    version="0.1.0",
)

# CORS for local dev / Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


class DBPingResponse(BaseModel):
    ok: bool
    error: Optional[str] = None


@app.get("/health")
async def health_check():
    # Lightweight health endpoint for container orchestrators
    return {"status": "ok", "version": app.version}


@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="healthy", version="0.1.0", timestamp=datetime.now())


@app.get("/db/ping", response_model=DBPingResponse)
async def db_ping():
    result = mongo_ping()
    return DBPingResponse(ok=result.get("ok", False), error=result.get("error"))


class QueryRequest(BaseModel):
    q: str


class QueryResponse(BaseModel):
    parsed: Dict
    datasets: List[str]
    citations: List[Dict]
    rows: List[Dict]
    answer: str
    answer_source: str


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    pq = parse_query(req.q)
    routed = route_query(pq)
    # Return a structured response to satisfy Phase 2 acceptance criteria
    parsed_dict: Dict = {
        "intent": pq.intent,
        "states": pq.states,
        "crops": pq.crops,
        "years": pq.years,
        "year_range": pq.year_range,
        "metrics": pq.metrics,
        "aggregation": pq.aggregation,
        "top_k": pq.top_k,
        "group_by": pq.group_by,
        "domain": pq.domain,
        "last_n_years": pq.last_n_years,
        "since_year": pq.since_year,
    }
    llm = llm_answer(parsed_dict, routed.rows, routed.citations)
    resp = QueryResponse(
        parsed=parsed_dict,
        datasets=routed.datasets,
        citations=routed.citations,
        rows=routed.rows[:100],
        answer=llm.answer,
        answer_source=llm.source,
    )
    # Background logging to MongoDB (optional, never breaks the response)
    if settings.log_queries:
        try:
            col = get_collection(settings.log_queries_collection)
            doc = {
                "q": req.q,
                "parsed": parsed_dict,
                "datasets": routed.datasets,
                "citations": routed.citations,
                "row_count": len(routed.rows),
                "rows_sample": routed.rows[: settings.log_queries_rows_sample],
                "answer_source": llm.source,
                "created_at": datetime.utcnow(),
                "version": app.version,
            }
            col.insert_one(doc)
        except Exception:
            # ignore logging errors entirely
            pass
    return resp


# Entry point hint: uvicorn src.api.main:app --reload


# ---------- Climate data endpoints ----------
ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed" / "climate"
AG_PROC = ROOT / "data" / "processed" / "agriculture"


class StateAnnual(BaseModel):
    State: str
    Year: int
    Annual_Rainfall_mm: float


class SubdivisionAnnual(BaseModel):
    Subdivision: str
    Year: int
    Annual_Rainfall_mm: float


def _read_csv_rows(path: Path):
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Processed file not found: {path.name}")
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            yield row


def _build_cache_key(endpoint: str, params: Dict[str, Any]) -> str:
    items = sorted((k, v) for k, v in params.items() if v is not None)
    return f"{endpoint}|" + "&".join(f"{k}={v}" for k, v in items)


def _cache_lookup(key: str):
    if not settings.cache_enabled:
        return None
    try:
        col = get_collection(settings.cache_collection)
        doc = col.find_one({"_id": key})
        if not doc:
            return None
        created_at = doc.get("created_at")
        if not created_at:
            return None
        if datetime.utcnow() - created_at > timedelta(seconds=settings.cache_ttl_seconds):
            col.delete_one({"_id": key})
            return None
        return doc.get("data")
    except Exception:
        return None


def _cache_store(key: str, data: Any):
    if not settings.cache_enabled:
        return
    try:
        col = get_collection(settings.cache_collection)
        col.replace_one(
            {"_id": key},
            {"_id": key, "created_at": datetime.utcnow(), "data": data},
            upsert=True,
        )
    except Exception:
        # Cache is optional; ignore failures
        pass


@app.get("/climate/state-annual", response_model=List[StateAnnual])
def get_state_annual(
    state: Optional[str] = Query(default=None, description="Filter by state name (exact match)"),
    year: Optional[int] = Query(default=None, description="Filter by year"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    cache_key = _build_cache_key("/climate/state-annual", {"state": state, "year": year, "limit": limit, "offset": offset})
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    path = PROC / "rainfall_state_year.csv"
    rows: List[Dict] = []
    for row in _read_csv_rows(path):
        s = row.get("State") or row.get("state") or ""
        y = int((row.get("Year") or row.get("year") or 0))
        if state and s != state:
            continue
        if year and y != year:
            continue
        try:
            val = float(row.get("Annual_Rainfall_mm", "0") or 0)
        except Exception:
            val = 0.0
        rows.append({"State": s, "Year": y, "Annual_Rainfall_mm": val})
    result = rows[offset : offset + limit]
    _cache_store(cache_key, result)
    return result


@app.get("/climate/subdivision-annual", response_model=List[SubdivisionAnnual])
def get_subdivision_annual(
    subdivision: Optional[str] = Query(default=None, description="Filter by subdivision name (exact match)"),
    year: Optional[int] = Query(default=None, description="Filter by year"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    cache_key = _build_cache_key("/climate/subdivision-annual", {"subdivision": subdivision, "year": year, "limit": limit, "offset": offset})
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    path = PROC / "rainfall_subdivision_year.csv"
    rows: List[Dict] = []
    for row in _read_csv_rows(path):
        s = row.get("Subdivision") or row.get("subdivision") or ""
        y = int((row.get("Year") or row.get("year") or 0))
        if subdivision and s != subdivision:
            continue
        if year and y != year:
            continue
        try:
            val = float(row.get("Annual_Rainfall_mm", "0") or 0)
        except Exception:
            val = 0.0
        rows.append({"Subdivision": s, "Year": y, "Annual_Rainfall_mm": val})
    result = rows[offset : offset + limit]
    _cache_store(cache_key, result)
    return result


# ---------- Agriculture data endpoints ----------

class CropAPYRow(BaseModel):
    State: str
    Year: str  # e.g., "2000-01"
    Crop: str
    Area_ha: float
    Production_tonnes: float
    Yield_t_per_ha: float


@app.get("/agriculture/crop-apy-state-year", response_model=List[CropAPYRow])
def get_crop_apy_state_year(
    state: Optional[str] = Query(default=None, description="Filter by state (exact match)"),
    crop: Optional[str] = Query(default=None, description="Filter by crop (exact match)"),
    year: Optional[str] = Query(default=None, description="Filter by year label, e.g., 2000-01"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    cache_key = _build_cache_key("/agriculture/crop-apy-state-year", {"state": state, "crop": crop, "year": year, "limit": limit, "offset": offset})
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    path = AG_PROC / "crop_apy_state_year.csv"
    rows: List[Dict] = []
    for row in _read_csv_rows(path):
        s = row.get("State", "")
        y = row.get("Year", "")
        c = row.get("Crop", "")
        if state and s != state:
            continue
        if crop and c != crop:
            continue
        if year and y != year:
            continue
        try:
            area = float(row.get("Area_ha", "0") or 0)
        except Exception:
            area = 0.0
        try:
            prod = float(row.get("Production_tonnes", "0") or 0)
        except Exception:
            prod = 0.0
        try:
            yld = float(row.get("Yield_t_per_ha", "0") or 0)
        except Exception:
            yld = 0.0
        rows.append(
            {
                "State": s,
                "Year": y,
                "Crop": c,
                "Area_ha": area,
                "Production_tonnes": prod,
                "Yield_t_per_ha": yld,
            }
        )
    result = rows[offset : offset + limit]
    _cache_store(cache_key, result)
    return result


# ---------- Datasets and Stats stubs ----------

def _line_count_minus_header(path: Path) -> int:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            n = sum(1 for _ in f)
        return max(0, n - 1)
    except Exception:
        return 0


def _file_meta(path: Path, kind: str) -> dict:
    stat = path.stat()
    return {
        "id": f"{kind}:{path.stem}",
        "kind": kind,
        "name": path.name,
        "path": str(path.relative_to(ROOT)),
        "bytes": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "rows": _line_count_minus_header(path),
    }


@app.get("/datasets", response_model=List[Dict])
def list_datasets():
    datasets: List[Dict] = []
    # Climate
    for p in (PROC.glob("*.csv")):
        datasets.append(_file_meta(p, "climate"))
    # Agriculture
    for p in ((ROOT / "data" / "processed" / "agriculture").glob("*.csv")):
        datasets.append(_file_meta(p, "agriculture"))
    return datasets


@app.get("/stats", response_model=Dict)
def basic_stats():
    stats: Dict[str, Any] = {"climate": {}, "agriculture": {}}
    # Climate counts
    state_year = PROC / "rainfall_state_year.csv"
    subdiv_year = PROC / "rainfall_subdivision_year.csv"
    stats["climate"]["state_annual_rows"] = _line_count_minus_header(state_year) if state_year.exists() else 0
    stats["climate"]["subdivision_annual_rows"] = _line_count_minus_header(subdiv_year) if subdiv_year.exists() else 0
    # Agriculture counts
    crop_apy = ROOT / "data" / "processed" / "agriculture" / "crop_apy_state_year.csv"
    stats["agriculture"]["crop_apy_rows"] = _line_count_minus_header(crop_apy) if crop_apy.exists() else 0
    return stats
