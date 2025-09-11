# 📘 Guida Completa (README2)

Questo documento spiega in modo dettagliato come funziona l’intero progetto: architettura, requisiti, setup locale, pipeline Jenkins (CI/CD), monitoraggio con Prometheus/Grafana, policy di branch/deploy, e flusso di lavoro end‑to‑end.

---

## 1) Obiettivo del progetto

- Deploy e monitoraggio di un modello di Sentiment Analysis per recensioni in inglese.
- API REST con Flask: `POST /predict`, `GET /metrics`, `GET /health`, `POST /predict-file`.
- CI/CD con Jenkins: test automatici, build immagine, deploy completo via Docker Compose.
- Monitoraggio: Prometheus (metriche e alert) + Grafana (dashboard).

---

## 2) Architettura e componenti

Servizi principali (vedi `docker-compose.yml`):
- `sentiment-app`: applicazione Flask (serve `app.py`), carica il modello `sentimentanalysismodel.pkl`.
- `prometheus`: esegue scraping su app (`/metrics`) e su `node-exporter`, carica regole di alert.
- `grafana`: provisioning automatico della datasource Prometheus e delle dashboard.
- `node-exporter`: metriche di sistema host/container.

File chiave:
- API: `app.py`, template UI: `templates/index.html`.
- Compose: `docker-compose.yml`, Docker image: `Dockerfile`.
- Prometheus: `monitoring/prometheus.yml`, regole: `monitoring/alert_rules.yml`.
- Grafana provisioning: `monitoring/grafana/provisioning/datasources/prometheus.yml`, `monitoring/grafana/provisioning/dashboards/dashboard.yml`.
- Dashboard JSON: `monitoring/grafana/dashboards/sentiment-analysis-dashboard.json`.
- Test: unit `tests/test_app.py`, integrazione `integration_tests/test_integration.py`.
- Pipeline: `Jenkinsfile`.

### Struttura del progetto
```
devopsprj/
├─ app.py
├─ Dockerfile
├─ docker-compose.yml
├─ Jenkinsfile
├─ README.md
├─ README2.md
├─ requirements.txt
├─ pytest.ini
├─ sentimentanalysismodel.pkl             # (scaricato/commitato)
├─ templates/
│  └─ index.html
├─ tests/
│  └─ test_app.py
├─ integration_tests/
│  └─ test_integration.py
├─ monitoring/
│  ├─ prometheus.yml
│  ├─ alert_rules.yml
│  └─ grafana/
│     ├─ dashboards/
│     │  └─ sentiment-analysis-dashboard.json
│     └─ provisioning/
│        ├─ dashboards/
│        │  └─ dashboard.yml
│        └─ datasources/
│           └─ prometheus.yml
└─ uploads/                              # volume per file batch
```

---

## 3) Requisiti (Agent Jenkins e/o locale)

- Docker Engine + Docker Compose (nuova sintassi `docker compose`).
- Python 3.11+ e pip.
- Git, curl.
- Accesso alla repo Git (credenziali se privata).
- Su macOS/Linux: utente nel gruppo `docker`. Su Windows: Docker Desktop attivo.

---

## 4) Setup locale rapido (facoltativo)

Avvio stack completo:
```
docker compose up -d --build
```

Accesso ai servizi:
- App: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)

Smoke check:
```
curl http://localhost:5000/health
curl http://localhost:5000/metrics
curl http://localhost:9090/-/ready
curl http://localhost:3000/login
```

Nota su Grafana: le modifiche via UI persistono nel volume `grafana_data`. Le dashboard "as code" sono versionate in `monitoring/grafana/dashboards/`.

---

## 5) Jenkins: creare il Job Pipeline (una sola volta)

1. Apri Jenkins → New Item → Pipeline → nome (es. `sentiment-ci`).
2. Pipeline → Definition: "Pipeline script from SCM".
3. SCM: Git → Repository URL: `https://github.com/Ealos001/DevOps_proj.git`.
4. Branch: `*/develop` (staging) e/o `*/main` (produzione), oppure `*/**`.
5. Script Path: `Jenkinsfile`.
6. Salva. Opzionale: configura webhook GitHub verso `http://<jenkins>/github-webhook/`.

Prerequisiti sull’agent Jenkins:
- Docker/Compose nel PATH; Python 3.x; Git; curl.
- Permessi Docker (senza sudo) o Docker Desktop avviato su Windows.

---

## 6) Pipeline (Jenkinsfile) – cosa fa, step by step

1. Checkout: scarica la repo.
2. Setup Environment: crea `venv`, installa `requirements.txt`.
3. Verify/Download Model: se `sentimentanalysismodel.pkl` manca, lo scarica dal link ufficiale.
4. Unit Tests: esegue `pytest` su `tests/`; la pipeline fallisce se i test falliscono.
5. Code Quality: `flake8` su `app.py` (non bloccante).
6. Integration Tests: avvia `app.py` temporaneamente, esegue `integration_tests/`.
7. Build Docker Image: build dell’immagine applicativa con `Dockerfile`.
8. Security Scan (placeholder): integrabile con Trivy/Grype.
9. Deploy stack completo via Docker Compose:
   - Branch `develop`: staging automatico.
   - Branch `main`: produzione con conferma manuale.
   - Usa `COMPOSE_PROJECT_NAME` per isolare gli ambienti (`sentiment-analysis-staging`/`-prod`).
10. Smoke Tests: verifica app (`/health`, `/metrics`), Prometheus (`/-/ready`), Grafana (`/login`).
11. Post: cleanup `venv`, archivia test report, messaggi di esito.

Nota: lo stack di deploy è governato da `docker-compose.yml` e comprende app, Prometheus (con regole montate), Grafana (provisioning), Node Exporter.

---

## 7) Politica di branch e deploy

- `develop` → Deploy in staging automatico dopo i test.
- `main` → Deploy in produzione dopo i test e conferma manuale.

Se vuoi evitare rebuild doppio:
- Opzione A: togli `build: .` da `docker-compose.yml` e referenzia `image: sentiment-analysis-app:latest`.
- Opzione B: rimuovi lo stage "Build Docker Image" e delega il build a Compose.
- Default attuale: semplicità > ottimizzazione; il rebuild garantisce coerenza col codice.

---

## 8) Endpoints dell’app (app.py)

- `POST /predict` – Body JSON `{"review": "..."}` → sentiment + confidence.
- `POST /predict-file` – Upload `.txt` (una review per riga) → batch results.
- `GET /metrics` – metriche Prometheus (include custom metrics dell’app).
- `GET /health` – stato istantaneo del servizio.

Metriche custom principali:
- `sentiment_requests_total`, `sentiment_request_duration_seconds`, `sentiment_errors_total`, `sentiment_model_confidence`.

---

## 9) Monitoraggio e alert

Prometheus (`monitoring/prometheus.yml`):
- Scrape di `sentiment-app:5000/metrics`, `node-exporter:9100`, e self.
- Regole di alert montate da `monitoring/alert_rules.yml` in `/etc/prometheus/alert_rules.yml` (vedi `docker-compose.yml`).

Alert inclusi (esempi):
- HighErrorRate, HighResponseTime, ServiceDown, LowModelConfidence, HighCPUUsage, HighMemoryUsage, LowRequestRate.

Grafana:
- Datasource: `monitoring/grafana/provisioning/datasources/prometheus.yml`.
- Dashboards: `monitoring/grafana/dashboards/sentiment-analysis-dashboard.json` + provider `monitoring/grafana/provisioning/dashboards/dashboard.yml`.

Persistenza:
- `grafana_data` (dashboard salvate via UI), `prometheus_data` (TSDB). Evita `docker compose down -v` per non perdere i volumi.

---

## 10) Esecuzione test

Con Jenkins (automatica):
- Unit e integrazione vengono eseguite durante la pipeline.

Locale (facoltativo):
```
# unit
pytest tests -v

# integrazione (app in esecuzione su :5000)
pytest integration_tests -v
```

---

## 11) Sicurezza e buone pratiche

- Contenitore app gira come utente non‑root (`Dockerfile`).
- Input validation sugli endpoint.
- Rate limiting/HTTPS da gestire con reverse proxy in ambienti esterni.
- Integra scanner immagini (es. Trivy) nello stage Security Scan se richiesto.

---

## 12) Troubleshooting

- Docker non parte: avvia Docker Desktop (Windows/Mac) o verifica `systemctl status docker` (Linux).
- Modello mancante: la pipeline lo scarica; localmente usa il comando `curl` nel `README.md`.
- Alert non caricati: verifica il mount `./monitoring/alert_rules.yml:/etc/prometheus/alert_rules.yml` e il path in `prometheus.yml`.
- Perdita configurazioni Grafana: non usare `down -v`; non cambiare `COMPOSE_PROJECT_NAME` per lo stesso ambiente.

---

## 13) Flusso di lavoro end‑to‑end (dal clone al deploy)

1) Sviluppatore clona repo: `git clone https://github.com/Ealos001/DevOps_proj.git`.
2) Admin crea job Jenkins Pipeline from SCM puntando a `Jenkinsfile` (una volta).
3) Sviluppatore fa push su `develop` o `main`.
4) Jenkins esegue pipeline:
   - checkout → venv+deps → verifica/scarica modello → unit test → lint → integrazione → build image → (scan) → deploy con docker compose → smoke tests.
5) Se branch `develop`: deploy in staging automatico. Se `main`: conferma e deploy produzione.
6) Operatori controllano Grafana/Prometheus.
7) In caso di problemi, alert via regole Prometheus (agganciare Alertmanager se necessario).

---

## 14) FAQ rapide

- Devo avviare Docker a mano? No, la pipeline gestisce il deploy. Serve solo che Docker sia disponibile sull’agent.
- Perché a volte ricostruisce due volte? Scelta semplificata per garantire coerenza; puoi ottimizzare come descritto nella sezione Branch/Deploy.
- Dove aggiorno la dashboard? Modifica via UI e poi esporta il JSON in `monitoring/grafana/dashboards/` per versionarlo.

---

## 15) Contatti

Per supporto: apri issue sul repository GitHub o contatta il team DevOps.


