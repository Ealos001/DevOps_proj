pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'sentiment-analysis'
        DOCKER_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'sentiment-app'
        PORT = '5000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python environment...'
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r sentiment-app/requirements.txt
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            venv\\Scripts\\activate
                            pip install --upgrade pip
                            pip install -r sentiment-app\\requirements.txt
                        '''
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            python -m pytest sentiment-app/test_app.py -v --tb=short
                        '''
                    } else {
                        bat '''
                            venv\\Scripts\\activate
                            python -m pytest sentiment-app\\test_app.py -v --tb=short
                        '''
                    }
                }
            }
            post {
                always {
                    // Pubblica i risultati dei test (se disponibili)
                    script {
                        if (fileExists('test-results.xml')) {
                            junit 'test-results.xml'
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", 'sentiment-app')
                    docker.build("${DOCKER_IMAGE}:latest", 'sentiment-app')
                }
            }
        }
        
        stage('Stop Previous Container') {
            steps {
                echo 'Stopping previous container...'
                script {
                    try {
                        if (isUnix()) {
                            sh "docker stop ${CONTAINER_NAME} || true"
                            sh "docker rm ${CONTAINER_NAME} || true"
                        } else {
                            bat "docker stop ${CONTAINER_NAME} || exit 0"
                            bat "docker rm ${CONTAINER_NAME} || exit 0"
                        }
                    } catch (Exception e) {
                        echo 'No previous container to stop'
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                script {
                    if (isUnix()) {
                        sh '''
                            docker run -d \
                                --name ${CONTAINER_NAME} \
                                -p ${PORT}:5000 \
                                --restart unless-stopped \
                                ${DOCKER_IMAGE}:latest
                        '''
                    } else {
                        bat '''
                            docker run -d --name %CONTAINER_NAME% -p %PORT%:5000 --restart unless-stopped %DOCKER_IMAGE%:latest
                        '''
                    }
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo 'Performing health check...'
                script {
                    // Aspetta che l'app si avvii
                    sleep(time: 10, unit: 'SECONDS')
                    
                    // Verifica che l'app risponda
                    def response
                    if (isUnix()) {
                        response = sh(
                            script: "curl -f http://localhost:${PORT}/health || exit 1",
                            returnStatus: true
                        )
                    } else {
                        response = bat(
                            script: "curl -f http://localhost:${PORT}/health || exit 1",
                            returnStatus: true
                        )
                    }
                    
                    if (response != 0) {
                        error('Health check failed!')
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
            // Pulizia dell'ambiente
            script {
                if (isUnix()) {
                    sh 'docker system prune -f --volumes || true'
                } else {
                    bat 'docker system prune -f --volumes || exit 0'
                }
            }
        }
        
        success {
            echo 'Pipeline succeeded! 🎉'
            // Notifica di successo (esempio con email)
            script {
                try {
                    mail to: 'developer@company.com',
                         subject: "✅ Deploy SUCCESS - Sentiment Analysis",
                         body: """
                         Il deploy del modello di Sentiment Analysis è completato con successo!
                         
                         Build: ${BUILD_NUMBER}
                         Branch: ${BRANCH_NAME}
                         URL: http://localhost:${PORT}
                         
                         L'applicazione è ora disponibile e operativa.
                         """
                } catch (Exception e) {
                    echo 'Email notification failed, but deployment succeeded'
                }
            }
        }
        
        failure {
            echo 'Pipeline failed! ❌'
            // Rollback in caso di fallimento
            script {
                try {
                    if (isUnix()) {
                        sh "docker stop ${CONTAINER_NAME} || true"
                        sh "docker rm ${CONTAINER_NAME} || true"
                        // Riavvia la versione precedente se esiste
                        sh "docker run -d --name ${CONTAINER_NAME} -p ${PORT}:5000 ${DOCKER_IMAGE}:previous || true"
                    } else {
                        bat "docker stop ${CONTAINER_NAME} || exit 0"
                        bat "docker rm ${CONTAINER_NAME} || exit 0"
                        // Riavvia la versione precedente se esiste
                        bat "docker run -d --name ${CONTAINER_NAME} -p ${PORT}:5000 ${DOCKER_IMAGE}:previous || exit 0"
                    }
                } catch (Exception e) {
                    echo 'Rollback failed'
                }
                
                // Notifica di errore
                try {
                    mail to: 'developer@company.com',
                         subject: "❌ Deploy FAILED - Sentiment Analysis",
                         body: """
                         Il deploy del modello di Sentiment Analysis è fallito!
                         
                         Build: ${BUILD_NUMBER}
                         Branch: ${BRANCH_NAME}
                         Error: Check Jenkins logs for details
                         
                         È stato tentato un rollback automatico.
                         """
                } catch (Exception e) {
                    echo 'Email notification failed'
                }
            }
        }
    }
}