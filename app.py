from flask import Flask, request, jsonify, render_template
import pickle
import os
import time
import logging
import psutil
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- Prometheus metrics ----------------
REQUEST_COUNT = Counter('sentiment_requests_total', 'Total sentiment analysis requests')
REQUEST_LATENCY = Histogram('sentiment_request_duration_seconds', 'Request latency')
ERROR_COUNT = Counter('sentiment_errors_total', 'Total errors in sentiment analysis')
MODEL_CONFIDENCE = Gauge('sentiment_model_confidence', 'Model confidence score')
CPU_USAGE = Gauge('app_cpu_usage_percent', 'CPU usage of the app')
MEM_USAGE = Gauge('app_memory_usage_bytes', 'Memory usage of the app')

# ---------------- Load model ----------------
MODEL_PATH = 'sentimentanalysismodel.pkl'
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    logger.info(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

def predict_sentiment(text):
    """Predict sentiment for a single text"""
    if model is None:
        raise ValueError("Model not loaded")
    prediction = model.predict([text])[0]
    confidence = float(max(model.predict_proba([text])[0])) if hasattr(model, 'predict_proba') else 1.0
    MODEL_CONFIDENCE.set(confidence)
    return prediction, confidence

# ---------------- Routes ----------------
@app.before_request
def update_resource_metrics():
    """Update CPU and memory metrics before each request"""
    CPU_USAGE.set(psutil.cpu_percent())
    MEM_USAGE.set(psutil.virtual_memory().used)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    REQUEST_COUNT.inc()

    data = request.get_json()
    if not data or 'review' not in data or not data['review'].strip():
        ERROR_COUNT.inc()
        return jsonify({'error': 'Review text is required'}), 400

    try:
        sentiment, confidence = predict_sentiment(data['review'])
        REQUEST_LATENCY.observe(time.time() - start_time)
        return jsonify({
            'review': data['review'][:100] + '...' if len(data['review']) > 100 else data['review'],
            'sentiment': sentiment,
            'confidence': confidence
        })
    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/predict-file', methods=['POST'])
def predict_file():
    start_time = time.time()
    REQUEST_COUNT.inc()

    if 'file' not in request.files:
        ERROR_COUNT.inc()
        return jsonify({'error': 'File is required'}), 400

    file = request.files['file']
    if file.filename == '':
        ERROR_COUNT.inc()
        return jsonify({'error': 'No selected file'}), 400

    try:
        content = file.read().decode('utf-8').splitlines()
        results = []
        for i, line in enumerate(content, start=1):
            if line.strip():
                try:
                    sentiment, confidence = predict_sentiment(line.strip())
                    results.append({
                        'line': i,
                        'review': line[:100] + '...' if len(line) > 100 else line,
                        'sentiment': sentiment,
                        'confidence': confidence
                    })
                except Exception as e:
                    results.append({
                        'line': i,
                        'review': line,
                        'error': str(e)
                    })

        REQUEST_LATENCY.observe(time.time() - start_time)
        return jsonify({
            'total_processed': len(results),
            'results': results
        })

    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"File prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': time.time()
    })

# ---------------- Main ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
