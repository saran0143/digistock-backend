pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        IMAGE_NAME = "your-dockerhub-2100031907/digistock-backend"  
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Clone Repo') {
            steps {
                git branch: 'main', url: 'https://github.com/your-username/your-backend-repo.git' // Idi marchu
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push()
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push('latest')
                    }
                }
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                script {
                    sh "kubectl set image deployment/digistock-backend digistock-backend=${IMAGE_NAME}:${IMAGE_TAG} --record"
                    sh "kubectl rollout status deployment/digistock-backend"
                }
            }
        }
    }
}