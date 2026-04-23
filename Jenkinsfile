pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        DOCKER_IMAGE = 'sallout/fitness-api'
        SONAR_CREDENTIALS_ID = 'sonar-token'
        KUBECONFIG_CREDENTIALS_ID = 'k8s-config'
        APP_VERSION = "1.0.${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment & Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Unit Testing & Coverage') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test_app.py --junitxml=test-results.xml --cov=app --cov-report=xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'sonar-scanner'
                    withSonarQubeEnv('SonarQubeServer') {
                        sh "${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=aceest-fitness \
                            -Dsonar.sources=. \
                            -Dsonar.python.coverage.reportPaths=coverage.xml"
                    }
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${APP_VERSION}", "--build-arg APP_VERSION=${APP_VERSION} .")
                }
            }
        }

        stage('Push to Docker Registry') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDENTIALS_ID}") {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withKubeConfig([credentialsId: "${KUBECONFIG_CREDENTIALS_ID}"]) {
                    sh '''
                        # Update deployment with the new image tag
                        sed -i "s|IMAGE_TAG_PLACEHOLDER|${APP_VERSION}|g" k8s/deployment.yaml
                        
                        # Apply manifests
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        
                        # Verify deployment health
                        kubectl rollout status deployment/aceest-api-deployment
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Version ${APP_VERSION} deployed."
        }
        failure {
            echo "Pipeline failed. Check logs and investigate."
        }
    }
}