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

RUN yum update -y

RUN useradd arista 

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

RUN yum install -y python3 git

RUN pip3 install ansible rcvpapi cvprac pyeapi jsonrpclib

# File setups

WORKDIR /home/arista

RUN mkdir -p .local/share/keyrings

COPY arista/.Xclients .Xclients

RUN chmod a+x .Xclients

COPY arista/local/. .local/share/keyrings/

COPY arista/Desktop/. Desktop/

RUN mkdir -p Desktop/labfiles/lab4 \
    Desktop/labfiles/lab6/repo \
    Desktop/labfiles/lab6/lab \
    Desktop/labfiles/lab6/lab/roles \
    Desktop/labfiles/lab6/lab/group_vars

COPY arista/labfiles/. Desktop/labfiles/lab4/

RUN chown -R arista:arista Desktop .local/ .Xclients

RUN chmod -R +x Desktop/*.desktop

RUN echo "arista" | passwd --stdin "arista"

EXPOSE 3389

CMD ["/usr/sbin/init"]
