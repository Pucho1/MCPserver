pipeline {
    agent any

    stages {

        stage('Checkout OK') {
            steps {
                echo 'Repository cloned successfully.'
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