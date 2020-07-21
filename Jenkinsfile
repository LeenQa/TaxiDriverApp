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
		sh 'PATH=$PATH:/usr/local/bin/virtualenv -p python myenv'
        sh 'PATH=$PATH:/usr/local/bin/source myenv/bin/activate'
        sh 'PATH=$PATH:/usr/local/bin/pip install -r requirements.txt'
        sh 'cd reports'
        sh 'touch *.xml'
        sh 'touch *.report'
        sh 'cd ..'
        sh 'PATH=$PATH:/usr/local/bin/python manage.py jenkins --enable-coverage'
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