FROM python:3.8

RUN pip install --upgrade pip

RUN pip install requests ruamel.yaml

WORKDIR /root

COPY ./src/atdMonitor.py /usr/local/bin/atdMonitor

RUN chmod +x /usr/local/bin/atdMonitor

CMD ["atdMonitor"]

