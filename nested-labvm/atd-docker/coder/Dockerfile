FROM codercom/code-server:4.0.1

RUN sudo apt update && \
    sudo apt install -y python3 git openssh-server vim nano less rsync man-db jq python3-pip wget zsh sshpass libvirt-clients

RUN sudo pip3 install --upgrade pip

RUN sudo pip3 install pyeapi jsonrpclib-pelix shyaml

# Install arista.avd, community.general and ansible.posix ansible-galaxy collections with upgrade flag if already exists
RUN ansible-galaxy collection install arista.avd --upgrade

RUN ansible-galaxy collection install community.general --upgrade

RUN ansible-galaxy collection install ansible.posix --upgrade

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/ansible_collections/arista/avd/requirements.txt

RUN sudo pip3 install -r requirements.txt

#Install arista.avd and arista.cvp ansible galaxy collection devel branch - Required until PR #1410 is in latest release branch
RUN ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-avd.git#/ansible_collections/arista/avd/,devel

RUN ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-cvp.git#/ansible_collections/arista/cvp/,devel

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/ansible_collections/arista/avd/requirements-dev.txt

RUN sudo pip3 install -r requirements-dev.txt

# Install arista.avd, community.general and ansible.posix ansible-galaxy collections with upgrade flag if already exists
RUN ansible-galaxy collection install arista.avd --upgrade

RUN ansible-galaxy collection install community.general --upgrade

RUN ansible-galaxy collection install ansible.posix --upgrade

#Install arista.avd and arista.cvp ansible galaxy collection devel branch - Required until PR #1410 is in latest release branch
RUN ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-avd.git#/ansible_collections/arista/avd/,devel

RUN ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-cvp.git#/ansible_collections/arista/cvp/,devel

# Install Code extensions
COPY src/vs-extensions.txt /home/coder/

RUN while IFS= read -r line; do code-server --install-extension $line; done < /home/coder/vs-extensions.txt

COPY src/.gitconfig /home/coder/

RUN wget --quiet https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true \
    && echo 'plugins=(ansible common-aliases safe-paste git jsontools history git-extras)' >> $HOME/.zshrc \
    && echo 'eval `ssh-agent -s`' >> $HOME/.zshrc \
    && echo 'export TERM=xterm' >>  $HOME/.zshrc

RUN sudo usermod --shell /bin/zsh coder

RUN sudo chown -R coder:coder /home/coder

VOLUME /home/coder/project

ENV SHELL /bin/zsh
