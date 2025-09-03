@echo off
setlocal enabledelayedexpansion

where docker >nul 2>&1
if %errorlevel% neq 0 (
  echo Docker non trovato
  exit /b 1
)

docker compose up -d --build

echo API:       http://localhost:8000
echo Prometheus: http://localhost:9090
echo Grafana:   http://localhost:3000 (admin/admin)
echo Jenkins:   http://localhost:8080


