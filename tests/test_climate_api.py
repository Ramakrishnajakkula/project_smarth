from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_state_annual_basic():
    r = client.get("/climate/state-annual?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_state_annual_filter_state_or_year():
    # Try filtering by a known structure; may be empty if filters don't match
    r = client.get("/climate/state-annual", params={"year": 2009})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # If data exists for 2009, all returned rows should have Year=2009
    for row in data:
        assert row["Year"] == 2009


def test_subdivision_annual_basic():
    r = client.get("/climate/subdivision-annual?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 5
