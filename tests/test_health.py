from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"


def test_db_ping_shape():
    res = client.get("/db/ping")
    assert res.status_code == 200
    body = res.json()
    assert "ok" in body
