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
                sh 'mkdir -p reports'
                sh 'uv run pytest --cov --junitxml=reports/junit.xml'
            }
            
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner' // Dame la ruta donde está instalada la herramienta llamada SonarScannerc

                    withSonarQubeEnv('Sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Build package') {
            steps {
                sh 'uv build'
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t sampling-server:ci .'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
    }

    
}