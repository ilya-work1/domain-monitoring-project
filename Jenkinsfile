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
        stage('clean workspace') {
            steps {
                cleanWs()
                echo 'workspace cleaned'
                script {
                    sh"""
                        if [ \$(sudo docker ps -aq) ]; then
                            sudo docker rm -f \$(sudo docker ps -aq)
                        else
                            echo "No containers to remove"
                        fi
                    """
                }
                echo 'docker container removed'
                }
            }

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
                            sudo docker build -t razielrey/domainmonitoring:${BUILD_TAG} .
                            sudo docker run --network=host -d --name monitoring-app-${BUILD_TAG} razielrey/domainmonitoring:${BUILD_TAG}
                        """
                    }
                }
            }
        }

        stage('Selenium Test') {
            steps {
                sh """
                    sudo docker run --network=host -d --name selenium-test ilyashev1/seleniumtest:1.0.0
                    sleep 10
                    sudo docker exec selenium-test python3 /selenium_test/test_run.py
                """
            }
        }
    }

    post {
        success {
            script {
                withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo ${DOCKER_PASS} | sudo docker login -u ${DOCKER_USER} --password-stdin
                        sudo docker tag razielrey/domainmonitoring:${BUILD_TAG} razielrey/domainmonitoring:latest
                        sudo docker push razielrey/domainmonitoring:${BUILD_TAG}
                        sudo docker push razielrey/domainmonitoring:latest
                    """
                }
            }
        }

        always {
            sh """
                sudo docker rm -f \$(sudo docker ps -aq --filter name=monitoring-app-${BUILD_TAG})
                sudo docker rm -f \$(sudo docker ps -aq --filter name=selenium-test)
            """
        }
    }
}