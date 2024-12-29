pipeline {
    agent {
        label 'docker'
    }

    environment {
        COMMIT_ID = '' // To store the short commit ID
        DOCKER_CREDENTIALS_ID = 'docker' // Credential ID for Docker Hub
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
                echo "Workspace cleaned successfully"
            }
        }

        stage('Clone Repository') {
            steps {
                dir('MonitoringApp') {
                    script {
                        git branch: 'raziel_jenkins', url: 'https://github.com/ilya-work1/domain-monitoring-project.git'
                        fullCommitId = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                        COMMIT_ID = fullCommitId.substring(0, 5)
                        echo "Short Commit ID: ${COMMIT_ID}"
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
                    echo "Monitoring App Docker container is running"
                }
            }
        }

        stage('Start running Selenium tests') {
            steps {
                sh '''
                 docker run -d --name selenium-test ilyashev1/seleniumtest
                  sleep 10
                    docker exec selenium-test python3 /app/test.py 
                '''
                echo "Selenium tests completed"
            }
        }

    }

    post {
        success {
            echo "Pipeline succeeded. Preparing to push Docker image to Docker Hub."
            script {
                withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo $DOCKER_USER $DOCKER_PASS 
                        sudo docker login -u $DOCKER_USER -p $DOCKER_PASS
                        sudo docker tag monitoring-app:${COMMIT_ID} razielrey/domainmonitoring:${COMMIT_ID}
                        sudo docker push razielrey/domainmonitoring:${COMMIT_ID}

                    '''
                }

            }
        }
        failure {
            echo "Pipeline failed. Not pushing Docker image to Docker Hub."
        }

        always {
            sh '''
                docker stop $(docker ps -a -q)
                docker rm $(docker ps -a -q)
                docker rmi $(docker images -q)
            '''
            echo "Pipeline completed"
        }
    }