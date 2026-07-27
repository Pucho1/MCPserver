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

        stage('Run tests') {
            steps {
                sh 'uv run pytest'
            }
        }

        stage('Build package') {
            steps {
                sh 'uv build'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
    }

    
}