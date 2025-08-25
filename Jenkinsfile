pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t sentiment-api ./model_api'
            }
        }
        stage('Test') {
            steps {
                sh 'docker run --rm sentiment-api pytest test.py'
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker compose up -d --build model-api'
            }
        }
    }
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
