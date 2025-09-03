import pytest
import json
from app import app, load_model

@pytest.fixture
def client():
    """Fixture per il client di test"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            load_model()  # Carica il modello per i test
        yield client

def test_health_endpoint(client):
    """Test dell'endpoint di health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['model_loaded'] is True

def test_predict_positive_sentiment(client):
    """Test predizione sentimento positivo"""
    response = client.post('/predict', 
                          json={'review': 'This product is amazing! I love it.'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'sentiment' in data
    assert 'confidence' in data
    assert isinstance(data['confidence'], float)
    assert 0 <= data['confidence'] <= 1

def test_predict_negative_sentiment(client):
    """Test predizione sentimento negativo"""
    response = client.post('/predict', 
                          json={'review': 'This product is terrible. I hate it.'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'sentiment' in data
    assert 'confidence' in data

def test_predict_missing_review(client):
    """Test con review mancante"""
    response = client.post('/predict', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_predict_empty_review(client):
    """Test con review vuota"""
    response = client.post('/predict', json={'review': ''})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_metrics_endpoint(client):
    """Test dell'endpoint delle metriche"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'sentiment_requests_total' in response.data.decode()

def test_home_page(client):
    """Test della pagina principale"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Sentiment Analysis' in response.data