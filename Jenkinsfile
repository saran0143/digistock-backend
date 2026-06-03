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
                  args: ['--host=tcp://0.0.0.0:2375', '--host=unix:///var/run/docker.sock']
                  tty: true
                  env:
                                    - name: DOCKER_HOST
                    value: tcp://localhost:2375
                                    - name: DOCKER_TLS_CERTDIR
                    value: ""
                                    - name: DOCKER_DRIVER
                    value: overlay2
                                - name: kubectl
                  image: bitnami/kubectl:1.29
                  command:
                                    - sleep
                  args:
                                    - infinity
                  tty: true
            '''
        }
    }
    environment {
        IMAGE_NAME = "2100031907/digistock-backend"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        K8S_DEPLOYMENT = "digistock-backend"
        K8S_NAMESPACE = "default"
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
                          docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                          echo "=== Logging to DockerHub ==="
                          echo $PASS | docker login -u $USER --password-stdin
                          echo "=== Pushing Image ==="
                          docker push ${IMAGE_NAME}:${IMAGE_TAG}
                          docker push ${IMAGE_NAME}:latest
                          echo "=== SUCCESS - IMAGE PUSHED ==="
                        '''
                    }
                } 
            } 
        }
        stage('Deploy to K8s') {
            steps {
                container('kubectl') {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                        sh '''
                          export KUBECONFIG=$KUBECONFIG_FILE
                          echo "=== Current Context ==="
                          kubectl config current-context
                          
                          echo "=== Check Deployment Exists ==="
                          kubectl get deployment ${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE}
                          
                          echo "=== Updating Deployment ==="
                          kubectl set image deployment/${K8S_DEPLOYMENT} ${K8S_DEPLOYMENT}=${IMAGE_NAME}:${IMAGE_TAG} -n ${K8S_NAMESPACE}
                          
                          echo "=== Waiting for Rollout ==="
                          kubectl rollout status deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE} --timeout=2m
                          
                          echo "=== Current Pods ==="
                          kubectl get pods -l app=${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE}
                          
                          echo "=== DEPLOY SUCCESS ==="
                        '''
                    }
                }
            }
        }
    }
    post {
        success {
            echo "Pipeline Success: ${IMAGE_NAME}:${IMAGE_TAG} deployed to ${K8S_NAMESPACE}"
        }
        failure {
            echo "Pipeline Failed. Check logs."
        }
    }
}
