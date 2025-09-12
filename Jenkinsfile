pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'sentiment-analysis-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        APP_NAME = 'sentiment-analysis'
        APP_PORT = '5000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
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
                sh '''
                    if [ ! -f "sentimentanalysismodel.pkl" ]; then
                        curl -L -o sentimentanalysismodel.pkl "https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl"
                    fi
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Deploy to Staging') {
            when { branch 'develop' }
            steps {
                sh '''
                    docker compose -p ${APP_NAME}-staging down || true
                    docker compose -p ${APP_NAME}-staging up -d --build
                '''
            }
        }

        stage('Deploy to Production') {
            when { branch 'main' }
            steps {
                input "Deploy to production?"
                sh '''
                    docker compose -p ${APP_NAME}-prod down || true
                    docker compose -p ${APP_NAME}-prod up -d --build
                '''
            }
        }
    }

    post {
        always {
            sh 'rm -rf venv'
            archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
        }
    }
}
