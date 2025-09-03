# Sentiment Analysis API

API di analisi del sentiment basata su FastAPI, con metriche Prometheus, dashboard Grafana e pipeline Jenkins. Il servizio carica un modello scikit-learn serializzato (`sentimentanalysismodel.pkl`) e fornisce endpoint per predizioni singole e batch, oltre a un frontend minimale per test manuali.

## Requisiti
- **Docker** e **Docker Compose** (consigliato)
- Opzionale: **Python 3.11** per esecuzione locale senza container

## Architettura e componenti
- **API (FastAPI)**: espone `/predict`, `/predict-batch`, `/metrics`, `/health` e interfaccia web su `/`.
- **Prometheus**: raccoglie metriche esposte da `/metrics` dell'API.
- **Grafana**: provisioning automatico di datasource Prometheus e dashboard "Sentiment API Overview".
- **Jenkins**: pipeline CI/CD per build, test, integrazione e deploy via Docker Compose.

Struttura principali file/dir:
- `app/main.py`: applicazione FastAPI, caricamento modello, endpoint, metriche.
- `sentimentanalysismodel.pkl`: modello ML serializzato caricato all'avvio.
- `Dockerfile`: build immagine dell'API.
- `docker-compose.yml`: orchestrazione di API, Prometheus, Grafana, Jenkins.
- `monitoring/prometheus/prometheus.yml`: configurazione scrape.
- `monitoring/grafana/provisioning/...`: datasource e dashboard pre-caricati.
- `Jenkinsfile`: pipeline Jenkins declarativa.

## Struttura del progetto
```text
devopsprj/
  app/
    __init__.py
    main.py
  monitoring/
    grafana/
      provisioning/
        dashboards/
          dashboard.yml
          json/
            sentiment_api_overview.json
        datasources/
          datasource.yml
    prometheus/
      prometheus.yml
  tests/
    test_api.py
  Dockerfile
  docker-compose.yml
  Jenkinsfile
  README.md
  requirements.txt
  sentimentanalysismodel.pkl
  start.bat
  start.sh
```

## Configurazione
- **MODEL_PATH**: percorso del file modello per l'API.
  - Default runtime: se non specificato, l'app cerca `../sentimentanalysismodel.pkl` rispetto a `app/main.py`.
  - In Docker Compose è impostato a `/app/sentimentanalysismodel.pkl`.
- **PORT**: porta su cui parte FastAPI (default `8000`). In Docker è mappata su `8000:8000`.
- **Grafana**: credenziali admin via env `GF_SECURITY_ADMIN_USER`/`GF_SECURITY_ADMIN_PASSWORD` (default `admin/admin`).
- **Prometheus**: legge la configurazione da `monitoring/prometheus/prometheus.yml` e scrapa l'API.
- **Jenkins**: volume persistente `jenkins_home` per lo stato.

Per modificare le porte pubbliche, cambia i binding in `docker-compose.yml` (es. `"8081:8080"` per Jenkins).

## Avvio con Docker Compose (consigliato)
1) Assicurati che `sentimentanalysismodel.pkl` sia nella root del progetto.
2) Build e avvio:
```bash
docker compose up -d --build
```
Servizi esposti:
- API: `http://localhost:8000`
- Documentazione OpenAPI: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (credenziali: admin/admin)
- Jenkins: `http://localhost:8080`

Per verificare lo stato dell'API:
```bash
curl -s http://localhost:8000/health
```

Per fermare tutto:
```bash
docker compose down
```

## Avvio locale senza Docker
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Imposta `MODEL_PATH` se il modello non è in root:
```bash
# Windows PowerShell
$env:MODEL_PATH="C:\\path\\to\\sentimentanalysismodel.pkl"; uvicorn app.main:app --host 0.0.0.0 --port 8000
# Linux/macOS
MODEL_PATH="/path/to/sentimentanalysismodel.pkl" uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Script di avvio rapidi:
- Linux/macOS: `./start.sh`
- Windows: `start.bat`

## API Endpoints
- **GET `/`**: pagina HTML minimale per test manuale.
- **GET `/docs`**: UI Swagger/OpenAPI.
- **GET `/health`**: stato servizio (`{"status":"ok"}`).
- **POST `/predict`**: predizione singola.
  - Request:
    ```json
    { "review": "This product is amazing!" }
    ```
  - Response:
    ```json
    { "sentiment": "positive", "confidence": 0.95 }
    ```
- **POST `/predict-batch`**: upload file `.txt` (una riga = una review). Restituisce lista di predizioni.
- **GET `/metrics`**: esporta metriche Prometheus in formato testo.

Esempi con curl:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"review":"Absolutely fantastic experience!"}'

curl -X POST http://localhost:8000/predict-batch \
  -F file=@./reviews.txt
```

## Metriche esposte
- `api_request_latency_seconds` (Histogram): latenza per endpoint/metodo/stato.
- `api_requests_total` (Counter): numero richieste per endpoint/metodo/stato.
- `api_prediction_errors_total` (Counter): errori di predizione.
- `system_cpu_percent` (Gauge): CPU di sistema percentuale.
- `process_memory_mb` (Gauge): memoria processo in MB.

Prometheus è configurato tramite `monitoring/prometheus/prometheus.yml`. Grafana viene provisionato con datasource e dashboard in `monitoring/grafana/provisioning/` e mostrerà la dashboard "Sentiment API Overview".

## CI/CD con Jenkins
La pipeline (`Jenkinsfile`) esegue:
1. Checkout del repository
2. Setup Python e installazione dipendenze
3. Test (unit/integration base)
4. Build immagine Docker dell'API
5. Test di integrazione avviando l'API via Docker Compose
6. Deploy completo via `docker compose up -d`

Prerequisiti agent Jenkins:
- Docker e Docker Compose installati
- Accesso al socket Docker (montato come volume in Compose)

## Test
```bash
pip install -r requirements.txt
pip install pytest
pytest -q
```

## Personalizzazione del modello
- Sostituisci `sentimentanalysismodel.pkl` con il tuo modello scikit-learn compatibile.
- Il codice invoca `pipeline.predict([...])` e, se disponibile, `pipeline.predict_proba([...])`. Se il tuo modello espone `classes_`, la confidenza verrà allineata alla classe predetta.
- In Docker, il modello viene copiato in immagine e referenziato tramite `MODEL_PATH=/app/sentimentanalysismodel.pkl`.

## Troubleshooting
- "Model file not found": verifica il percorso e la variabile `MODEL_PATH`.
- L'endpoint `/predict` risponde 500: controlla i log dell'API e il formato dell'input.
- Metriche non visibili in Grafana: verifica che Prometheus stia scrappando l'API e che la datasource in Grafana sia "UP".
- Porta occupata: modifica i binding porte in `docker-compose.yml`.

## Licenza
Uso didattico/dimostrativo. Adatta secondo le esigenze del tuo progetto.

