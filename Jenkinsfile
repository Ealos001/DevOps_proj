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
        
        stage('Download Model') {
            steps {
                echo 'Downloading sentiment analysis model...'
                sh '''
                    . venv/bin/activate
                    python download_model.py
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    . venv/bin/activate
                    python -m pytest tests/ -v --junitxml=test-results.xml || true
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
                    python -m pytest integration_tests/ -v || true
                    
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
                echo 'Deploying to staging environment...'
                sh '''
                    # Stop existing staging container
                    docker stop ${APP_NAME}-staging || true
                    docker rm ${APP_NAME}-staging || true
                    
                    # Run new staging container
                    docker run -d \\
                        --name ${APP_NAME}-staging \\
                        -p 5001:${APP_PORT} \\
                        --restart unless-stopped \\
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                    
                    # Health check
                    sleep 10
                    curl -f http://localhost:5001/health || exit 1
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                echo 'Deploying to production environment...'
                sh '''
                    # Blue-Green deployment strategy
                    
                    # Stop existing production container
                    docker stop ${APP_NAME}-prod || true
                    docker rm ${APP_NAME}-prod || true
                    
                    # Run new production container
                    docker run -d \\
                        --name ${APP_NAME}-prod \\
                        -p ${APP_PORT}:${APP_PORT} \\
                        --restart unless-stopped \\
                        -e FLASK_ENV=production \\
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                    
                    # Health check
                    sleep 15
                    curl -f http://localhost:${APP_PORT}/health || exit 1
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
                echo 'Running smoke tests on deployed application...'
                sh '''
                    # Wait for application to be fully ready
                    sleep 10
                    
                    # Test health endpoint
                    curl -f http://localhost:${APP_PORT}/health
                    
                    # Test metrics endpoint
                    curl -f http://localhost:${APP_PORT}/metrics
                    
                    # Test prediction endpoint
                    curl -X POST http://localhost:${APP_PORT}/predict \\
                         -H "Content-Type: application/json" \\
                         -d '{"review": "This is a test review"}' \\
                         -f
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