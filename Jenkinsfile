pipeline {
    agent any
    stages {
        stage('Preparation') {
            steps {
                git 'https://github.com/LeenQa/TaxiDriverApp'
            }
        }
        stage ('build'){
            steps {
		sh 'PATH=$PATH:/usr/local/bin/pip install -r requirements.txt'
            }
         }
        stage ('test') {
            steps {
		sh 'PATH=$PATH:/usr/local/bin/python manage.py jenkins --enable-coverage'
            }
            post {
                always {
                    junit 'reports/*.xml'
                }
            }
        }
    }
}