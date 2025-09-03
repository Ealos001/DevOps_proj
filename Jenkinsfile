pipeline {
    agent any

    environment {
        IMAGE = 'sentiment-api'
        TAG = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test API') {
            agent {
                docker {
                    image 'python:3.11'
                }
            }
            steps {
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt pytest httpx'
                sh 'pytest -q'
            }
        }

        stage('Build Docker image') {
            steps {
                sh "docker build -t ${IMAGE}:${TAG} ."
            }
        }

        stage('Integration Test') {
            steps {
                sh 'docker compose up -d --build api'
                sh '''
                for i in {1..10}; do
                  if curl -sSf http://localhost:8000/health; then
                    echo "API is healthy"
                    exit 0
                  fi
                  echo "Waiting for API..."
                  sleep 3
                done
                echo "API failed to start"
                exit 1
                '''
            }
            post {
                always { sh 'docker compose down' }
            }
        }

        stage('Deploy (docker-compose)') {
            steps {
                sh 'docker compose up -d --build'
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded.'
        }
        failure {
            echo 'Pipeline failed.'
        }
        always {
            sh 'docker images | head -n 5 || true'
        }
    }
}
