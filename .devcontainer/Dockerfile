FROM python:3.11

RUN apt update && apt install -y sudo \
    vim \
    git \
    zip \
    cloc \
    lastpass-cli \
    dnsutils \
    zsh \
    zsh-syntax-highlighting \
    zsh-doc \
    less \
    liquidprompt \
    software-properties-common

RUN apt -y dist-upgrade

ARG USERNAME=atddev
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    # && apt-get update \ # redundant
    # && apt-get install -y sudo \ # redundant
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install Google Cloud SDK

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

RUN apt install -y apt-transport-https ca-certificates gnupg

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

RUN apt update && sudo apt install -y google-cloud-sdk

# Install Python Packages
RUN pip install --upgrade pip
RUN pip install dotbot docutils rstcheck sphinx sphinx-bootstrap-theme sphinxcontrib-images sphinx-copybutton sphinx-autobuild rcvpapi ruamel.yaml Pyyaml lxml jsonrpclib ansible cvprac pyeapi pylint tornado apscheduler pymongo paramiko scp

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0

#RUN apt-add-repository https://cli.github.com/packages
RUN type -p curl >/dev/null || sudo apt install curl -y 

RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && sudo apt update \
    && sudo apt install gh -y

USER $USERNAME

# Persist session history

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=$CONTAINERWS/.history" \
    && echo $SNIPPET >> "/home/$USERNAME/.zshrc"
