FROM python:3.8

ARG UID=1000

RUN useradd -s /usr/local/bin/login.py -m -u $UID arista

RUN usermod -aG root arista

RUN apt update

RUN apt install -y openssh-server vim sudo screen

RUN pip install ruamel.yaml rcvpapi cvprac pyaml paramiko scp urllib3

RUN mkdir /var/run/sshd

RUN sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"

RUN echo "export VISIBLE=now" >> /etc/profile

RUN echo 'arista ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /home/arista

RUN mkdir .ssh

COPY src/login.py /usr/local/bin

RUN chmod +x /usr/local/bin/login.py

RUN mkdir /usr/local/bin/ConfigureTopology

COPY src/ConfigureTopology/* /usr/local/bin/ConfigureTopology/

RUN echo 'login.py' >> .profile

RUN chown -R arista:arista .

EXPOSE 22

USER arista

CMD ["sudo", "/usr/sbin/sshd", "-D"]