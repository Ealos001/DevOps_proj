pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/<user>/<repo>.git'
            }
        }

        stage('Install & Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest test.py'
            }
        }

        stage('Build Docker') {
            steps {
                sh 'docker build -t flask-sentiment-app .'
            }
        }

        stage('Run Container') {
            steps {
                sh 'docker stop flask-sentiment || true && docker rm flask-sentiment || true'
                sh 'docker run -d --name flask-sentiment -p 5000:5000 flask-sentiment-app'
            }
        }
    }
}
