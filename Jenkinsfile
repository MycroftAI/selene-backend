pipeline {
    agent any
    options {
        // Running builds concurrently could cause a race condition with
        // building the Docker image.
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '5'))
        ansiColor('xterm')
    }
    environment {
        // Some branches have a "/" in their name (e.g. feature/new-and-cool)
        // Some commands, such as those that deal with directories, don't
        // play nice with this naming convention.  Define an alias for the
        // branch name that can be used in these scenarios.
        BRANCH_ALIAS = sh(
            script: 'echo $BRANCH_NAME | sed -e "s#/#-#g"',
            returnStdout: true
        ).trim()
        DOCKER_BUILDKIT=1
        //spawns GITHUB_USR and GITHUB_PSW environment variables
        GITHUB_API_KEY=credentials('38b2e4a6-167a-40b2-be6f-d69be42c8190')
        GITHUB_CLIENT_ID=credentials('380f58b1-8a33-4a9d-a67b-354a9b0e792e')
        GITHUB_CLIENT_SECRET=credentials('71626c21-de59-4450-bfad-5034fd596fb2')
        GOOGLE_STT_KEY=credentials('287949f8-2ada-4450-8806-1fe2dd8e4c4d')
        STRIPE_KEY=credentials('9980e41f-d418-49af-9d62-341d1246f555')
        WOLFRAM_ALPHA_KEY=credentials('f718e0a1-c19c-4c7f-af88-0689738ccaa1')
    }
    stages {
        stage('Lint & Format') {
            // Run PyLint and Black to check code quality.
            when {
                anyOf {
                    changeRequest target: 'dev'
                    changeRequest target: 'master'
                }
            }
            steps {
                labelledShell label: 'Account API Setup', script: """
                     docker build \
                        --build-arg github_api_key=${GITHUB_API_KEY} \
                        --build-arg api_name=account \
                        --target api-code-check --no-cache \
                        -t selene-linter:${BRANCH_ALIAS} .
                """
                labelledShell label: 'Account API Check', script: """
                    docker run selene-linter:${BRANCH_ALIAS} --poetry-dir api/account --pull-request=${BRANCH_NAME}
                """
                labelledShell label: 'Single Sign On API Setup', script: """
                     docker build \
                        --build-arg github_api_key=${GITHUB_API_KEY} \
                        --build-arg api_name=sso \
                        --target api-code-check --no-cache \
                        -t selene-linter:${BRANCH_ALIAS} .
                """
                labelledShell label: 'Single Sign On API Check', script: """
                    docker run selene-linter:${BRANCH_ALIAS} --poetry-dir api/sso --pull-request=${BRANCH_NAME}
                """
                labelledShell label: 'Public API Setup', script: """
                     docker build \
                        --build-arg github_api_key=${GITHUB_API_KEY} \
                        --build-arg api_name=public \
                        --target api-code-check --no-cache \
                        --label job=${JOB_NAME} \
                        -t selene-linter:${BRANCH_ALIAS} .
                """
                labelledShell label: 'Public API Check', script: """
                    docker run selene-linter:${BRANCH_ALIAS} --poetry-dir api/public --pull-request=${BRANCH_NAME}
                """
            }
        }
        stage('Bootstrap DB') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                    changeRequest target: 'master'
                }
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                    docker build \
                        --target db-bootstrap \
                        --build-arg github_api_key=${GITHUB_API_KEY} \
                        --label job=${JOB_NAME} \
                        -t selene-db:${BRANCH_ALIAS} .
                """
                timeout(time: 5, unit: 'MINUTES')
                {
                    labelledShell label: 'Run database bootstrap script', script: """
                        docker run \
                            -v '${HOME}/selene:/tmp/selene' \
                            --net selene-net selene-db:${BRANCH_ALIAS}
                    """
                }
            }
        }
        stage('Account API Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                    changeRequest target: 'master'
                }
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                    docker build \
                        --build-arg stripe_api_key=${STRIPE_KEY} \
                        --target account-api-test \
                        --label job=${JOB_NAME} \
                        -t selene-account:${BRANCH_ALIAS} .
                """
                timeout(time: 5, unit: 'MINUTES')
                {
                    sh 'mkdir -p $HOME/selene/$BRANCH_ALIAS/allure'
                    labelledShell label: 'Running behave tests', script: """
                        docker run \
                            --net selene-net \
                            -v '$HOME/selene/$BRANCH_ALIAS/allure/:/root/allure' \
                            --label job=${JOB_NAME} \
                            selene-account:${BRANCH_ALIAS}
                    """
                }
            }
            post {
                always {
                    sh 'docker run \
                        -v "$HOME/selene/$BRANCH_ALIAS/allure:/root/allure" \
                        --entrypoint=/bin/bash \
                        --label build=${JOB_NAME} \
                        selene-account:${BRANCH_ALIAS} \
                        -x -c "chown $(id -u $USER):$(id -g $USER) \
                        -R /root/allure/"'
                }
            }
        }
        stage('Single Sign On API Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                    changeRequest target: 'master'
                }
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                    docker build \
                        --build-arg github_client_id=${GITHUB_CLIENT_ID} \
                        --build-arg github_client_secret=${GITHUB_CLIENT_SECRET} \
                        --target sso-api-test \
                        --label job=${JOB_NAME} \
                        -t selene-sso:${BRANCH_ALIAS} .
                """
                timeout(time: 2, unit: 'MINUTES')
                {
                    labelledShell label: 'Running behave tests', script: """
                        docker run \
                            --net selene-net \
                            -v '$HOME/selene/$BRANCH_ALIAS/allure/:/root/allure' \
                            selene-sso:${BRANCH_ALIAS}
                    """
                }
            }
            post {
                always {
                    sh 'docker run \
                        -v "$HOME/selene/$BRANCH_ALIAS/allure:/root/allure" \
                        --entrypoint=/bin/bash \
                        --label build=${JOB_NAME} \
                        selene-sso:${BRANCH_ALIAS} \
                        -x -c "chown $(id -u $USER):$(id -g $USER) \
                        -R /root/allure/"'
                }
            }
        }
        stage('Public Device API Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                    changeRequest target: 'master'
                }
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                    docker build \
                        --build-arg google_stt_key=${GOOGLE_STT_KEY} \
                        --build-arg wolfram_alpha_key=${WOLFRAM_ALPHA_KEY} \
                        --target public-api-test \
                        --label job=${JOB_NAME} \
                        -t selene-public:${BRANCH_ALIAS} .
                """
                timeout(time: 2, unit: 'MINUTES')
                {
                    labelledShell label: 'Running behave tests', script: """
                        docker run \
                            --net selene-net \
                            -v '$HOME/selene/$BRANCH_ALIAS/allure/:/root/allure' \
                            selene-public:${BRANCH_ALIAS}
                    """
                }
            }
            post {
                always {
                    sh 'docker run \
                        -v "$HOME/selene/$BRANCH_ALIAS/allure:/root/allure" \
                        --entrypoint=/bin/bash \
                        --label build=${JOB_NAME} \
                        selene-account:${BRANCH_ALIAS} \
                        -x -c "chown $(id -u $USER):$(id -g $USER) \
                        -R /root/allure/"'
                }
            }
        }
    }
    post {
        always {
            sh 'rm -rf allure-result/*'
            sh 'mkdir -p $HOME/selene/$BRANCH_ALIAS/allure'
            sh 'mv $HOME/selene/$BRANCH_ALIAS/allure/allure-result allure-result'
            // This directory should now be empty, rmdir will intentionally fail if not.
            sh 'rmdir $HOME/selene/$BRANCH_ALIAS/allure'
            script {
                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'allure-result']]
                ])
            }
            sh(
                label: 'Cleanup lingering docker containers and images.',
                script: """
                    docker container prune --force;
                    docker image prune --force;
                """
            )
        }
        success {
            // Docker images should remain upon failure for troubleshooting purposes.  However,
            // if the stage is successful, there is no reason to look back at the Docker image.  In theory
            // broken builds will eventually be fixed so this step should run eventually for every PR
            sh(
                label: 'Delete Docker Image on Success',
                script: '''
                    docker image prune --all --force --filter label=job=${JOB_NAME};
                '''
            )
        }
    }
}
