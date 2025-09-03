#!/usr/bin/env bash
set -euo pipefail

command -v docker >/dev/null 2>&1 || { echo "Docker non trovato"; exit 1; }

docker compose up -d --build
echo "API:       http://localhost:8000"
echo "Prometheus: http://localhost:9090"
echo "Grafana:   http://localhost:3000 (admin/admin)"
echo "Jenkins:   http://localhost:8080"


