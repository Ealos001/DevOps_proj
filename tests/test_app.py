import unittest
import json
import io
from unittest.mock import patch, MagicMock
import os
import importlib.util

# Mock del modello prima di importare l'app
with patch('builtins.open'), patch('pickle.load') as mock_pickle:
    mock_model = MagicMock()
    mock_model.predict.return_value = ['positive']
    mock_model.predict_proba.return_value = [[0.1, 0.9]]
    mock_model.__class__.__name__ = 'MockModel'
    mock_pickle.return_value = mock_model

    # Importa direttamente app.py dalla root del progetto
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    spec = importlib.util.spec_from_file_location("app", app_path)
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    app = app_module.app


class TestSentimentApp(unittest.TestCase):

    def setUp(self):
        """Setup per ogni test"""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        """Test della route principale"""
        with patch('app.render_template') as mock_render:
            mock_render.return_value = 'index page'
            response = self.app.get('/')
            self.assertEqual(response.status_code, 200)
            mock_render.assert_called_once_with('index.html')

    def test_health_route(self):
        """Test dell'endpoint di health check"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('model_loaded', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['status'], 'healthy')

    def test_predict_success(self):
        """Test predizione con testo valido"""
        test_data = {'review': 'This movie is great!'}
        response = self.app.post('/predict',
                                 json=test_data,
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('sentiment', data)
        self.assertIn('confidence', data)
        self.assertIn('review', data)

    def test_predict_empty_text(self):
        """Test predizione con testo vuoto"""
        test_data = {'review': ''}
        response = self.app.post('/predict',
                                 json=test_data,
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_predict_no_data(self):
        """Test predizione senza dati"""
        response = self.app.post('/predict',
                                 json={},
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_predict_file_success(self):
        """Test predizione con file valido"""
        test_file_content = "Great movie!\nTerrible film!\nOkay story."

        data = {
            'file': (io.BytesIO(test_file_content.encode()), 'test.txt')
        }

        response = self.app.post('/predict-file',
                                 data=data,
                                 content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('total_processed', result)
        self.assertIn('results', result)
        self.assertGreater(result['total_processed'], 0)

    def test_predict_file_no_file(self):
        """Test predizione senza file"""
        response = self.app.post('/predict-file')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_metrics_endpoint(self):
        """Test dell'endpoint delle metriche Prometheus"""
        response = self.app.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/plain', response.content_type)

    @patch('app.predict_sentiment')
    def test_predict_internal_error(self, mock_predict):
        """Test gestione errori interni"""
        mock_predict.side_effect = Exception("Model error")

        test_data = {'review': 'Test text'}
        response = self.app.post('/predict',
                                 json=test_data,
                                 content_type='application/json')

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == '__main__':
    # Esegue tutti i test
    unittest.main(verbosity=2)
