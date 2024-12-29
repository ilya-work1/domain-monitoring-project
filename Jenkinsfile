pipeline {
    agent {
        label 'docker'
    }

    environment {
        DOCKER_CREDENTIALS_ID = 'docker'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
                echo 'Workspace cleaned successfully'
            }
        }

        stage('Clone Repository') {
            steps {
                dir('MonitoringApp') {
                    script {
                        git branch: 'raziel_jenkins', url: 'https://github.com/ilya-work1/domain-monitoring-project.git'
                        fullCommitId = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                        COMMIT_ID = fullCommitId.substring(0, 5)
                    }
                }
            }
        }

        stage('Docker Build & Run Monitoring App') {
            steps {
                dir('MonitoringApp') {
                    sh '''
                        docker build -t monitoring-app:${COMMIT_ID} .
                        docker run --network=host -p 8080:8080 -d monitoring-app:${COMMIT_ID}
                    '''
                }
            }
        }

        stage('Selenium Test') {
            steps {
                sh '''
                    docker run -d --name selenium-test ilyashev1/seleniumtest
                    sleep 10
                    docker exec selenium-test python3 /app/test.py
                '''
            }
        }
    }

    post {
        success {
            script {
                withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                        docker tag monitoring-app:${COMMIT_ID} ilyashev1/monitoring-app:${COMMIT_ID}
                        docker push ilyashev1/monitoring-app:${COMMIT_ID}
                    '''
                }
            }
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed.'
        }

        always {
            sh 'docker rm -f $(docker ps -aq)'
            echo 'Cleaned up Docker containers.'
        }
    }
}
