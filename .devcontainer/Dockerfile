FROM python:3.8.1

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

RUN pip install --upgrade pip
RUN pip install dotbot docutils rstcheck sphinx sphinx-bootstrap-theme sphinx-autobuild rcvpapi ruamel.yaml Pyyaml lxml jsonrpclib ansible cvprac pyeapi pylint tornado apscheduler pymongo 

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0

RUN apt-add-repository https://cli.github.com/packages

RUN apt update && apt install -y gh

USER $USERNAME
