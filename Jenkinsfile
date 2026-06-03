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
            '''
        }
    }
    stages {
        stage('Clone') { 
            steps { 
                git branch: 'main', url: 'https://github.com/saran0143/digistock-backend.git' 
            } 
        }
        stage('Build + Push') { 
            steps { 
                container('docker') { 
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        sh '''
                          echo "=== Waiting for Docker daemon ==="
                          sleep 30
                          docker ps
                          echo "=== Building Image ==="
                          docker build -t 2100031907/digistock-backend:1 .
                          echo "=== Logging to DockerHub ==="
                          echo $PASS | docker login -u $USER --password-stdin
                          echo "=== Pushing Image ==="
                          docker push 2100031907/digistock-backend:1
                          echo "=== SUCCESS ==="
                        '''
                    }
                } 
            } 
        }
    }
}
