pipeline {
    agent any

    stages {

        stage('Environment') { // Verifico toda mi infraestructura
            steps {
                sh 'python3 --version'
                sh 'uv --version'
                sh 'git --version'
                sh 'docker --version'
                sh 'node --version'
                sh 'npm --version'
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'uv sync'
            }
        }

    }

    post {
        always {
            echo 'Pipeline finished.'
        }
    }
}