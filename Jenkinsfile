pipeline {
    agent any
    
    environment {
        // Docker configuration
        DOCKER_IMAGE = 'sentiment-analysis-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        
        // Application configuration
        APP_NAME = 'sentiment-analysis'
        APP_PORT = '5000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out code from repository...'
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo '⚙️ Setting up Python environment...'
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
                echo '🔍 Verifying sentiment analysis model exists...'
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
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '🧪 Running unit tests...'
                sh '''
                    . venv/bin/activate
                    python -m pytest tests/ -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                echo '🔗 Running integration tests...'
                sh '''
                    . venv/bin/activate
                    python app.py &
                    APP_PID=$!
                    
                    sleep 10
                    python -m pytest integration_tests/ -v
                    kill $APP_PID || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo '🚀 Deploying full stack to staging using docker-compose...'
                sh '''
                    export COMPOSE_PROJECT_NAME=${APP_NAME}-staging
                    docker compose down || true
                    docker compose build --no-cache --pull
                    docker compose up -d
                    sleep 20
                    curl -f http://localhost:5000/health || exit 1
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
                echo '🚀 Deploying full stack to production using docker-compose...'
                sh '''
                    export COMPOSE_PROJECT_NAME=${APP_NAME}-prod
                    docker compose down || true
                    docker compose build --no-cache --pull
                    docker compose up -d
                    sleep 30
                    curl -f http://localhost:${APP_PORT}/health || exit 1
                    curl -f http://localhost:9090/-/healthy || exit 1
                    curl -f http://localhost:3000/login || exit 1
                '''
            }
        }
        
        stage('Smoke Tests') {
            steps {
                echo '✅ Running smoke tests on deployed stack...'
                sh '''
                    sleep 15
                    curl -f http://localhost:${APP_PORT}/health
                    curl -f http://localhost:${APP_PORT}/metrics
                    curl -X POST http://localhost:${APP_PORT}/predict \
                         -H "Content-Type: application/json" \
                         -d '{"review": "This is a test review"}' -f
                    curl -f http://localhost:9090/-/ready
                    curl -f http://localhost:3000/login
                '''
            }
        }
    }
    
    post {
        always {
            echo '📦 Pipeline execution completed.'
            sh '''
                rm -rf venv
                docker images ${DOCKER_IMAGE} --format "table {{.Repository}}:{{.Tag}}" | tail -n +4 | xargs -r docker rmi || true
            '''
            archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
        }
        
        success {
            echo '🎉 Pipeline succeeded!'
        }
        
        failure {
            echo '❌ Pipeline failed!'
        }
        
        unstable {
            echo '⚠️ Pipeline finished with warnings.'
        }
    }
}
 