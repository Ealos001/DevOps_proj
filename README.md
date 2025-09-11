# 🎯 Sentiment Analysis DevOps Project

A complete DevOps implementation for deploying and monitoring a sentiment analysis model using Flask, Docker, Jenkins, Prometheus, and Grafana.

## 📋 Project Overview

This project implements an automated pipeline for sentiment analysis of product reviews with comprehensive monitoring and CI/CD capabilities. The system analyzes text sentiment (positive, negative, neutral) and provides real-time monitoring dashboards.

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Flask API     │    │ ML Model        │
│   (HTML/CSS/JS) │───▶│   (REST API)    │───▶│ (Pickle)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Prometheus   │◀───│    Metrics      │    │     Grafana     │
│   (Monitoring)  │    │   (Expose)      │───▶│  (Dashboard)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Jenkins     │
                       │    (CI/CD)      │
                       └─────────────────┘
```

## 🚀 Features

- **Web Interface**: Modern, responsive UI for single and batch sentiment analysis
- **REST API**: Complete API with `/predict`, `/predict-file`, `/metrics`, `/health` endpoints
- **Monitoring**: Real-time metrics with Prometheus and Grafana dashboards
- **CI/CD Pipeline**: Automated testing, building, and deployment with Jenkins
- **Containerization**: Docker containers for easy deployment and scaling
- **Testing**: Comprehensive unit and integration test suites
- **Error Handling**: Robust error handling and logging
- **Security**: Non-root user in containers, input validation

## 📁 Project Structure

```
sentiment-analysis-devops/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── download_model.py              # Model download script
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Multi-container setup
├── Jenkinsfile                    # CI/CD pipeline definition
├── pytest.ini                    # Test configuration
├── templates/
│   └── index.html                 # Web interface
├── tests/
│   └── test_app.py               # Unit tests
├── integration_tests/
│   └── test_integration.py       # Integration tests
├── monitoring/
│   ├── prometheus.yml            # Prometheus configuration
│   ├── alert_rules.yml           # Alerting rules
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/
│       │   │   └── prometheus.yml
│       │   └── dashboards/
│       │       └── dashboard.yml
│       └── dashboards/
│           └── sentiment-analysis-dashboard.json
└── README.md                     # This file
```

## 🛠️ Prerequisites

### System Requirements
- **Docker** and **Docker Compose** (v3.8+)
- **Python 3.11+** (for local development)
- **Git** for version control
- **Jenkins** (for CI/CD pipeline)

### Hardware Requirements
- **RAM**: Minimum 4GB, recommended 8GB
- **CPU**: 2+ cores recommended
- **Storage**: At least 2GB free space

## 📦 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd sentiment-analysis-devops
```

### 2. First-Time Setup

#### Option A: Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build -d

# Check services status
docker-compose ps

# View logs
docker-compose logs -f sentiment-app
```

#### Option B: Local Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download the sentiment model
python download_model.py

# Run the application
python app.py
```

### 3. Access the Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Sentiment App** | http://localhost:5000 | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin123 |

## 🔧 Configuration

### Environment Variables

```bash
# Application Configuration
FLASK_ENV=production          # or development
FLASK_APP=app.py

# Docker Configuration  
DOCKER_IMAGE=sentiment-analysis-app
DOCKER_TAG=latest
```

### Model Configuration

The application uses a pre-trained sentiment analysis model. The model is automatically downloaded on first startup or can be manually downloaded:

```bash
python download_model.py
```

## 🧪 Testing

### Run Unit Tests

```bash
# With pytest
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Run Integration Tests

```bash
# Start the application first
python app.py &

# Run integration tests
pytest integration_tests/ -v

# Kill the application
pkill -f "python app.py"
```

### Run All Tests

```bash
pytest -v --cov=app --cov-report=html --junitxml=test-results.xml
```

## 🚀 CI/CD Pipeline

### Jenkins Setup

1. **Install Jenkins** with Docker support
2. **Create a new Pipeline job**
3. **Configure SCM** to point to your repository
4. **Set the script path** to `Jenkinsfile`

### Pipeline Stages

1. **Checkout**: Clone the repository
2. **Setup Environment**: Create Python virtual environment
3. **Download Model**: Get the ML model
4. **Unit Tests**: Run pytest unit tests
5. **Code Quality**: Lint code with flake8
6. **Integration Tests**: Test API endpoints
7. **Build Docker Image**: Create container image
8. **Security Scan**: Scan for vulnerabilities
9. **Deploy to Staging**: Deploy to staging environment (develop branch)
10. **Deploy to Production**: Deploy to production (main branch, manual approval)
11. **Smoke Tests**: Verify deployment health

### Manual Pipeline Trigger

```bash
# Trigger Jenkins build via webhook (if configured)
curl -X POST http://your-jenkins:8080/job/your-job/build \
  --user your-username:your-token
```

## 📊 Monitoring & Metrics

### Prometheus Metrics

The application exposes these metrics:

- `sentiment_requests_total`: Total number of prediction requests
- `sentiment_request_duration_seconds`: Request processing time histogram
- `sentiment_errors_total`: Total number of errors
- `sentiment_model_confidence`: Current model confidence gauge

### Grafana Dashboards

Pre-configured dashboard includes:

- **Request Rate**: Requests per second
- **Response Time**: 95th percentile response times
- **Error Rate**: Errors per second  
- **Model Confidence**: ML model confidence scores
- **System Metrics**: CPU and Memory usage

### Custom Alerts

Configure alerts in `monitoring/alert_rules.yml`:

- High error rate (>0.1 errors/sec)
- High response time (>3 seconds)
- Service down
- Low model confidence (<50%)
- High resource usage

## 🔍 API Documentation

### POST /predict

Analyze sentiment for a single review.

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"review": "This product is amazing!"}'
```

**Response:**
```json
{
  "sentiment": "positive",
  "confidence": 0.95,
  "review": "This product is amazing!"
}
```

### POST /predict-file

Batch analysis from uploaded text file (one review per line).

```bash
curl -X POST http://localhost:5000/predict-file \
  -F "file=@reviews.txt"
```

### GET /metrics

Prometheus metrics endpoint.

```bash
curl http://localhost:5000/metrics
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:5000/health
```

## 🐳 Docker Commands

### Development Commands

```bash
# Build image
docker build -t sentiment-analysis-app .

# Run container
docker run -d -p 5000:5000 --name sentiment-app sentiment-analysis-app

# View logs
docker logs -f sentiment-app

# Execute shell in container
docker exec -it sentiment-app /bin/bash
```

### Production Commands

```bash
# Start all services
docker-compose up -d

# Scale the application
docker-compose up -d --scale sentiment-app=3

# Update a service
docker-compose up -d --no-deps sentiment-app

# View resource usage
docker stats
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Model Download Fails
```bash
# Manually download the model
wget -O sentimentanalysismodel.pkl "https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl"
```

#### 2. Port Already in Use
```bash
# Check what's using the port
lsof -i :5000

# Kill the process
kill -9 $(lsof -t -i:5000)
```

#### 3. Permission Denied (Docker)
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

#### 4. Out of Memory
```bash
# Check container memory usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
```

### Logs and Debugging

```bash
# Application logs
docker-compose logs sentiment-app

# All services logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Check container health
docker-compose ps
```

## 🔒 Security Considerations

- **Non-root user** in Docker containers
- **Input validation** for all endpoints
- **File upload restrictions** (16MB limit, .txt files only)
- **CORS protection** (configure as needed)
- **Rate limiting** (implement with nginx if needed)
- **HTTPS** (configure reverse proxy)

## 📈 Performance Optimization

### Scaling Strategies

1. **Horizontal Scaling**: Multiple app instances
```bash
docker-compose up -d --scale sentiment-app=3
```

2. **Load Balancing**: Use nginx or cloud load balancer
3. **Caching**: Implement Redis for frequent predictions
4. **Database**: Use PostgreSQL for storing predictions

### Resource Limits

```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Profession AI** for providing the sentiment analysis model
- **Flask** team for the excellent web framework
- **Prometheus** and **Grafana** communities for monitoring tools
- **Docker** for containerization platform

## 📞 Support

If you encounter any issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the logs: `docker-compose logs`
3. Open an issue on GitHub
4. Contact the development team

---

**Happy Analyzing! 🎯**