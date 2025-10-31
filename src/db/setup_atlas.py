from __future__ import annotations

"""
One-time MongoDB setup helper for Atlas M0 (or local Mongo).

Reads .env (if present), connects using MONGODB_URI/MONGODB_DB, and ensures
recommended collections and indexes exist. Safe to run multiple times.

Usage (Windows PowerShell):
  .\.venv\Scripts\Activate.ps1
  python .\src\db\setup_atlas.py
"""

import os
from datetime import datetime
from typing import Optional

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if v is not None and v != "" else default


def main() -> int:
    uri = get_env("MONGODB_URI", "mongodb://localhost:27017")
    dbname = get_env("MONGODB_DB", "samarth")
    print(f"Connecting to MongoDB: {uri} (db={dbname})")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
    except PyMongoError as e:
        print(f"ERROR: Cannot connect to MongoDB: {e}")
        return 1

    db = client[dbname]

    # Ensure collections exist by referencing them
    queries = db.get_collection("queries")
    cache = db.get_collection("cache")

    # Minimal indexes
    try:
        # queries: basic indexes for typical lookups
        queries.create_index([("created_at", DESCENDING)])
        queries.create_index([("answer_source", ASCENDING)])
        queries.create_index([("q", "text")])  # text search on question

        # cache: index on created_at for maintenance; TTL optional
        cache.create_index([("created_at", DESCENDING)])
        ttl_env = get_env("CACHE_TTL_SECONDS")
        if ttl_env and ttl_env.isdigit():
            # TTL index requires an ascending index on a date field with expireAfterSeconds
            cache.create_index([("created_at", ASCENDING)], expireAfterSeconds=int(ttl_env))
    except PyMongoError as e:
        print(f"WARNING: Index creation issue: {e}")

    # Touch a doc to confirm write perms (then delete)
    try:
        probe_id = queries.insert_one({
            "_type": "setup_probe",
            "created_at": datetime.utcnow(),
            "note": "ok to delete",
        }).inserted_id
        queries.delete_one({"_id": probe_id})
        print("MongoDB setup complete. Collections and indexes ensured.")
        return 0
    except PyMongoError as e:
        print(f"ERROR: Cannot write to database: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
