FROM codercom/code-server:4.7.0

RUN sudo apt update && \
    sudo apt install -y python3 git openssh-server vim nano less rsync man-db jq python3-pip wget zsh sshpass libvirt-clients

RUN sudo pip3 install --upgrade pip

RUN sudo pip3 install pyeapi jsonrpclib-pelix shyaml

RUN sudo pip3 install "ansible-core>=2.12.7,<2.13.0"

# Install arista.avd, community.general and ansible.posix ansible-galaxy collections, Use this for version control of AVD topologies
RUN ansible-galaxy collection install arista.avd:==3.6.0

RUN ansible-galaxy collection install arista.cvp:==3.4.0 --upgrade

RUN ansible-galaxy collection install community.general --upgrade

RUN ansible-galaxy collection install ansible.posix --upgrade

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/v3.6.0/ansible_collections/arista/avd/requirements.txt

RUN sudo pip3 install -r requirements.txt

# Install Code extensions
COPY src/vs-extensions.txt /home/coder/

RUN while IFS= read -r line; do code-server --install-extension $line; done < /home/coder/vs-extensions.txt

COPY src/.gitconfig /home/coder/

RUN wget --quiet https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true \
    && echo 'plugins=(ansible common-aliases safe-paste git jsontools history git-extras)' >> $HOME/.zshrc \
    # redirect to &>/dev/null is required to silence `agent pid XXXX` message from ssh-agent
    && echo 'eval `ssh-agent -s` &>/dev/null' >> $HOME/.zshrc \
    && echo 'export TERM=xterm' >>  $HOME/.zshrc

RUN sudo usermod --shell /bin/zsh coder

RUN sudo chown -R coder:coder /home/coder

VOLUME /home/coder/project

ENV SHELL /bin/zsh
