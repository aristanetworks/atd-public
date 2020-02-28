FROM python:3.8.1

ARG UID=1000

RUN useradd -m -u $UID arista

RUN pip install ruamel.yaml 

WORKDIR /home/arista

COPY login.py /usr/local/bin

RUN chmod +x /usr/local/bin/login.py

RUN chown -R arista:arista .

USER arista

ENTRYPOINT [ "login.py" ]