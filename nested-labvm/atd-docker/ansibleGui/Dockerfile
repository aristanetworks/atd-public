FROM centos:7 as cbuilder

ENV container docker

RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;

VOLUME [ "/sys/fs/cgroup" ]

CMD ["/usr/sbin/init"]

FROM cbuilder

RUN sed -i "s/tsflags/#tsflags/g" /etc/yum.conf

RUN yum update -y

ARG UID=1000

RUN useradd -m -u $UID arista 

RUN mkdir scripts

COPY scripts/. scripts/

# Install Desktop 

RUN yum install -y epel-release

RUN yum groupinstall -y xfce

# Section for xRDP

RUN bash scripts/install_xrdp.sh

# Install Chrome

RUN bash scripts/install_chrome.sh

COPY chrome/policy.json /etc/opt/chrome/policies/managed/

# Install VS Code

RUN bash scripts/install_code.sh

# Install Lab specifics

RUN yum install -y python3 git openssh-server vim nano less rsync sudo man man-pages man-pages-overrides jq

RUN pip3 install ansible rcvpapi cvprac pyeapi jsonrpclib jsonrpclib-pelix paramiko

# File setups

WORKDIR /home/arista

COPY arista/.Xclients .Xclients

RUN chmod a+x .Xclients

RUN mkdir -p .local/share/keyrings

COPY arista/local/. .local/share/keyrings/

COPY arista/Desktop/. Desktop/

COPY arista/home/. /home/arista/

RUN mkdir -p Desktop/labfiles/lab4 \
    Desktop/labfiles/lab6/repo \
    Desktop/labfiles/lab6/lab \
    Desktop/labfiles/lab6/lab/roles \
    Desktop/labfiles/lab6/lab/group_vars

COPY arista/labfiles/. Desktop/labfiles/lab4/

RUN chown -R arista:arista .

RUN chmod -R +x Desktop/*.desktop

RUN echo "@rista123" | passwd --stdin "root"

RUN echo "arista" | passwd --stdin "arista"

RUN sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

RUN echo "export VISIBLE=now" >> /etc/profile

RUN echo 'arista ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN usermod -aG wheel arista

RUN pip3 install --upgrade pip

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/development/requirements.txt

RUN pip3 install -r requirements.txt

RUN wget --quiet https://raw.githubusercontent.com/aristanetworks/ansible-avd/devel/development/requirements-dev.txt

RUN pip3 install -r requirements-dev.txt

EXPOSE 3389 22

CMD ["/usr/sbin/init"]
