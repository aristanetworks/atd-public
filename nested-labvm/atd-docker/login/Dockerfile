FROM python:3.9

RUN adduser --disabled-password --shell /usr/local/bin/login.py --home /home/arista --gecos "" arista

RUN curl -SsL https://github.com/boxboat/fixuid/releases/download/v0.5/fixuid-0.5-linux-amd64.tar.gz | tar -C /usr/local/bin -xzf - && \
    chown root:root /usr/local/bin/fixuid && \
    chmod 4755 /usr/local/bin/fixuid && \
    mkdir -p /etc/fixuid && \
    printf "user: arista\ngroup: arista\n" > /etc/fixuid/config.yml

RUN apt update && \
    apt install -y openssh-server vim sudo screen libvirt-clients libvirt-dev

RUN pip install ruamel.yaml rcvpapi cvprac pyaml paramiko scp urllib3 libvirt-python jsonrpclib

RUN mkdir /var/run/sshd

RUN sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"

RUN echo "export VISIBLE=now" >> /etc/profile

RUN echo 'arista ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /home/arista

RUN mkdir .ssh

COPY src/login.py /usr/local/bin

COPY src/resetVMs.py /usr/local/bin

COPY src/uploadExam.py /usr/local/bin

COPY src/saveRunning.py /usr/local/bin

RUN chmod +x /usr/local/bin/login.py

RUN chmod +x /usr/local/bin/resetVMs.py

RUN chmod +x /usr/local/bin/uploadExam.py

RUN chmod +x /usr/local/bin/saveRunning.py

RUN mkdir /usr/local/bin/ConfigureTopology

COPY src/ConfigureTopology/* /usr/local/bin/ConfigureTopology/

RUN echo 'login.py' >> .profile

RUN chown -R arista:arista .

RUN pip install --upgrade rcvpapi

COPY src/entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 22

USER arista

CMD ["/usr/local/bin/entrypoint.sh"]
