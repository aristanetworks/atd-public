FROM jenkins/jenkins:2.176.2
# Current LTS version is 2.176.2

ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dorg.apache.commons.jelly.tags.fmt.timeZone=America/Chicago -Dhudson.model.UsageStatistics.disabled=true"

COPY src/users.groovy /usr/share/jenkins/ref/init.groovy.d/users.groovy
COPY src/plugins.txt /usr/share/jenkins/ref/plugins.txt

RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt
