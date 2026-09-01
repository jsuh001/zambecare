pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Validate') {
            steps {
                sh './scripts/validate_phase1.sh'
            }
        }
        stage('Test API') {
            steps {
                sh 'docker build -t zambecare-api:${BUILD_NUMBER} api'
                sh 'docker run --rm zambecare-api:${BUILD_NUMBER} pytest -q'
            }
        }
        stage('Build dbt Image') {
            steps {
                sh 'docker build -t zambecare-dbt:${BUILD_NUMBER} dbt_zambecare'
            }
        }
        stage('Deploy Development') {
            when { branch 'main' }
            steps {
                echo 'Phase 2 will deploy to an isolated development environment.'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: '**/junit*.xml'
        }
    }
}
