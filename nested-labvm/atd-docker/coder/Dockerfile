FROM codercom/code-server:3.7.3

RUN sudo apt update

RUN sudo apt install -y python3 git openssh-server vim nano less rsync man-db jq python3-pip wget

RUN sudo pip3 install ansible rcvpapi cvprac pyeapi jsonrpclib jsonrpclib-pelix paramiko

RUN sudo pip3 install --upgrade pip

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/development/requirements.txt

RUN sudo pip3 install -r requirements.txt

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/development/requirements-dev.txt

RUN sudo pip3 install -r requirements-dev.txt
