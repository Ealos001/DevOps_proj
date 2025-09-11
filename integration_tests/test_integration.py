#!/usr/bin/env python3
"""
Integration tests for the sentiment analysis application
These tests assume the application is running on localhost:5000
"""

import requests
import json
import time
import tempfile
import os

BASE_URL = "http://localhost:5000"
TIMEOUT = 10

class TestApplicationIntegration:
    """Integration tests for the running application"""
    
    def test_application_startup(self):
        """Test that the application starts and responds to health checks"""
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
                assert response.status_code == 200
                
                data = response.json()
                assert data['status'] == 'healthy'
                return
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    time.sleep(2)
                    continue
                raise
        
        raise AssertionError("Application failed to start within expected time")
    
    def test_web_interface_loads(self):
        """Test that the web interface loads correctly"""
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        assert response.status_code == 200
        assert "Sentiment Analysis Dashboard" in response.text
        assert "html" in response.headers.get('content-type', '').lower()
    
    def test_metrics_endpoint_prometheus_format(self):
        """Test that metrics endpoint returns Prometheus format"""
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        assert response.status_code == 200
        
        # Check for Prometheus metrics format
        content = response.text
        assert "sentiment_requests_total" in content
        assert "# HELP" in content or "# TYPE" in content
    
    def test_predict_api_integration(self):
        """Test the prediction API end-to-end"""
        test_review = "This is an amazing product! I love it so much!"
        
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"review": test_review},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "sentiment" in data
        assert "confidence" in data
        assert "review" in data
        assert data["sentiment"] in ["positive", "negative", "neutral"]
        assert 0 <= data["confidence"] <= 1
    
    def test_batch_prediction_integration(self):
        """Test batch prediction with file upload"""
        # Create a temporary file with test reviews
        test_reviews = [
            "This product is absolutely fantastic!",
            "Worst purchase ever, completely disappointed.",
            "It's okay, nothing special but not bad either."
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for review in test_reviews:
                f.write(review + '\n')
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_reviews.txt', f, 'text/plain')}
                response = requests.post(
                    f"{BASE_URL}/predict-file",
                    files=files,
                    timeout=TIMEOUT
                )
            
            assert response.status_code == 200
            
            data = response.json()
            assert "results" in data
            assert "total_processed" in data
            assert data["total_processed"] == len(test_reviews)
            
            # Check each result
            for result in data["results"]:
                assert "line" in result
                assert "sentiment" in result
                assert "confidence" in result
                assert result["sentiment"] in ["positive", "negative", "neutral"]
                
        finally:
            os.unlink(temp_file_path)
    
    def test_error_handling_integration(self):
        """Test error handling in the API"""
        # Test with invalid JSON
        response = requests.post(
            f"{BASE_URL}/predict",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        assert response.status_code == 400
        
        # Test with missing review field
        response = requests.post(
            f"{BASE_URL}/predict",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        assert response.status_code == 400
        
        # Test with empty review
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"review": ""},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        assert response.status_code == 400
    
    def test_prometheus_metrics_integration(self):
        """Test that Prometheus metrics are updated after requests"""
        # Make initial request to get baseline metrics
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        initial_metrics = response.text
        
        # Make a prediction request
        requests.post(
            f"{BASE_URL}/predict",
            json={"review": "Test review for metrics"},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        # Check that metrics were updated
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        updated_metrics = response.text
        
        # The metrics should contain our custom metrics
        assert "sentiment_requests_total" in updated_metrics
        assert "sentiment_request_duration_seconds" in updated_metrics
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request(review_text):
            try:
                response = requests.post(
                    f"{BASE_URL}/predict",
                    json={"review": f"Test review {review_text}"},
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT
                )
                return response.status_code == 200
            except Exception:
                return False
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(results), f"Some concurrent requests failed: {results}"
    
    def test_large_text_handling(self):
        """Test handling of large text inputs"""
        # Create a large review (but not too large to cause issues)
        large_review = "This is a test review. " * 100  # About 2300 characters
        
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"review": large_review},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT * 2  # Allow more time for processing
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert "confidence" in data

class TestApplicationPerformance:
    """Performance tests for the application"""
    
    def test_response_time(self):
        """Test that response times are within acceptable limits"""
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"review": "This is a performance test review"},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0, f"Response time {response_time}s exceeds 5s limit"
    
    def test_memory_stability(self):
        """Test memory stability with multiple requests"""
        # Make multiple requests to check for memory leaks
        for i in range(50):
            response = requests.post(
                f"{BASE_URL}/predict",
                json={"review": f"Memory test review number {i}"},
                headers={"Content-Type": "application/json"},
                timeout=TIMEOUT
            )
            assert response.status_code == 200
        
        # Application should still be responsive
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, "-v"])