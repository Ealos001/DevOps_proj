from flask import Flask, request, jsonify, render_template
import pickle
import os
import time
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import requests
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('sentiment_requests_total', 'Total sentiment analysis requests')
REQUEST_LATENCY = Histogram('sentiment_request_duration_seconds', 'Request latency')
ERROR_COUNT = Counter('sentiment_errors_total', 'Total errors in sentiment analysis')
MODEL_CONFIDENCE = Gauge('sentiment_model_confidence', 'Model confidence score')

# Load sentiment model
MODEL_PATH = 'sentimentanalysismodel.pkl'
model = None

def load_model():
    """Load the sentiment analysis model"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            logger.info("Model loaded successfully")
        else:
            logger.warning(f"Model file {MODEL_PATH} not found. Download it first.")
            model = None
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        model = None

def predict_sentiment(text):
    """Predict sentiment for given text"""
    if model is None:
        raise ValueError("Model not loaded")
    
    try:
        # Assuming the model returns prediction and confidence
        prediction = model.predict([text])
        
        # Mock confidence calculation (adapt based on actual model)
        confidence = 0.85  # Replace with actual confidence if available
        
        # Map numerical predictions to sentiment labels
        sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
        sentiment = sentiment_map.get(prediction[0], 'unknown')
        
        return sentiment, confidence
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict sentiment for a single review"""
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    try:
        data = request.get_json()
        if not data or 'review' not in data:
            ERROR_COUNT.inc()
            return jsonify({'error': 'Review text is required'}), 400
        
        review_text = data['review']
        if not review_text.strip():
            ERROR_COUNT.inc()
            return jsonify({'error': 'Review text cannot be empty'}), 400
        
        sentiment, confidence = predict_sentiment(review_text)
        MODEL_CONFIDENCE.set(confidence)
        
        response = {
            'sentiment': sentiment,
            'confidence': confidence,
            'review': review_text[:100] + '...' if len(review_text) > 100 else review_text
        }
        
        REQUEST_LATENCY.observe(time.time() - start_time)
        return jsonify(response)
        
    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/predict-file', methods=['POST'])
def predict_file():
    """Predict sentiment for reviews from uploaded file"""
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    try:
        if 'file' not in request.files:
            ERROR_COUNT.inc()
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            ERROR_COUNT.inc()
            return jsonify({'error': 'No file selected'}), 400
        
        # Save and process file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        results = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        sentiment, confidence = predict_sentiment(line)
                        results.append({
                            'line': i,
                            'review': line[:50] + '...' if len(line) > 50 else line,
                            'sentiment': sentiment,
                            'confidence': confidence
                        })
                        MODEL_CONFIDENCE.set(confidence)
                    except Exception as e:
                        results.append({
                            'line': i,
                            'review': line[:50] + '...' if len(line) > 50 else line,
                            'error': str(e)
                        })
        
        # Clean up uploaded file
        os.remove(filepath)
        
        REQUEST_LATENCY.observe(time.time() - start_time)
        return jsonify({'results': results, 'total_processed': len(results)})
        
    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"File processing error: {str(e)}")
        return jsonify({'error': 'Error processing file'}), 500

@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': time.time()
    })

if __name__ == '__main__':
    # Load model on startup
    load_model()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=False)