pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'sentiment-analysis-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        APP_NAME = 'sentiment-analysis'
        APP_PORT = '5000'
    }

    triggers {
        // Trigger automatico (puoi sostituire con webhook)
        pollSCM('* * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Model') {
            steps {
                sh '''
                    if [ ! -f "sentimentanalysismodel.pkl" ]; then
                        echo "ERROR: sentimentanalysismodel.pkl not found!"
                        exit 1
                    fi
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                // Build immagine usando Dockerfile del progetto senza plugin
                sh """
                    docker build --pull -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('Run Tests in Container') {
            steps {
                sh """
                    docker run --rm \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        pytest tests/ --junitxml=test-results.xml
                """
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }


        stage('Deploy to Staging') {
            when { branch 'develop' }
            steps {
                sh """
                    docker compose -p ${APP_NAME}-staging down || true
                    docker compose -p ${APP_NAME}-staging up -d --build
                """
            }
        }

        stage('Deploy to Production') {
            when { branch 'main' }
            steps {
                input "Deploy to production?"
                sh """
                    docker compose -p ${APP_NAME}-prod down || true
                    docker compose -p ${APP_NAME}-prod up -d --build
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'tests/test-results.xml', allowEmptyArchive: true
            // Pulizia immagini Docker temporanee
            sh "docker image prune -f"
        }
    }
}
