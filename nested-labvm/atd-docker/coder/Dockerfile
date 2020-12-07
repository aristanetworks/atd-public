FROM codercom/code-server:3.7.4

RUN sudo apt update

RUN sudo apt install -y python3 git openssh-server vim nano less rsync man-db jq python3-pip wget zsh

RUN sudo pip3 install --upgrade pip

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/development/requirements.txt

RUN sudo pip3 install -r requirements.txt

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/development/requirements-dev.txt

RUN sudo pip3 install -r requirements-dev.txt

RUN mkdir -p /home/coder/project/labfiles/lab4 \
    /home/coder/project/labfiles/lab6/repo \
    /home/coder/project/labfiles/lab6/lab \
    /home/coder/project/labfiles/lab6/lab/roles \
    /home/coder/project/labfiles/lab6/lab/group_vars

COPY src/arista/labfiles/. /home/coder/project/labfiles/lab4/

RUN wget --quiet https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true \
    && echo 'plugins=(ansible common-aliases safe-paste git jsontools history git-extras)' >> $HOME/.zshrc \
    && echo 'eval `ssh-agent -s`' >> $HOME/.zshrc \
    && echo 'export TERM=xterm' >>  $HOME/.zshrc

RUN sudo usermod --shell /bin/zsh coder

VOLUME /home/coder/project/labfiles

ENV SHELL /bin/zsh