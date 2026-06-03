pipeline {
    agent {
        kubernetes {
            yaml '''
              apiVersion: v1
              kind: Pod
              spec:
                hostNetwork: true
                dnsPolicy: ClusterFirstWithHostNet
                dnsConfig:
                  nameservers:
                    - 8.8.8.8
                    - 8.8.4.4
                  options:
                    - name: ndots
                      value: "5"
                containers:
                - name: docker
                  image: docker:24-dind
                  securityContext:
                    privileged: true
                  args: [
                    '--dns=8.8.8.8',           // ← Idi add chesa
                    '--dns=8.8.4.4',           // ← Idi add chesa
                    '--host=tcp://0.0.0.0:2375', 
                    '--host=unix:///var/run/docker.sock'
                  ]
                  tty: true
                  env:
                  - name: DOCKER_HOST
                    value: tcp://localhost:2375
                  - name: DOCKER_TLS_CERTDIR
                    value: ""
                  - name: DOCKER_DRIVER
                    value: overlay2
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
                          echo "=== Testing DNS ==="
                          nslookup auth.docker.io
                          nslookup registry-1.docker.io
                          
                          echo "=== Waiting 30s for Docker daemon ==="
                          for i in $(seq 1 30); do
                            docker info >/dev/null 2>&1 && break
                            echo "Waiting... $i/30"
                            sleep 1
                          done
                          
                          echo "=== Docker is Ready ==="
                          docker ps
                          
                          echo "=== Building Image ==="
                          docker build -t 2100031907/digistock-backend:1 .
                          
                          echo "=== Logging to DockerHub ==="
                          echo $PASS | docker login -u $USER --password-stdin
                          
                          echo "=== Pushing Image ==="
                          docker push 2100031907/digistock-backend:1
                          
                          echo "=== SUCCESS - IMAGE PUSHED ==="
                        '''
                    }
                } 
            } 
        }
    }
}
