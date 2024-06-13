FROM ghcr.io/coder/code-server:4.89.1-bookworm

# set the enviroment correctly first, including path
USER coder
ENV HOME=/home/coder
ENV PATH=$PATH:/home/coder/.local/bin
ENV AVD_VERSION="4.8.0"
ENV CVP_VERSION="3.10.1"
ENV ANTA_VERSION="0.14.0"

RUN sudo apt update && \
    sudo apt install -y python3 git openssh-server vim nano less rsync man-db jq python3-pip wget zsh sshpass libvirt-clients && \
    # clean unnecessary files after install
    sudo rm -rf /var/lib/apt/lists/* && \
    sudo apt-get clean

RUN pip3 config set global.disable-pip-version-check true && \
    pip3 install --user --no-cache-dir pyeapi jsonrpclib-pelix shyaml && \
    pip3 install --user --no-cache-dir "ansible-core>=2.15.0,<2.17.0" --upgrade

# Install arista.avd, community.general and ansible.posix ansible-galaxy collections, Use this for version control of AVD topologies
RUN ansible-galaxy collection install arista.avd:==${AVD_VERSION} && \
    ansible-galaxy collection install arista.cvp:==${CVP_VERSION} --upgrade && \
    ansible-galaxy collection install community.general --upgrade && \
    ansible-galaxy collection install ansible.posix --upgrade

# Install Ansible-AVD collection requirements
RUN pip3 install --user --no-cache-dir "pyavd[ansible]==${AVD_VERSION}" "anta==${ANTA_VERSION}" --upgrade

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

WORKDIR /home/coder/project

RUN sudo chown -R coder:coder /home/coder/project

ENV SHELL /bin/zsh
