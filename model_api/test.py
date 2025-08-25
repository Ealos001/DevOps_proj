import json
import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Sentiment Analysis" in res.data

def test_predict_valid_json(client):
    res = client.post("/predict", json={"review": "This product is great!"})
    assert res.status_code == 200
    data = json.loads(res.data)
    assert "sentiment" in data
    assert "confidence" in data

def test_predict_invalid_input(client):
    res = client.post("/predict", json={"wrong_key": "test"})
    assert res.status_code == 400

def test_predict_empty_string(client):
    res = client.post("/predict", json={"review": ""})
    assert res.status_code == 400

def test_metrics(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert b"api_requests_total" in res.data
