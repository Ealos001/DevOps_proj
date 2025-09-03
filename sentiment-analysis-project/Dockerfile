# Usa un'immagine Python leggera
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file dei requirements
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY app.py .
COPY test_app.py .
COPY sentimentanalysismodel.pkl .

# Espone la porta 5000
EXPOSE 5000

# Comando per avviare l'applicazione
CMD ["python", "app.py"]