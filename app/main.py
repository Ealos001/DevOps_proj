import os
import time
import pickle
from typing import List

import psutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, HTMLResponse


MODEL_FILENAME = os.environ.get("MODEL_PATH", os.path.join(os.path.dirname(__file__), "..", "sentimentanalysismodel.pkl"))
MODEL_FILENAME = os.path.abspath(MODEL_FILENAME)


class PredictRequest(BaseModel):
    review: str


class PredictResponse(BaseModel):
    sentiment: str
    confidence: float


REQUEST_LATENCY = Histogram("api_request_latency_seconds", "Request latency", ["endpoint", "method", "status"])
PREDICTION_ERRORS = Counter("api_prediction_errors_total", "Total prediction errors")
REQUEST_COUNTER = Counter("api_requests_total", "Total API requests", ["endpoint", "method", "status"])
CPU_USAGE = Gauge("system_cpu_percent", "System CPU percentage")
MEM_USAGE = Gauge("process_memory_mb", "Process memory usage in MB")


def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found at {path}")
    with open(path, "rb") as f:
        return pickle.load(f)


app = FastAPI(title="Sentiment Analysis API", version="1.0.0")


@app.on_event("startup")
def _startup() -> None:
    global pipeline
    pipeline = load_model(MODEL_FILENAME)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        status_code = getattr(response, "status_code", 500)
        return response
    finally:
        elapsed = time.perf_counter() - start
        endpoint = request.url.path
        method = request.method
        status_label = str(locals().get("status_code", 500))
        REQUEST_LATENCY.labels(endpoint=endpoint, method=method, status=status_label).observe(elapsed)
        REQUEST_COUNTER.labels(endpoint=endpoint, method=method, status=status_label).inc()
        try:
            CPU_USAGE.set(psutil.cpu_percent(interval=None))
            MEM_USAGE.set(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024))
        except Exception:
            pass


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest):
    try:
        # The provided pickle expects a list of strings
        preds: List[str] = pipeline.predict([payload.review])
        # If the pipeline has predict_proba, use it for confidence; otherwise default
        try:
            proba = pipeline.predict_proba([payload.review])
            # Find the probability corresponding to the predicted label
            if hasattr(pipeline, "classes_"):
                label = preds[0]
                idx = list(pipeline.classes_).index(label)
                confidence = float(proba[0][idx])
            else:
                confidence = float(max(proba[0]))
        except Exception:
            confidence = 1.0

        # Normalize label to common sentiments if needed
        label_norm = str(preds[0]).lower()
        return JSONResponse(content={"sentiment": label_norm, "confidence": round(confidence, 4)})
    except Exception as exc:
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}")


@app.get("/metrics")
async def metrics():
    data = generate_latest()  # default registry
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/predict-batch")
async def predict_batch(file: UploadFile = File(...)):
    try:
        content_bytes = await file.read()
        text = content_bytes.decode("utf-8", errors="ignore")
        reviews = [line.strip() for line in text.splitlines() if line.strip()]
        if not reviews:
            return JSONResponse(content={"items": []})

        labels: List[str] = list(pipeline.predict(reviews))
        confidences: List[float] = []
        try:
            proba = pipeline.predict_proba(reviews)
            if hasattr(pipeline, "classes_"):
                for i, label in enumerate(labels):
                    idx = list(pipeline.classes_).index(label)
                    confidences.append(float(proba[i][idx]))
            else:
                for i in range(len(labels)):
                    confidences.append(float(max(proba[i])))
        except Exception:
            confidences = [1.0 for _ in labels]

        items = []
        for review, label, conf in zip(reviews, labels, confidences):
            items.append({"review": review, "sentiment": str(label).lower(), "confidence": round(float(conf), 4)})
        return JSONResponse(content={"items": items})
    except Exception as exc:
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {exc}")


@app.get("/")
async def index() -> HTMLResponse:
    html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sentiment Analyzer</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
      color: #333;
    }

    .container {
      max-width: 1000px;
      margin: 0 auto;
    }

    .header {
      text-align: center;
      margin-bottom: 40px;
      color: white;
    }

    .title {
      font-size: 2.5rem;
      margin-bottom: 10px;
      font-weight: 700;
    }

    .subtitle {
      font-size: 1.1rem;
      opacity: 0.9;
    }

    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 30px;
      margin-bottom: 30px;
    }

    .card {
      background: white;
      border-radius: 15px;
      padding: 30px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.2);
      transition: transform 0.3s ease;
    }

    .card:hover {
      transform: translateY(-5px);
    }

    .card-title {
      font-size: 1.3rem;
      margin-bottom: 20px;
      color: #4a5568;
      display: flex;
      align-items: center;
    }

    .icon {
      width: 24px;
      height: 24px;
      margin-right: 10px;
      opacity: 0.7;
    }

    .textarea {
      width: 100%;
      min-height: 120px;
      border: 2px solid #e2e8f0;
      border-radius: 10px;
      padding: 15px;
      font-size: 14px;
      resize: vertical;
      font-family: inherit;
      transition: border-color 0.3s ease;
    }

    .textarea:focus {
      outline: none;
      border-color: #667eea;
    }

    .btn {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      margin-top: 15px;
      margin-right: 10px;
    }

    .btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    .btn-secondary {
      background: #f7fafc;
      color: #4a5568;
      border: 2px solid #e2e8f0;
    }

    .btn-secondary:hover {
      background: #edf2f7;
    }

    .file-input {
      border: 2px dashed #cbd5e0;
      border-radius: 10px;
      padding: 30px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      position: relative;
    }

    .file-input:hover {
      border-color: #667eea;
      background: #f7fafc;
    }

    .file-input input {
      position: absolute;
      inset: 0;
      opacity: 0;
      cursor: pointer;
    }

    .file-text {
      color: #718096;
      font-size: 14px;
    }

    .result {
      background: #f7fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 20px;
      margin-top: 15px;
      min-height: 60px;
      display: none;
    }

    .result.show {
      display: block;
    }

    .sentiment {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      margin-bottom: 10px;
    }

    .sentiment.positive {
      background: #c6f6d5;
      color: #22543d;
    }

    .sentiment.negative {
      background: #fed7d7;
      color: #742a2a;
    }

    .sentiment.neutral {
      background: #e2e8f0;
      color: #4a5568;
    }

    .confidence {
      font-size: 14px;
      color: #718096;
      margin-bottom: 10px;
    }

    .confidence-bar {
      width: 100%;
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      overflow: hidden;
      margin-bottom: 15px;
    }

    .confidence-fill {
      height: 100%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      transition: width 1s ease;
    }

    .batch-results {
      max-height: 250px;
      overflow-y: auto;
    }

    .batch-item {
      background: white;
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 10px;
      border-left: 4px solid #667eea;
    }

    .review-text {
      font-size: 13px;
      color: #4a5568;
      font-style: italic;
    }

    .loading {
      display: flex;
      align-items: center;
      justify-content: center;
      color: #667eea;
      font-size: 14px;
    }

    .spinner {
      width: 20px;
      height: 20px;
      border: 2px solid #e2e8f0;
      border-top-color: #667eea;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-right: 10px;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error {
      color: #e53e3e;
      background: #fed7d7;
      padding: 10px;
      border-radius: 5px;
      font-size: 14px;
    }

    .footer {
      text-align: center;
      color: white;
      opacity: 0.8;
      font-size: 14px;
    }

    .footer a {
      color: white;
      text-decoration: none;
    }

    @media (max-width: 768px) {
      .grid {
        grid-template-columns: 1fr;
      }
      
      .card {
        padding: 20px;
      }
      
      .title {
        font-size: 2rem;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 class="title">🤖 Sentiment Analyzer</h1>
      <p class="subtitle">Analyze the sentiment of your reviews with AI</p>
    </div>

    <div class="grid">
      <!-- Single Review -->
      <div class="card">
        <h2 class="card-title">
          💬 Single Review
        </h2>
        
        <textarea 
          id="review" 
          class="textarea" 
          placeholder="Enter your review here... (e.g., 'This product is amazing!')"
        ></textarea>
        
        <button id="btnPredict" class="btn">Analyze</button>
        <a href="/docs" target="_blank" class="btn btn-secondary">API Docs</a>
        
        <div id="singleResult" class="result"></div>
      </div>

      <!-- Batch Upload -->
      <div class="card">
        <h2 class="card-title">
          📁 Batch Analysis
        </h2>
        
        <div class="file-input">
          <input type="file" id="fileReviews" accept=".txt" />
          <div class="file-text">
            📤 Click to upload .txt file<br>
            <small>(one review per line)</small>
          </div>
        </div>
        
        <button id="btnBatch" class="btn">Process File</button>
        
        <div id="batchResult" class="result"></div>
      </div>
    </div>

    <div class="footer">
      <p>Made with ❤️ for DevOps practice • <a href="/metrics">View Metrics</a></p>
    </div>
  </div>

  <script>
    const btnPredict = document.getElementById('btnPredict');
    const btnBatch = document.getElementById('btnBatch');
    const reviewEl = document.getElementById('review');
    const singleResult = document.getElementById('singleResult');
    const fileEl = document.getElementById('fileReviews');
    const batchResult = document.getElementById('batchResult');

    function getSentimentClass(sentiment) {
      return sentiment.toLowerCase();
    }

    function showLoading(element, text = 'Processing...') {
      element.innerHTML = `
        <div class="loading">
          <div class="spinner"></div>
          ${text}
        </div>
      `;
      element.classList.add('show');
    }

    function showError(element, message) {
      element.innerHTML = `<div class="error">❌ Error: ${message}</div>`;
      element.classList.add('show');
    }

    // Single prediction
    btnPredict.addEventListener('click', async () => {
      const review = reviewEl.value.trim();
      if (!review) {
        showError(singleResult, 'Please enter a review to analyze.');
        return;
      }

      btnPredict.disabled = true;
      showLoading(singleResult, 'Analyzing...');

      try {
        const res = await fetch('/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ review })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || res.statusText);

        const confidencePercent = Math.round(data.confidence * 100);
        
        singleResult.innerHTML = `
          <div class="sentiment ${getSentimentClass(data.sentiment)}">
            ${data.sentiment.toUpperCase()}
          </div>
          <div class="confidence">Confidence: ${confidencePercent}%</div>
          <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
          </div>
          <div class="review-text">"${review}"</div>
        `;

      } catch (e) {
        showError(singleResult, e.message);
      } finally {
        btnPredict.disabled = false;
      }
    });

    // Batch prediction
    btnBatch.addEventListener('click', async () => {
      const file = fileEl.files[0];
      if (!file) {
        showError(batchResult, 'Please select a .txt file.');
        return;
      }

      btnBatch.disabled = true;
      showLoading(batchResult, 'Processing file...');

      try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch('/predict-batch', {
          method: 'POST',
          body: formData
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || res.statusText);

        if (!data.items || data.items.length === 0) {
          batchResult.innerHTML = '<div>No reviews found in file.</div>';
          return;
        }

        const items = data.items.map(item => `
          <div class="batch-item">
            <div class="sentiment ${getSentimentClass(item.sentiment)}">
              ${item.sentiment.toUpperCase()}
            </div>
            <div class="confidence">Confidence: ${Math.round(item.confidence * 100)}%</div>
            <div class="review-text">"${item.review}"</div>
          </div>
        `).join('');

        batchResult.innerHTML = `
          <div style="margin-bottom: 15px; font-weight: 600;">
            📊 Processed ${data.items.length} reviews
          </div>
          <div class="batch-results">${items}</div>
        `;

      } catch (e) {
        showError(batchResult, e.message);
      } finally {
        btnBatch.disabled = false;
      }
    });

    // File input change
    fileEl.addEventListener('change', (e) => {
      const fileName = e.target.files[0]?.name;
      if (fileName) {
        document.querySelector('.file-text').innerHTML = `
          📄 ${fileName}<br>
          <small>Ready to process</small>
        `;
      }
    });
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=False)