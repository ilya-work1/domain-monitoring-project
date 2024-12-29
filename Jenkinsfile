pipeline {
    agent {
        label 'docker'
    }

    environment {
        DOCKER_CREDENTIALS_ID = 'docker'
        // Use BUILD_NUMBER as a unique tag
        BUILD_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Clone Repository') {
            steps {
                dir('MonitoringApp') {
                    script {
                        git branch: 'raziel_jenkins', url: 'https://github.com/ilya-work1/domain-monitoring-project.git'
                        COMMIT_ID = sh(script: 'git rev-parse HEAD', returnStdout: true).trim().take(5)
                    }
                }
            }
        }

        stage('Docker Build & Run Monitoring App') {
            steps {
                dir('MonitoringApp') {
                    script {
                        sh """
                            docker build -t razielrey/domainmonitoring:${BUILD_TAG} .
                            docker run --network=host -d --name monitoring-app-${BUILD_TAG} ilyashev1/monitorsystem:latest

                        """
                    }
                }
            }
        }

        stage('Selenium Test') {
            steps {
                sh """
                    docker run --network=host -d --name selenium-test-${BUILD_TAG} ilyashev1/seleniumtest:1.0.0
                    sleep 10
                    docker exec selenium-test-${BUILD_TAG} python3 /selenium_test/test_run.py
                """
            }
        }
    }

    post {
        success {
            script {
                withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                        docker tag razielrey/domainmonitoring:${BUILD_TAG} razielrey/domainmonitoring:latest
                        docker push razielrey/domainmonitoring:${BUILD_TAG}
                        docker push razielrey/domainmonitoring:latest
                    """
                }
            }
        }

        always {
            sh """
                docker rm -f \$(docker ps -aq --filter name=monitoring-app-${BUILD_TAG})
                docker rm -f \$(docker ps -aq --filter name=selenium-test-${BUILD_TAG})
            """
        }
    }
}