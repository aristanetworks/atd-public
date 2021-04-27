FROM python:3.8

RUN adduser --disabled-password --home /home/arista --gecos "" arista

RUN curl -SsL https://github.com/boxboat/fixuid/releases/download/v0.5/fixuid-0.5-linux-amd64.tar.gz | tar -C /usr/local/bin -xzf - && \
    chown root:root /usr/local/bin/fixuid && \
    chmod 4755 /usr/local/bin/fixuid && \
    mkdir -p /etc/fixuid && \
    printf "user: arista\ngroup: arista\n" > /etc/fixuid/config.yml

RUN pip install rcvpapi \
    cvprac \
    Pyyaml

WORKDIR /home/arista

COPY src/gitConfigletSync.py .

COPY src/entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/entrypoint.sh

RUN chown -R arista:arista .

USER arista

CMD ["/usr/local/bin/entrypoint.sh"]
