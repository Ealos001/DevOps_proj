# Usa l'ultima versione minima e aggiorna i pacchetti di sistema
FROM python:3.11.9-slim-bullseye

WORKDIR /app

# Aggiorna i pacchetti di sistema e installa dipendenze
RUN apt-get update && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]