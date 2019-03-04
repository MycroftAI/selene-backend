pipeline {
    agent any

    stages {

        // Create the virtual environments and install the packages
        stage('Build dev branch') {
            when {
                branch 'dev'
            }
            steps {
                echo 'Building code in the "dev" branch...'
                sh '''
                    cd api/account
                    pipenv install
                    pipenv install --dev
                '''
            }
        }

    }
}
