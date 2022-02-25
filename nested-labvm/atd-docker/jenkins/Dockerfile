FROM jenkins/jenkins:lts-jdk11

USER root

RUN apt update

RUN apt install -y sshpass ansible

USER jenkins

COPY src/groovy/* /usr/share/jenkins/ref/init.groovy.d/

ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dorg.apache.commons.jelly.tags.fmt.timeZone=America/Chicago -Dhudson.model.UsageStatistics.disabled=true"

RUN jenkins-plugin-cli --plugins ansible git

USER root

RUN ansible-galaxy collection install arista.eos -p /usr/share/ansible/collections

USER jenkins
