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
    command: ["dockerd"]
    args:
            - --dns=8.8.8.8
            - --dns=8.8.4.4
            - --host=tcp://0.0.0.0:2375
            - --host=unix:///var/run/docker.sock
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
                          
                          echo "=== Waiting for Docker daemon ==="
                          for i in $(seq 1 30); do
                            docker info >/dev/null 2>&1 && break
                            sleep 1
                          done
                          
                          echo "=== Building Image ==="
                          docker build -t 2100031907/digistock-backend:1 .
                          
                          echo "=== Pushing Image ==="
                          echo $PASS | docker login -u $USER --password-stdin
                          docker push 2100031907/digistock-backend:1
                        '''
                    }
                } 
            } 
        }
    }
}
