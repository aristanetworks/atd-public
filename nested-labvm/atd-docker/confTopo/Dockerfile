FROM python:3.8


RUN pip install --upgrade pip

RUN pip install tornado requests ruamel.yaml cvprac rcvpapi

RUN mkdir -p /opt/topo/html

WORKDIR /root

COPY ./src/ConfigureTopology/* /usr/local/bin/ConfigureTopology/

COPY ./src/confTopo.py /usr/local/bin/confTopo

RUN chmod +x /usr/local/bin/confTopo

EXPOSE 50010

CMD ["confTopo"]

