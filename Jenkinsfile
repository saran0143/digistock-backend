pipeline {
    agent {
        kubernetes {
            yaml '''
              apiVersion: v1
              kind: Pod
              spec:
                containers:
                - name: docker
                  image: docker:27-dind
                  securityContext:
                    privileged: true
                  command:
                  - cat
                  tty: true
                  env:
                  - name: DOCKER_TLS_CERTDIR
                    value: ""
                  volumeMounts:
                  - name: docker-graph-storage
                    mountPath: /var/lib/docker
                - name: kubectl
                  image: bitnami/kubectl:latest
                  command:
                  - cat
                  tty: true
                volumes:
                - name: docker-graph-storage
                  emptyDir: {}
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
                sh 'dockerd & sleep 5 && docker build -t 2100031907/digistock-backend:1 .'
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
