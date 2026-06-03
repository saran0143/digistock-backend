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
                  command: ['cat']
                  tty: true
                  env:
                  - name: DOCKER_HOST
                    value: tcp://localhost:2375
                - name: kubectl
                  image: alpine/k8s:1.30.2
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
                    sh 'sleep 10 && docker build -t 2100031907/digistock-backend:1 .' 
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
                    sh 'kubectl set image deployment/digistock-backend digistock-backend=2100031907/digistock-backend:1 || echo "Skip deploy - first run"' 
                } 
            } 
        }
    }
}
