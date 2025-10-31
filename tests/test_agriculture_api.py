from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_agri_basic_limit():
    r = client.get("/agriculture/crop-apy-state-year?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    if data:
        row = data[0]
        # Ensure all expected keys are present
        for k in [
            "State",
            "Year",
            "Crop",
            "Area_ha",
            "Production_tonnes",
            "Yield_t_per_ha",
        ]:
            assert k in row


def test_agri_filter_year_and_crop():
    # Try a commonly available pair; if empty, it's acceptable, but if data exists, it must match filters
    params = {"year": "2000-01", "crop": "Rice"}
    r = client.get("/agriculture/crop-apy-state-year", params=params)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for row in data:
        assert row["Year"] == "2000-01"
        assert row["Crop"] == "Rice"
