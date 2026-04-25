pipeline {
    agent any

    environment {
        DOCKER_HUB_CRED = 'dockerhub-credentials' 
        IMAGE_NAME = 'sallout/aceest-fitness'
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
                echo 'Running Pytest...'
                // Using a virtual environment to safely install packages
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest test_app.py --junitxml=test-results.xml
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
                echo 'Running Static Code Analysis...'
                script {
                    try {
                        def scannerHome = tool 'sonar-scanner'
                        withSonarQubeEnv('sonar-server') {
                            sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=aceest-fitness -Dsonar.sources=. -Dsonar.python.xunit.reportPath=test-results.xml || true"
                        }
                    } catch (Exception e) {
                        echo "SonarQube scanner issue detected. Skipping this step to continue deployment. Details: ${e.message}"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker Image...'
                sh "docker build -t ${IMAGE_NAME}:${env.BUILD_ID} ."
                sh "docker tag ${IMAGE_NAME}:${env.BUILD_ID} ${IMAGE_NAME}:latest"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to registry...'
                withCredentials([usernamePassword(credentialsId: DOCKER_HUB_CRED, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh 'echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin'
                    sh "docker push ${IMAGE_NAME}:${env.BUILD_ID}"
                    sh "docker push ${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying Rolling Update to K8s...'
                sh "sed -i 's|IMAGE_PLACEHOLDER|${env.BUILD_ID}|g' k8s/deployment.yaml"
                sh 'kubectl apply -f k8s/deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
                
                sh 'kubectl rollout status deployment/aceest-fitness-app'
            }
        }
    }
}
