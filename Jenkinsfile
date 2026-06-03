pipeline {
    agent {
        kubernetes {
            yaml '''
              apiVersion: v1
              kind: Pod
              spec:
                hostNetwork: true
                containers:
                - name: docker
                  image: crazymax/docker:cli-dind
                  securityContext:
                    privileged: true
                  command:
                  - cat
                  tty: true
                  env:
                  - name: DOCKER_HOST
                    value: tcp://localhost:2375
                - name: kubectl
                  image: alpine/k8s:1.30.2
                  command:
                  - cat
                  tty: true
            '''
            defaultContainer 'docker'
        }
    }
    
    stages {
        stage('Clone Repo') {
            steps {
                git branch: 'main', url: 'https://github.com/saran0143/digistock-backend.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'sleep 10 && docker build -t 2100031907/digistock-backend:1 .'
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                      echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                      docker push 2100031907/digistock-backend:1
                    '''
                }
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                container('kubectl') {
                    sh 'kubectl set image deployment/digistock-backend digistock-backend=2100031907/digistock-backend:1'
                }
            }
        }
    }
}
