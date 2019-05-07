pipeline {
    agent any

    stages {

        // Create the virtual environments and install the packages
        stage('Dev PR') {
            when {
                changeRequest target: 'dev'
            }
            steps {
                echo 'setting up the mycroft db'
                sh '''
                    cd db
                    pipenv install
                '''
                echo 'running account API tests...'
                sh '''
                    cd api/account
                    pipenv install
                    pipenv install --dev
                '''
            }
        }
    }
}
