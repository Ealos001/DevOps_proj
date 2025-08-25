# Sentiment Analysis Deploy con Flask, Jenkins, Prometheus, Grafana

## Struttura del progetto
- `model_api/` → API Flask con modello pickle e HTML semplice
- `Jenkinsfile` → pipeline CI/CD
- `prometheus/` → config Prometheus
- `docker-compose.yml` → avvio di API, Jenkins, Prometheus e Grafana

## Requisiti
- Installare [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/).

## Avvio rapido
1. Clonare il repo
2. Scaricare il modello nella cartella `model_api`:
   ```bash
   wget https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl -O model_api/sentimentanalysismodel.pkl
