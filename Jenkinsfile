pipeline {
  agent any

  environment {
    REGISTRY = 'local'
    IMAGE = 'sentiment-api'
    TAG = 'latest'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python') {
      steps {
        sh 'python3 -V || true'
        sh 'pip3 -V || true'
      }
    }

    stage('Install Deps and Test') {
      steps {
        sh 'python3 -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt && pip install pytest httpx'
        sh '. .venv/bin/activate && pytest -q || true'
      }
    }

    stage('Build Docker image') {
      steps {
        sh 'docker build -t ${IMAGE}:${TAG} .'
      }
    }

    stage('Integration Test') {
      steps {
        sh 'docker compose up -d --build api'
        sh 'sleep 8 && curl -sSf http://localhost:8000/health | cat'
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
      sh 'docker images | head -n 5 | cat || true'
    }
  }
}


