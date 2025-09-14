# Sentiment Analysis DevOps Project

## Descrizione del progetto
Questo progetto implementa un sistema completo di **Sentiment Analysis** per recensioni di prodotti, pensato per piattaforme e-commerce. L'obiettivo è analizzare automaticamente le recensioni in lingua inglese e classificare il sentimento come **positivo**, **negativo** o **neutro**, garantendo scalabilità, affidabilità e monitoraggio continuo.

Il progetto integra:
- **Modello ML pre-addestrato** (`sentimentanalysismodel.pkl`)
- **API REST** con Flask per predizioni (`/predict`) e metriche (`/metrics`, `/health`)
- **CI/CD** con Jenkins per build, test e deploy automatico
- **Monitoraggio** con Prometheus e dashboard Grafana
- **Alerting** su errori, latenza, risorse e confidence del modello

---

## Repository GitHub
- Repository: [https://github.com/Ealos001/DevOps_proj](https://github.com/Ealos001/DevOps_proj)  
- Branch principale per test e sviluppo: `develop`  
- Branch per produzione: `main`

**Regole dei branch:**
- `develop`: test e sviluppo; tutte le modifiche devono essere provate qui prima del merge.  
- `main`: ambiente di produzione; deploy effettuato solo dopo approvazione manuale.

---

## Struttura del progetto
sentiment-analysis-devops/
├── app.py # Flask app con API REST
├── requirements.txt # Dipendenze Python
├── sentimentanalysismodel.pkl # Modello ML
├── Dockerfile # Docker immagine app
├── docker-compose.yml # Multi-container stack
├── Jenkinsfile # Pipeline CI/CD
├── pytest.ini # Configurazione test
├── templates/ # Template HTML
├── tests/ # Unit test
├── monitoring/ # Prometheus e Grafana
│ ├── prometheus.yml
│ ├── alert_rules.yml
│ └── grafana/
│ ├── provisioning/ # Datasource e dashboards YAML
│ └── dashboards/ # Dashboard JSON
└── README.md


---

## Primo avvio e configurazione

### 1. Clonare repository e selezionare branch
```bash
git clone https://github.com/Ealos001/DevOps_proj.git
cd DevOps_proj
git checkout develop
```
### 2. Avviare servizi con Docker Compose

```bash
docker-compose up -d
```

Servizi inclusi:

  - Flask App: http://localhost:5000

  - Prometheus: http://localhost:9090

  - Grafana: http://localhost:3000 (user: admin, password: admin123)

  - Jenkins: http://localhost:8080

Al primo avvio, Grafana importerà automaticamente datasource e dashboard.

### 3. Confugirazione Jenkins

Aprire Jenkins e completare l'installazione guidata.

Creare una pipeline:

Nome: Sentiment-Analysis-Pipeline

Tipo: Pipeline

Definizione: Pipeline script from SCM

SCM: Git

Repository URL: https://github.com/Ealos001/DevOps_proj.git

Branch: develop

La pipeline esegue:

Build immagine Docker

Test automatici (pytest)

Deploy su staging (develop) o produzione (main)

### 4. Configurazione Prometheus

Raccoglie metriche da:
  - App Flask (sentiment-app:5000/metrics)
  - Node Exporter per CPU e memoria

Alerting confugirato in monitorin/alter_rules.yml

### 5. Configurazione Grafana 

Datasource Prometheus e dashboard già definiti in monitoring/grafana/provisioning/ e monitoring/grafana/dashboards/

Dashboard pronta con pannelli per:

  - Request rate
  - Response time
  - Error rate
  - Model confidence
  - CPU e memoria

---

### API REST

POST /predict
{
  "review": "This product is amazing! I love it."
}

Risposta 
{
  "review": "This product is amazing! I love it.",
  "sentiment": "positive",
  "confidence": 0.95
}

POST /predict-file

Carica un file .txt con recensioni riga per riga.

Restituisce JSON con sentiment e confidence per ogni riga.

GET /metrics

Espone metriche per Prometheus (request count, latency, error count, CPU, memoria, confidence modello).

GET /health

Stato di salute del servizio e del modello (healthy, model_loaded).

---

## Test
si utilizza pytest ma vengono fatti direttamente i Pipeline Jenkins

I riusltati verrano poi collezionati in test-result.xml

## Benefici aziendali

Automazione: pipeline CI/CD su commit nel branch develop.

Monitoraggio proattivo: alert su errori, latenza, utilizzo risorse e confidence modello.

Decisioni basate sui dati: insight immediati sulle recensioni tramite API e dashboard.

# Flusso Progetto

Commit su GitHub (develop)
          |
          v
     Jenkins Pipeline
   --------------------
   | Checkout codice  |
   | Build Docker     |
   | Run pytest       |
   | Deploy staging   |
   --------------------
          |
          v
   Docker Compose Stack
   --------------------------
   | Flask App              |
   | Prometheus             |
   | Node Exporter          |
   | Grafana                |
   --------------------------
          |
          v
    Dashboard & Alerting
  --------------------------
  | Request rate           |
  | Response time          |
  | Error rate             |
  | CPU / Memory usage     |
  | Model confidence       |
  --------------------------

# Note importanti

Usare il **Branch develop** per test, **Branch main** per produzione

Grafana aggiorna automaticamente dashboard e datasource al primo avvio.

Modifiche a dashboard Grafana devono aggiornare i JSON in monitoring/grafana/dashboards/.