# Sentiment Analysis Project

A complete sentiment analysis web application with monitoring, containerization, and CI/CD pipeline.

## Features

- 🎭 **Sentiment Analysis**: Real-time sentiment analysis using machine learning
- 📊 **Monitoring**: Prometheus metrics and Grafana dashboards
- 🐳 **Containerization**: Docker and Docker Compose setup
- 🔄 **CI/CD**: Jenkins pipeline for automated deployment
- 🧪 **Testing**: Comprehensive test suite with pytest

## 🚀 First Time Deployment Guide

### Prerequisites

- Docker and Docker Compose installed
- Jenkins server running
- Git repository (GitHub/GitLab) configured

### Step 1: Clone and Setup Repository

```bash
git clone <your-repository-url>
cd sentiment-analysis-project
```

### Step 2: Deploy with Docker Compose

#### Option A: Using Startup Scripts (Recommended)

**For macOS/Linux:**
```bash
./start.sh
```

**For Windows:**
```batch
./start.bat
```

#### Option B: Manual Docker Compose

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Verify all services are running:**
   ```bash
   docker-compose ps
   ```

3. **Check logs if needed:**
   ```bash
   docker-compose logs -f
   ```

### Step 3: Configure Jenkins Pipeline

1. **Create a new Jenkins job:**
   - Go to Jenkins dashboard
   - Click "New Item"
   - Choose "Pipeline" type
   - Name it "sentiment-analysis-pipeline"

2. **Configure the pipeline:**
   - In "Pipeline" section, select "Pipeline script from SCM"
   - Choose "Git" as SCM
   - Enter your repository URL
   - Set branch to `*/main` (or your default branch)
   - Script path: `Jenkinsfile`

3. **Save and run the pipeline:**
   - Click "Save"
   - Click "Build Now" to test

### Step 4: Configure Grafana Data Source

1. **Access Grafana:**
   - Open http://localhost:3000
   - Login with admin/admin123

2. **Add Prometheus as data source:**
   - Go to Configuration → Data Sources
   - Click "Add data source"
   - Select "Prometheus"
   - URL: `http://prometheus:9090`
   - Click "Save & Test"

3. **Import the dashboard:**
   - Go to Dashboards → Import
   - The dashboard should auto-load from provisioning
   - If not, look for "Sentiment Analysis Dashboard"

### Step 5: Verify Everything Works

1. **Test the application:**
   - Web App: http://localhost:5000
   - Try analyzing a review: "This product is amazing!"

2. **Check monitoring:**
   - Prometheus: http://localhost:9090/targets
   - Grafana: http://localhost:3000 (check dashboard)

3. **Test Jenkins pipeline:**
   - Make a small change to the code
   - Commit and push to trigger pipeline
   - Check Jenkins build logs

## Quick Start (After Initial Setup)

### Using Docker Compose

#### Quick Start with Scripts

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```batch
start.bat
```

#### Manual Start

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Web App: http://localhost:5000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin123)

#### Stop Services

**macOS/Linux:**
```bash
./stop.sh
```

**Windows:**
```batch
stop.bat
```

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Run tests:**
   ```bash
   pytest test_app.py -v
   ```

## Project Structure

```
├── app.py                          # Main Flask application
├── test_app.py                     # Test suite
├── sentimentanalysismodel.pkl      # Trained ML model
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
├── docker-compose.yml              # Multi-service setup
├── Jenkinsfile                     # CI/CD pipeline
├── start.sh                        # Startup script (macOS/Linux)
├── start.bat                       # Startup script (Windows)
├── stop.sh                         # Stop script (macOS/Linux)
├── stop.bat                        # Stop script (Windows)
├── prometheus/
│   └── prometheus.yml              # Prometheus configuration
└── grafana/
    └── provisioning/               # Grafana configuration
        ├── datasources/
        └── dashboards/
```

## API Endpoints

- `GET /` - Web interface
- `POST /predict` - Sentiment analysis
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## Monitoring

The application includes comprehensive monitoring:

- **Prometheus**: Collects metrics from the application
- **Grafana**: Visualizes metrics with pre-configured dashboards
 

## CI/CD Pipeline

The Jenkins pipeline includes:

1. Code checkout
2. Python environment setup
3. Test execution
4. Docker image build
5. Deployment
6. Health checks
7. Rollback on failure

## Development

### Running Tests
```bash
pytest test_app.py -v --tb=short
```

### Building Docker Image
```bash
docker build -t sentiment-analysis .
```

### Local Development
```bash
# Activate virtual environment
python -m venv devenv
devenv\Scripts\activate  # Windows
# or
source devenv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## Environment Variables

- `PORT`: Application port (default: 5000)

## 🔧 Troubleshooting

### Common Issues

#### Model Not Found
- Ensure `sentimentanalysismodel.pkl` is in the project root directory
- Check file permissions

#### Docker Issues
- **Port conflicts**: Check if ports 5000, 3000, 9090, 9100 are available
- **Docker not running**: Start Docker Desktop
- **Container won't start**: Check logs with `docker-compose logs <service-name>`
- **Permission issues**: Run `docker-compose down` then `docker-compose up -d`

#### Jenkins Pipeline Issues
- **Build fails**: Check Jenkins console output
- **Git access**: Ensure Jenkins has access to your repository
- **Docker in Jenkins**: Install Docker plugin in Jenkins
- **Windows compatibility**: The pipeline supports both Windows and Linux

#### Monitoring Issues
- **Prometheus targets down**: 
  - Check http://localhost:9090/targets
  - Verify all services are running: `docker-compose ps`
- **Grafana no data**:
  - Verify Prometheus data source URL: `http://prometheus:9090`
  - Check if Prometheus is collecting metrics
- **Dashboard not loading**:
  - Go to Grafana → Dashboards → Import
  - Look for "Sentiment Analysis Dashboard"

#### Application Issues
- **Health check fails**: Check if model file exists and is readable
- **API not responding**: Verify Flask app is running on port 5000
- **Tests failing**: Run `pytest test_app.py -v` to see detailed errors

### Useful Commands

```bash
# Check all services status
docker-compose ps

# View logs for specific service
docker-compose logs -f sentiment-app
docker-compose logs -f prometheus
docker-compose logs -f grafana

# Restart specific service
docker-compose restart sentiment-app

# Stop all services
docker-compose down

# Remove all containers and volumes
docker-compose down -v

# Rebuild and start
docker-compose up -d --build
```

### Ports Used
- **5000**: Sentiment Analysis Web App
- **3000**: Grafana Dashboard
- **9090**: Prometheus Metrics
 

## 📊 Monitoring Dashboard

The Grafana dashboard includes:
- **Total Requests**: Number of sentiment analysis requests
- **Request Duration**: Response time metrics
- **Error Rate**: Failed requests percentage
- **Request Rate**: Requests per second
- **System Metrics**: CPU, memory, disk usage

## 🔄 CI/CD Pipeline Features

- **Automatic triggers**: Runs on every commit
- **Multi-platform**: Works on Windows and Linux
- **Comprehensive testing**: Unit and integration tests
- **Docker deployment**: Automated container building
- **Health checks**: Verifies deployment success
- **Rollback**: Automatic rollback on failure
- **Notifications**: Email alerts for success/failure

## 📝 API Documentation

### POST /predict
Analyze sentiment of a text review.

**Request:**
```json
{
  "review": "This product is amazing! I love it."
}
```

**Response:**
```json
{
  "sentiment": "positive",
  "confidence": 0.95
}
```

### GET /health
Check application health and model status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### GET /metrics
Prometheus metrics endpoint.

## 🛠️ Development

### Running Tests
```bash
# Run all tests
pytest test_app.py -v

# Run with coverage
pytest test_app.py --cov=app

# Run specific test
pytest test_app.py::test_predict_positive_sentiment -v
```

### Building Docker Image
```bash
# Build image
docker build -t sentiment-analysis .

# Run container
docker run -p 5000:5000 sentiment-analysis
```

### Local Development
```bash
# Activate virtual environment
python -m venv devenv
devenv\Scripts\activate  # Windows
# or
source devenv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## 📋 Environment Variables

- `PORT`: Application port (default: 5000)

## 📄 License

This project is for educational purposes.
