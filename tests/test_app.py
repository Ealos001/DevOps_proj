#!/usr/bin/env python3
"""
Unit tests for the sentiment analysis application
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, predict_sentiment

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_model():
    """Mock the sentiment analysis model"""
    with patch('app.model') as mock:
        mock.predict.return_value = [2]  # Positive sentiment by default
        mock.predict_proba.return_value = [[0.1, 0.2, 0.7]]
        yield mock

class TestAppEndpoints:
    """Test class for application endpoints"""
    
    def test_index_route(self, client):
        """Test the index route returns HTML page"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Sentiment Analysis Dashboard' in response.data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert data['status'] == 'healthy'
    
    def test_metrics_endpoint(self, client):
        """Test the Prometheus metrics endpoint"""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')

class TestPredictEndpoint:
    """Test class for prediction endpoints"""
    
    def test_predict_valid_request(self, client, mock_model):
        """Test prediction with valid request"""
        test_data = {"review": "This product is amazing!"}
        
        response = client.post('/predict',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'sentiment' in data
        assert 'confidence' in data
        assert 'review' in data
        assert data['sentiment'] in ['positive', 'negative', 'neutral']
        assert 0 <= data['confidence'] <= 1
    
    def test_predict_missing_review(self, client):
        """Test prediction with missing review field"""
        test_data = {}
        
        response = client.post('/predict',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_empty_review(self, client):
        """Test prediction with empty review"""
        test_data = {"review": "   "}
        
        response = client.post('/predict',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_invalid_json(self, client):
        """Test prediction with invalid JSON"""
        response = client.post('/predict',
                               data="invalid json",
                               content_type='application/json')
        
        assert response.status_code == 400

class TestFileUpload:
    """Test class for file upload functionality"""
    
    def test_predict_file_valid(self, client, mock_model):
        """Test batch prediction with valid file"""
        test_content = "This product is great!\nI hate this item.\n"
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as f:
            f.write(test_content)
            temp_file_path = f.name
        
        with open(temp_file_path, 'rb') as f:
            response = client.post('/predict-file',
                                   data={'file': (f, 'test_reviews.txt')},
                                   content_type='multipart/form-data')
        
        os.unlink(temp_file_path)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'results' in data
        assert 'total_processed' in data
        assert len(data['results']) == 2
    
    def test_predict_file_no_file(self, client):
        """Test batch prediction with no file uploaded"""
        response = client.post('/predict-file',
                               data={},
                               content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

class TestSentimentPrediction:
    """Test class for sentiment prediction logic"""
    
    @patch('app.model')
    def test_predict_sentiment_function(self, mock_model):
        """Test the predict_sentiment function"""
        mock_model.predict.return_value = [2]  # Positive sentiment
        mock_model.predict_proba.return_value = [[0.1, 0.2, 0.7]]
        
        sentiment, confidence = predict_sentiment("Great product!")
        
        assert sentiment == 'positive'
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
        mock_model.predict.assert_called_once_with(["Great product!"])
    
    def test_predict_sentiment_no_model(self):
        """Test prediction when model is not loaded"""
        with patch('app.model', None):
            with pytest.raises(ValueError, match="Model not loaded"):
                predict_sentiment("Test review")

if __name__ == '__main__':
    pytest.main([__file__])
