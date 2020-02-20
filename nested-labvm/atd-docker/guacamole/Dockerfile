FROM guacamole/guacamole:1.1.0

RUN apt update && apt install -y zip
COPY src/user-mapping.xml /root/.guacamole/
COPY src/start.sh /opt/guacamole/bin/
RUN chmod +x /opt/guacamole/bin/start.sh

WORKDIR /root/.guacamole/extensions
COPY src/src-aristalogin .
RUN zip -r aristalogin.jar * 

WORKDIR /opt/guacamole
