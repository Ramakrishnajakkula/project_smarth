from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_query_trend_rainfall_state():
    payload = {"q": "Show trend of rainfall in Kerala from 2009 to 2010"}
    r = client.post("/query", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["parsed"]["intent"] == "trend"
    assert "Kerala" in data["parsed"]["states"]
    assert "climate:rainfall_state_year" in data["datasets"]
    # rows may be empty if data missing, but should be a list
    assert isinstance(data["rows"], list)
    assert "answer" in data and isinstance(data["answer"], str)
    assert data.get("answer_source") in ("fallback", "huggingface")


def test_query_comparison_crop_yield():
    payload = {"q": "Compare yield of Rice across states in 2001"}
    r = client.post("/query", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["parsed"]["intent"] in ("comparison", "unknown")
    # Ensure crop was detected
    assert "Rice" in data["parsed"]["crops"]
    assert "agriculture:crop_apy_state_year" in data["datasets"] or data["datasets"] == []
    assert isinstance(data["rows"], list)
    assert "answer" in data and isinstance(data["answer"], str)
    assert data.get("answer_source") in ("fallback", "huggingface")
