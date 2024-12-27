def commitId
def fullCommitId

pipeline {
    agent {
        label 'docker'
    }

    environment {
        DOCKER_CREDENTIALS_ID = 'docker'
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
            
            stage('clone repo'){
                steps {
                    dir('Monitoring app'){
                    git branch: 'dev', url: 'https://github.com/ilya-work1/domain-monitoring-project.git'
                    script {
                        fullCommitId = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                        commitId = fullCommitId.substring(0, 5)
                    }
                }
            }
        }
            stage('docker build & run'){
                steps {
                    dir('Monitoring app') {
                        script {
                            echo "Commit ID is ${commitId}"
                        }
                        sh """
                        sudo docker build -t monitorsystem:${fullCommitId} . 1> /dev/null
                        sudo docker run --network host --name moniappci -p 8080:8080 -d monitorsystem:${fullCommitId}
                        """
                    }
                }
            }

            stage('selenium test'){
                steps{
                    dir('tests') {
                        script {
                            sh """
                            sudo docker run --network host --name test ilyashev1/seleniumtest:1.0.0
                            sudo docker logs test | grep -E 'passed|failed'
                            """
                        }
                    }
                }
            }
        }
    
        post {
            success {
                echo 'Success - Build completed.'
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]){
                        sh """
                        echo ${DOCKER_PASS} | sudo docker login -u ${DOCKER_USER} --password-stdin
                        sudo docker tag monitorsystem:${fullCommitId} ilyashev1/monitorsystem:${fullCommitId}
                        sudo docker push ilyashev1/monitorsystem:${fullCommitId}
                        """
                    }
                }
            }
    
            failure {
                echo 'Failure - Build failed.'
            }
            always {
                sh 'sudo docker rm -f $(sudo docker ps -aq)'
                echo 'deleted all containers'
            }
        }
    }
