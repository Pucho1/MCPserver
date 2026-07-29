pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'pucho1/sampling-mcp'
        IMAGE_VERSION = '0.1.1'
    }

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

                    withSonarQubeEnv('SonarQube') {
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
                sh  '''
                    docker build \
                    -t ${DOCKER_IMAGE}:${IMAGE_VERSION} \
                    -t ${DOCKER_IMAGE}:latest \
                    .
                '''
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerHub_credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login \
                            -u "$DOCKER_USER" \
                            --password-stdin
                    '''
                }
            }
        }

        stage('Push Docker image') {
            steps {
                sh '''
                    docker push ${DOCKER_IMAGE}:${IMAGE_VERSION}
                    docker push ${DOCKER_IMAGE}:latest
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
    }

    
}