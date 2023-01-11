FROM codercom/code-server:4.9.1

RUN sudo apt update && \
    sudo apt-get install -y python3 python3-venv git openssh-server vim nano less rsync man-db jq python3-pip wget zsh sshpass libvirt-clients && \
    sudo apt-get clean  && \
    sudo rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip --no-cache-dir

ENV VIRTUAL_ENV=/home/coder/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install arista.avd, community.general and ansible.posix ansible-galaxy collections, Use this for version control of AVD topologies
RUN pip3 install pyeapi jsonrpclib-pelix shyaml --no-cache-dir && \
    pip3 install "ansible-core>=2.12.7,<2.13.0" --no-cache-dir && \
    ansible-galaxy collection install arista.avd:=3.8.0-dev2 && \
    ansible-galaxy collection install arista.cvp && \
    ansible-galaxy collection install community.general --upgrade && \
    ansible-galaxy collection install ansible.posix --upgrade && \
    wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/v3.7.0/ansible_collections/arista/avd/requirements.txt && \
    pip3 install -r requirements.txt --no-cache-dir

# Install Code extensions
COPY src/vs-extensions.txt /home/coder/

RUN while IFS= read -r line; do code-server --install-extension $line; done < /home/coder/vs-extensions.txt

COPY src/.gitconfig /home/coder/

RUN wget --quiet https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true \
    && echo 'plugins=(ansible common-aliases safe-paste git jsontools history git-extras)' >> $HOME/.zshrc \
    && echo 'eval `ssh-agent -s`' >> $HOME/.zshrc \
    && echo 'export TERM=xterm' >>  $HOME/.zshrc

RUN sudo usermod --shell /bin/zsh coder

WORKDIR /home/coder/project

RUN sudo chown -R coder:coder /home/coder/project

ENV SHELL /bin/zsh
