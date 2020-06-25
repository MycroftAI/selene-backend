pipeline {
    agent any
    options {
        // Running builds concurrently could cause a race condition with
        // building the Docker image.
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    environment {
        // Some branches have a "/" in their name (e.g. feature/new-and-cool)
        // Some commands, such as those tha deal with directories, don't
        // play nice with this naming convention.  Define an alias for the
        // branch name that can be used in these scenarios.
        BRANCH_ALIAS = sh(
            script: 'echo $BRANCH_NAME | sed -e "s#/#-#g"',
            returnStdout: true
        ).trim()
        //spawns GITHUB_USR and GITHUB_PSW environment variables
        GITHUB=credentials('38b2e4a6-167a-40b2-be6f-d69be42c8190')
    }
    stages {
        stage('Integration Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                }
            }
            steps {
                echo 'Bootstrapping DB'
                sh 'DOCKER_BUILDKIT=1 docker build \
                    --target db-bootstrap \
                    --build-arg github_api_key=$GITHUB_PSW
                    -t selene-db:${BRANCH_ALIAS} .'
                timeout(time: 10, unit: 'MINUTES')
                {
                    sh 'docker run --net selene-net selene-db:${BRANCH_ALIAS}'
                }
                echo 'Building Account API Testing Docker Image '
                sh 'DOCKER_BUILDKIT=1 docker build \
                    --target account-api-test \
                    -t selene-account:${BRANCH_ALIAS} .'
                echo 'Running Account API Test Suite'
                timeout(time: 5, unit: 'MINUTES')
                {
                    sh 'docker run \
                        --net selene-net
                        -v "$HOME/allure/selene/:/root/allure" \
                        selene-account:${BRANCH_ALIAS}'
                }
            }
        }
    }
}
