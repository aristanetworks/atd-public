FROM python:3.8

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
RUN pip install dotbot docutils rstcheck sphinx sphinx-bootstrap-theme sphinxcontrib-images sphinx-copybutton sphinx-autobuild rcvpapi ruamel.yaml Pyyaml lxml jsonrpclib ansible cvprac pyeapi pylint tornado apscheduler pymongo 

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0

RUN apt-add-repository https://cli.github.com/packages

RUN apt update && apt install -y gh

# Install GoLang

RUN wget https://golang.org/dl/go1.16.6.linux-amd64.tar.gz

RUN rm -rf /usr/local/go && tar -C /usr/local -xzf go1.16.6.linux-amd64.tar.gz

USER $USERNAME

# Persist session history

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=$CONTAINERWS/.history" \
    && echo $SNIPPET >> "/home/$USERNAME/.zshrc"
    
ENV PATH=$PATH:/usr/local/go/bin

RUN go get -v golang.org/x/tools/gopls github.com/gorilla/mux
