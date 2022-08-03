FROM golang:1.16.6

RUN apt update && apt install -y sudo vim git zip cloc zsh zsh-syntax-highlighting zsh-doc less man

ARG USERNAME=atddev
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG CONTAINERWS="/workspaces"

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME


USER $USERNAME

RUN go get -v golang.org/x/tools/gopls github.com/gorilla/mux

# Install oh-my-zsh

RUN cd ~/ && wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh && sh install.sh --unattended && rm install.sh

# Persist session history

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=$CONTAINERWS/.history" \
    && echo $SNIPPET >> "/home/$USERNAME/.zshrc"


