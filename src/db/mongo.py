from typing import Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from ..utils.config import settings

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongodb_uri)
    return _client


def ping() -> dict:
    """Ping MongoDB and return server info or error."""
    try:
        client = get_client()
        # The ping command is cheap and does not require auth beyond connection
        client.admin.command("ping")
        return {"ok": True}
    except PyMongoError as e:
        return {"ok": False, "error": str(e)}


def get_db():
    """Get the configured database handle."""
    client = get_client()
    return client[settings.mongodb_db]


def get_collection(name: str):
    """Get a collection handle by name from the configured database."""
    db = get_db()
    return db[name]
