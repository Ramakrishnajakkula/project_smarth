import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


def _getenv(name: str, default: str = "") -> str:
    val = os.getenv(name)
    return val if val is not None else default


def _getbool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    api_host: str = _getenv("API_HOST", "0.0.0.0")
    api_port: int = int(_getenv("API_PORT", "8000"))

    mongodb_uri: str = _getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db: str = _getenv("MONGODB_DB", "samarth")

    hf_api_token: str = _getenv("HF_API_TOKEN", "")
    data_gov_in_api_key: str = _getenv("DATA_GOV_IN_API_KEY", "")

    log_level: str = _getenv("LOG_LEVEL", "INFO")
    log_file: str = _getenv("LOG_FILE", "logs/app.log")

    # Optional Mongo-backed cache for API CSV reads
    cache_enabled: bool = _getbool("CACHE_ENABLED", False)
    cache_ttl_seconds: int = int(_getenv("CACHE_TTL_SECONDS", "600"))
    cache_collection: str = _getenv("CACHE_COLLECTION", "cache")

    # Optional background logging of queries
    log_queries: bool = _getbool("LOG_QUERIES", False)
    log_queries_collection: str = _getenv("LOG_QUERIES_COLLECTION", "queries")
    log_queries_rows_sample: int = int(_getenv("LOG_QUERIES_ROWS_SAMPLE", "20"))


settings = Settings()
