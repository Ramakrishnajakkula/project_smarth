from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_datasets_endpoint():
    r = client.get("/datasets")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Expect at least one dataset present
    assert any(d["id"].startswith("climate:") or d["id"].startswith("agriculture:") for d in data)


def test_stats_endpoint():
    r = client.get("/stats")
    assert r.status_code == 200
    data = r.json()
    assert "climate" in data and "agriculture" in data
    assert isinstance(data["climate"].get("state_annual_rows", 0), int)
