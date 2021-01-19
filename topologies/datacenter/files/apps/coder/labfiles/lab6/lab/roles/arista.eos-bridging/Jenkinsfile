#!/usr/bin/env groovy

/*
 * Jenkinsfile for ansible-eos-bridging role
 *
 * Run the Ansible-Role-Test job against a commit or
 * pull request in the ansible-eos-bridging repo
 */

pipeline {
    agent { label 'master' }
    options {
        buildDiscarder(
            // Only keep the 20 most recent builds
            logRotator(numToKeepStr:'20'))
    }
    environment {
        projectName = 'ansible-eos-bridging'
        emailTo = 'ansible-dev+jenkins@arista.com'
        emailFrom = 'eosplus-dev@arista.com'
    }

    stages {
        stage ('Run tests for ansible-eos-bridging role') {
            when {
                // Limit runs to any of these conditions
                anyOf {
                    branch 'master'     // master branch
                    branch 'PR-*'       // pull requests
                }
            }
            steps {
                // Grab the revision hash and pass it to the test build
                sh 'git rev-parse HEAD > revision'
                build job: 'Ansible-Role-Test-Starter',
                      parameters: [
                          string(name: 'ROLE_NAME', value: 'ansible-eos-bridging'),
                          string(name: 'REVISION', value: readFile('revision'))
                      ]
            }
            post {
                // Cleanup and notifications
                failure {
                    // Send an email with a link to logs on failure
                    mail to: env.emailTo,
                        from: env.emailFrom,
                        subject: "${env.projectName} ${env.JOB_NAME} (${env.BUILD_NUMBER}) build failed",
                        body: "${env.JOB_NAME} (${env.BUILD_NUMBER}) ${env.projectName} build error " +
                            "is here: ${env.BUILD_URL}\nStarted by ${env.BUILD_CAUSE}"
                }
                success {
                    // Send an email notification on success
                    mail to: env.emailTo,
                        from: env.emailFrom,
                        subject: "${env.projectName} ${env.JOB_NAME} (${env.BUILD_NUMBER}) build successful",
                        body: "${env.JOB_NAME} (${env.BUILD_NUMBER}) ${env.projectName} build successful\n" +
                            "Started by ${env.BUILD_CAUSE}\n" +
                            "${env.BUILD_URL}"
                }
            }
        }
    }
}
