from flask import Flask, request, jsonify, render_template_string
import pickle
import requests
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Metriche Prometheus
REQUEST_COUNT = Counter('sentiment_requests_total', 'Total sentiment analysis requests')
REQUEST_DURATION = Histogram('sentiment_request_duration_seconds', 'Request duration')
ERROR_COUNT = Counter('sentiment_errors_total', 'Total errors')

# Caricamento del modello
model = None

def load_model():
    global model
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'sentimentanalysismodel.pkl')
    
    if not os.path.exists(model_path):
        logger.error(f"File modello non trovato: {model_path}. Assicurati di averlo nella cartella.")
        raise FileNotFoundError(f"{model_path} non trovato")
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info("Modello caricato con successo!")
    except Exception as e:
        logger.error(f"Errore nel caricamento del modello: {e}")
        raise

# UI Template
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Analysis</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
        }
        textarea:focus {
            outline: none;
            border-color: #007bff;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #6c757d;
            cursor: not-allowed;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .result.positive {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .result.negative {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .result.neutral {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        .loading {
            text-align: center;
            color: #666;
        }
        .confidence {
            font-weight: bold;
            margin-top: 10px;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Sentiment Analysis</h1>
        <p style="text-align: center; color: #666; margin-bottom: 30px;">
            Enter a text review and get instant sentiment analysis with confidence score
        </p>
        
        <form id="sentimentForm">
            <div class="form-group">
                <label for="review">Enter your review:</label>
                <textarea id="review" name="review" placeholder="Type your review here..." required></textarea>
            </div>
            <button type="submit" id="submitBtn">Analyze Sentiment</button>
        </form>
        
        <div id="loading" class="loading" style="display: none;">
            <p>🔄 Analyzing sentiment...</p>
        </div>
        
        <div id="result" class="result">
            <h3>Analysis Result:</h3>
            <p><strong>Sentiment:</strong> <span id="sentiment"></span></p>
            <p class="confidence"><strong>Confidence:</strong> <span id="confidence"></span>%</p>
        </div>
        
        <div id="error" class="error">
            <h3>Error:</h3>
            <p id="errorMessage"></p>
        </div>
    </div>

    <script>
        document.getElementById('sentimentForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const review = document.getElementById('review').value.trim();
            if (!review) {
                showError('Please enter a review text.');
                return;
            }
            
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const error = document.getElementById('error');
            
            // Reset UI
            submitBtn.disabled = true;
            loading.style.display = 'block';
            result.style.display = 'none';
            error.style.display = 'none';
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ review: review })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showResult(data);
                } else {
                    showError(data.error || 'An error occurred during analysis.');
                }
            } catch (err) {
                showError('Network error. Please try again.');
            } finally {
                submitBtn.disabled = false;
                loading.style.display = 'none';
            }
        });
        
        function showResult(data) {
            const result = document.getElementById('result');
            const sentiment = document.getElementById('sentiment');
            const confidence = document.getElementById('confidence');
            
            sentiment.textContent = data.sentiment;
            confidence.textContent = (data.confidence * 100).toFixed(1);
            
            // Set result class based on sentiment
            result.className = 'result ' + data.sentiment;
            result.style.display = 'block';
        }
        
        function showError(message) {
            const error = document.getElementById('error');
            const errorMessage = document.getElementById('errorMessage');
            
            errorMessage.textContent = message;
            error.style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Pagina principale con UI"""
    return render_template_string(UI_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint per la predizione del sentimento usando predict_proba"""
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    try:
        if model is None:
            ERROR_COUNT.inc()
            return jsonify({'error': 'Modello non caricato'}), 500

        data = request.json
        if not data or 'review' not in data:
            ERROR_COUNT.inc()
            return jsonify({'error': 'Campo review richiesto'}), 400
        
        review_text = data['review'].strip()
        if not review_text:
            ERROR_COUNT.inc()
            return jsonify({'error': 'Review non può essere vuota'}), 400

        # Probabilità predette dal modello
        proba = model.predict_proba([review_text])[0]  # es: [0.2, 0.8]
        classes = model.classes_  # le classi effettive, es ['negative', 'positive']
        
        # Prendi la classe con probabilità massima
        max_index = proba.argmax()  # posizione della probabilità più alta
        sentiment = classes[max_index].lower()  # classe predetta
        confidence = float(proba[max_index])  # confidenza reale

        REQUEST_DURATION.observe(time.time() - start_time)
        return jsonify({
            'sentiment': sentiment,
            'confidence': confidence
        })
        
    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"Errore nella predizione: {e}")
        return jsonify({'error': 'Errore interno del server'}), 500

@app.route('/metrics')
def metrics():
    """Endpoint per le metriche Prometheus"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

if __name__ == '__main__':
    # Carica il modello all'avvio
    load_model()
    
    # Avvia l'app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
