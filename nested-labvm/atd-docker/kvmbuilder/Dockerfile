FROM python:3.8.1

RUN adduser --disabled-password --home /home/atdadmin --gecos "" atdadmin

RUN curl -SsL https://github.com/boxboat/fixuid/releases/download/v0.5/fixuid-0.5-linux-amd64.tar.gz | tar -C /usr/local/bin -xzf - && \
    chown root:root /usr/local/bin/fixuid && \
    chmod 4755 /usr/local/bin/fixuid && \
    mkdir -p /etc/fixuid && \
    printf "user: atdadmin\ngroup: atdadmin\n" > /etc/fixuid/config.yml

RUN pip install ruamel.yaml psutil

WORKDIR /home/atdadmin

RUN mkdir /home/atdadmin/kvm

COPY src/kvm-topo-builder.py .

COPY src/entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/entrypoint.sh

RUN chown -R atdadmin:atdadmin .

USER atdadmin

CMD ["/usr/local/bin/entrypoint.sh"]
