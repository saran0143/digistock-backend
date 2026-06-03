pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  dnsPolicy: "None"
  dnsConfig:
    nameservers:
      - 8.8.8.8
      - 1.1.1.1

  containers:
    - name: jnlp
      image: jenkins/inbound-agent:latest
      command:
        - cat
      tty: true
      env:
        - name: JENKINS_TUNNEL
          value: "jenkins.jenkins.svc.cluster.local:50000"
        - name: JENKINS_URL
          value: "http://jenkins.jenkins.svc.cluster.local:8080"
'''
        }
    }

    stages {
        stage('Git Clone Test') {
            steps {
                container('jnlp') {
                    sh 'echo "Agent connected successfully"'
                    sh 'cat /etc/resolv.conf'
                    sh 'nslookup github.com || true'
                    sh 'git clone https://github.com/saran0143/digistock-backend.git'
                    sh 'ls -la digistock-backend'
                }
            }
        }
    }
}
