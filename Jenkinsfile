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
                    def scannerHome = tool 'sonar-scanner'
                    withSonarQubeEnv('sonar-server') {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=aceest-fitness -Dsonar.sources=. -Dsonar.python.xunit.reportPath=test-results.xml"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker Image...'
                script {
                    dockerImage = docker.build("${IMAGE_NAME}:${env.BUILD_ID}")
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to registry...'
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_HUB_CRED) {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
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
