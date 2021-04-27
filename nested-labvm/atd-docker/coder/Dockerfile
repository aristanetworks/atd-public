FROM codercom/code-server:3.9.3

RUN sudo apt update && \
    sudo apt install -y python3 git openssh-server vim nano less rsync man-db jq python3-pip wget zsh sshpass libvirt-clients

RUN sudo pip3 install --upgrade pip

RUN sudo pip3 install pyeapi jsonrpclib-pelix

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/ansible_collections/arista/avd/requirements.txt

RUN sudo pip3 install -r requirements.txt

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/ansible_collections/arista/avd/requirements-dev.txt

RUN sudo pip3 install -r requirements-dev.txt

COPY src/.gitconfig /home/coder/

RUN wget --quiet https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true \
    && echo 'plugins=(ansible common-aliases safe-paste git jsontools history git-extras)' >> $HOME/.zshrc \
    && echo 'eval `ssh-agent -s`' >> $HOME/.zshrc \
    && echo 'export TERM=xterm' >>  $HOME/.zshrc

RUN sudo usermod --shell /bin/zsh coder

RUN sudo chown -R coder:coder /home/coder

VOLUME /home/coder/project

ENV SHELL /bin/zsh