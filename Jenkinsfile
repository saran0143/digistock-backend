pipeline {
    agent {
        kubernetes {
            yaml '''
              apiVersion: v1
              kind: Pod
              spec:
                hostNetwork: true
                dnsPolicy: ClusterFirstWithHostNet
                containers:
                - name: docker
                  image: docker:24-dind
                  securityContext:
                    privileged: true
                  command: ['cat']
                  tty: true
                  env:
                  - name: DOCKER_HOST
                    value: tcp://localhost:2375
                  - name: DOCKER_TLS_CERTDIR
                    value: ""
                - name: kubectl
                  image: bitnami/kubectl:1.30
                  command: ['cat']
                  tty: true
            '''
        }
    }
    stages {
        stage('Clone') { 
            steps { 
                git branch: 'main', url: 'https://github.com/saran0143/digistock-backend.git' 
            } 
        }
        stage('Build Image') { 
            steps { 
                container('docker') { 
                    sh '''
                      sleep 20
                      docker ps
                      docker build -t 2100031907/digistock-backend:1 .
                    '''
                } 
            } 
        }
        stage('Push to DockerHub') { 
            steps { 
                container('docker') { 
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) { 
                        sh 'echo $PASS | docker login -u $USER --password-stdin && docker push 2100031907/digistock-backend:1' 
                    } 
                } 
            } 
        }
        stage('Deploy') { 
            steps { 
                container('kubectl') { 
                    sh 'kubectl get nodes && echo "Deploy skip - first run"'
                } 
            } 
        }
    }
}
