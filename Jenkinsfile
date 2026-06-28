pipeline {
    agent any

    environment {
        SERVICE_NAME = "notification-service"
        IMAGE_NAME   = "shopflow/notification-service"
        IMAGE_TAG    = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build Docker Image') {
            steps {
                dir('notification-service') {
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                dir('notification-service') {
                    sh '''
                        docker run --rm \
                          -e REDIS_URL=redis://localhost:6379 \
                          ${IMAGE_NAME}:${IMAGE_TAG} \
                          python -c "from app.routes import router; print('Import OK')"
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                dir('notification-service') {
                    sh "docker compose down --remove-orphans || true"
                    sh "docker compose up -d --build"
                    sh "docker compose ps"
                }
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 10
                    curl -f http://localhost:8004/health || exit 1
                    echo "Notification Service is healthy!"
                '''
            }
        }
    }

    post {
        success { echo "Notification Service deployed! Build #${BUILD_NUMBER}" }
        failure { sh "docker compose logs --tail=50 || true" }
    }
}
