FROM jenkins/jenkins:lts-centos

USER root

RUN yum install -y epel-release

RUN yum install -y sshpass ansible

USER jenkins

ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dorg.apache.commons.jelly.tags.fmt.timeZone=America/Chicago -Dhudson.model.UsageStatistics.disabled=true"

RUN /usr/local/bin/install-plugins.sh ansible
