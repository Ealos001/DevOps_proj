import os
import json
import pytest
from fastapi.testclient import TestClient

os.environ["MODEL_PATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sentimentanalysismodel.pkl"))

from app.main import app  # noqa: E402


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_basic():
    payload = {"review": "This product is amazing!"}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "sentiment" in data and "confidence" in data


