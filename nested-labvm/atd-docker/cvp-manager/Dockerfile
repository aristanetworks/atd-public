FROM python:3.13

RUN pip install --upgrade pip && \
    pip install requests \
               ruamel.yaml \
               paramiko \
               scp \
               pyyaml

RUN adduser --disabled-password --gecos "" arista

WORKDIR /home/arista

COPY src/ .

RUN chmod +x entrypoint.sh

USER arista

ENTRYPOINT ["/home/arista/entrypoint.sh"]
