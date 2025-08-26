from flask import Flask, request, jsonify, render_template
import pickle
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Carica modello
model = pickle.load(open("sentimentanalysismodel.pkl", "rb"))

# Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Metriche Prometheus
REQUEST_COUNT = Counter('api_requests_total', 'Numero totale di richieste', ['endpoint', 'method'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'Latenza delle richieste', ['endpoint'])

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint="/predict", method="POST").inc()
    try:
        data = request.get_json() if request.is_json else request.form
        review = data.get("review")
        if not review or not isinstance(review, str):
            return jsonify({"error": "Invalid input"}), 400

        sentiment = model.predict([review])[0]
        # Se il modello restituisce probabilità/confidenza
        try:
            confidence = max(model.predict_proba([review])[0])
        except:
            confidence = 1.0  # fallback se predict_proba non disponibile

        elapsed = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/predict").observe(elapsed)

        return jsonify({"sentiment": sentiment, "confidence": round(float(confidence), 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
