// Declarative Jenkins pipeline for the Heart Disease MLOps project.
//
// Required Jenkins plugins:
//   - Pipeline, Git, Docker Pipeline, Credentials Binding, JUnit, HTML Publisher
//
// Required credentials (configure in: Manage Jenkins -> Credentials):
//   - dockerhub-creds        (username/password)  -- only if pushing to DockerHub
//   - kubeconfig-cred        (secret file)        -- only if deploying to k8s
//
// Branch strategy:
//   - Test + lint + train run on every branch.
//   - Image build/push and k8s deploy run only on `main`.

pipeline {
    agent any

    options {
        timestamps()
        ansiColor('xterm')
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        PYTHON          = 'python3'
        VENV            = '.venv'
        IMAGE_REPO      = 'heart-disease-api'
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        REGISTRY        = ''           // e.g. 'docker.io/yourname' -- leave empty to skip push
        K8S_NAMESPACE   = 'mlops'
        DEPLOY_TO_K8S   = 'false'      // set to 'true' once kubeconfig-cred is configured
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python') {
            steps {
                // `uv` is provided by the Jenkins image; it's significantly
                // faster than pip and resolves the venv against a pinned 3.11
                // toolchain so the wheels in requirements.txt are available.
                sh '''
                    set -eux
                    uv venv --clear --python 3.11 ${VENV}
                    . ${VENV}/bin/activate
                    # mlflow imports pkg_resources at runtime; uv venvs don't
                    # include setuptools by default, and setuptools >=81 has
                    # removed pkg_resources, so pin a compatible version.
                    uv pip install "setuptools<81"
                    uv pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    flake8 src tests
                '''
            }
        }

        stage('Download data') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    python -m src.data.download_data
                '''
            }
        }

        stage('Unit tests') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    pytest --junitxml=reports/junit.xml --cov=src --cov-report=xml:reports/coverage.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('Train model') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    python -m src.models.train
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'models/*.pkl,models/metrics.json,mlruns/**', allowEmptyArchive: true
                }
            }
        }

        stage('Build Docker image') {
            // The job is a single-branch pipeline, so `when { branch ... }`
            // is skipped (it only works in multibranch). Build unconditionally.
            steps {
                script {
                    def fullName = (env.REGISTRY?.trim()) ? "${env.REGISTRY}/${env.IMAGE_REPO}" : env.IMAGE_REPO
                    sh "docker build -t ${fullName}:${env.IMAGE_TAG} -t ${fullName}:latest -f deployment/Dockerfile ."
                    env.IMAGE_FULL = fullName
                }
            }
        }

        stage('Push image') {
            when {
                expression { return env.REGISTRY?.trim() }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'REG_USER',
                                                  passwordVariable: 'REG_PASS')]) {
                    sh '''
                        echo "$REG_PASS" | docker login -u "$REG_USER" --password-stdin
                        docker push ${IMAGE_FULL}:${IMAGE_TAG}
                        docker push ${IMAGE_FULL}:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                expression { return env.DEPLOY_TO_K8S == 'true' }
            }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig-cred', variable: 'KUBECONFIG')]) {
                    sh '''
                        kubectl -n ${K8S_NAMESPACE} apply -f deployment/k8s/
                        kubectl -n ${K8S_NAMESPACE} set image deployment/heart-disease-api \
                            api=${IMAGE_FULL}:${IMAGE_TAG} --record
                        kubectl -n ${K8S_NAMESPACE} rollout status deployment/heart-disease-api --timeout=180s
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        failure {
            echo 'Pipeline failed - inspect stage logs above.'
        }
    }
}
