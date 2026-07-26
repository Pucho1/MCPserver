pipeline {
    agent any  // "Ejecuta este pipeline en cualquier nodo disponible.

    stages {

        stage('Checkout OK') {
            steps {
                echo 'Repository cloned successfully.'
            }
        }

        stage('Inspect Environment') {
            steps {

                echo '=== USER ==='
                sh 'whoami'

                echo '=== WORKSPACE ==='
                sh 'pwd'

                echo '=== OS ==='
                sh 'uname -a'

                echo '=== GIT ==='
                sh 'git --version'

                echo '=== PYTHON ==='
                sh 'python3 --version || true'

                echo '=== UV ==='
                sh 'uv --version || true'

                echo '=== DOCKER ==='
                sh 'docker --version || true'

            }
        }

    }

    post {
        always {
            echo 'Pipeline finished.'
        }

        success {
            echo 'Pipeline SUCCESS'
        }

        failure {
            echo 'Pipeline FAILED'
        }
    }
}