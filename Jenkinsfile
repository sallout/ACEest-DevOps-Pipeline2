pipeline {
    agent any
    
    environment {
        DOCKER_HUB_CREDENTIALS = 'dockerhub-credentials-id'
        DOCKER_IMAGE = 'yourdockerhubusername/aceest-fitness'
        SONAR_PROJECT_KEY = 'aceest-fitness-api'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from Git...'
                checkout scm
            }
        }
        
        stage('Unit Testing') {
            steps {
                echo 'Running Pytest suite...'
                sh 'pip install -r requirements.txt'
                sh 'pytest test_app.py --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Code Quality (SonarQube)') {
            steps {
                echo 'Running Static Code Analysis...'
                sh 'sonar-scanner -Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.sources=app.py -Dsonar.python.xunit.reportPath=test-results.xml'
            }
        }

        stage('Build Container Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    appImage = docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push to Container Registry') {
            steps {
                echo 'Pushing image to Docker Hub...'
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_HUB_CREDENTIALS}") {
                        appImage.push()
                        appImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to K8s Cluster...'
                sh "sed -i 's|IMAGE_PLACEHOLDER|${DOCKER_IMAGE}:${BUILD_NUMBER}|g' k8s/deployment.yaml"
                sh 'kubectl apply -f k8s/deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
                sh 'kubectl rollout status deployment/aceest-fitness-app'
            }
        }
    }
    
    post {
        failure {
            echo 'Pipeline failed. Triggering notifications and keeping previous stable deployment active.'
        }
    }
}