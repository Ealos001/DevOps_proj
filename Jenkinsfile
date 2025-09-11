pipeline {
    agent any
    
    environment {
        // Docker configuration
        DOCKER_IMAGE = 'sentiment-analysis-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'localhost:5000'  // Local registry or change to your registry
        
        // Application configuration
        APP_NAME = 'sentiment-analysis'
        APP_PORT = '5000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo 'Setting up Python environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Verify Model') {
            steps {
                echo 'Verifying sentiment analysis model exists...'
                sh '''
                    if [ ! -f "sentimentanalysismodel.pkl" ]; then
                        echo "Model file not found. Downloading..."
                        (
                          curl -L -o sentimentanalysismodel.pkl "https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl" \
                          || python - <<'PY'
import urllib.request
url = "https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl"
urllib.request.urlretrieve(url, "sentimentanalysismodel.pkl")
print("Downloaded model via Python")
PY
                        ) || { echo "ERROR: Failed to download sentimentanalysismodel.pkl"; exit 1; }
                    fi
                    echo "✅ Model file present: sentimentanalysismodel.pkl"
                    ls -la sentimentanalysismodel.pkl
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    . venv/bin/activate
                    python -m pytest tests/ -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    // Publish test results
                    publishTestResults testResultsPattern: 'test-results.xml'
                }
            }
        }
        
        stage('Code Quality') {
            steps {
                echo 'Running code quality checks...'
                sh '''
                    . venv/bin/activate
                    # Install flake8 for linting
                    pip install flake8
                    # Run linting (ignore long lines and some Flask-specific issues)
                    flake8 app.py --max-line-length=120 --ignore=E402,W503 || true
                '''
            }
        }
        
        stage('Integration Tests') {
            steps {
                echo 'Running integration tests...'
                sh '''
                    . venv/bin/activate
                    # Start the app in background
                    python app.py &
                    APP_PID=$!
                    
                    # Wait for app to start
                    sleep 10
                    
                    # Run integration tests
                    python -m pytest integration_tests/ -v
                    
                    # Kill the app
                    kill $APP_PID || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    // Build the Docker image
                    def image = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    
                    // Tag as latest
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Running security scan on Docker image...'
                sh '''
                    # Install and run Docker security scanner (example with trivy)
                    # docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                    echo "Security scan placeholder - integrate with your preferred scanner"
                '''
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying full stack to staging using docker-compose...'
                sh '''
                    # Use a separate project name for staging to avoid conflicts
                    export COMPOSE_PROJECT_NAME=${APP_NAME}-staging

                    # Recreate all services defined in docker-compose.yml
                    docker compose down || true
                    docker compose build --no-cache --pull
                    docker compose up -d

                    # Wait for app to become healthy
                    sleep 20
                    curl -f http://localhost:5000/health || exit 1

                    # Quick checks for monitoring stack
                    curl -f http://localhost:9090/-/healthy || exit 1
                    curl -f http://localhost:3000/login || exit 1
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                echo 'Deploying full stack to production using docker-compose...'
                sh '''
                    export COMPOSE_PROJECT_NAME=${APP_NAME}-prod

                    # Bring down old stack and recreate
                    docker compose down || true
                    docker compose build --no-cache --pull
                    docker compose up -d

                    # Health checks
                    sleep 30
                    curl -f http://localhost:${APP_PORT}/health || exit 1
                    curl -f http://localhost:9090/-/healthy || exit 1
                    curl -f http://localhost:3000/login || exit 1
                '''
            }
        }
        
        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                echo 'Pushing image to Docker registry...'
                sh '''
                    # Tag for registry
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                    
                    # Push to registry
                    # docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    # docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                    echo "Registry push placeholder - configure your Docker registry"
                '''
            }
        }
        
        stage('Smoke Tests') {
            steps {
                echo 'Running smoke tests on deployed stack...'
                sh '''
                    # Wait for services to be fully ready
                    sleep 15

                    # App endpoints
                    curl -f http://localhost:${APP_PORT}/health
                    curl -f http://localhost:${APP_PORT}/metrics
                    curl -X POST http://localhost:${APP_PORT}/predict \
                         -H "Content-Type: application/json" \
                         -d '{"review": "This is a test review"}' \
                         -f

                    # Prometheus
                    curl -f http://localhost:9090/-/ready

                    # Grafana (login page ok is enough)
                    curl -f http://localhost:3000/login
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed.'
            
            // Clean up workspace
            sh '''
                # Remove virtual environment
                rm -rf venv
                
                # Clean up old Docker images (keep last 3)
                docker images ${DOCKER_IMAGE} --format "table {{.Repository}}:{{.Tag}}" | tail -n +4 | xargs -r docker rmi || true
            '''
            
            // Archive artifacts
            archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
        }
        
        success {
            echo 'Pipeline succeeded!'
            
            // Notifications for successful deployment
            script {
                if (env.BRANCH_NAME == 'main') {
                    // Production deployment notification
                    echo 'Sending production deployment notification...'
                    // Add your notification logic here (Slack, email, etc.)
                } else if (env.BRANCH_NAME == 'develop') {
                    // Staging deployment notification
                    echo 'Sending staging deployment notification...'
                }
            }
        }
        
        failure {
            echo 'Pipeline failed!'
            
            // Cleanup failed containers
            sh '''
                docker stop ${APP_NAME}-staging || true
                docker rm ${APP_NAME}-staging || true
            '''
            
            // Send failure notification
            echo 'Sending failure notification...'
            // Add your notification logic here
        }
        
        unstable {
            echo 'Pipeline finished with warnings.'
        }
    }
}