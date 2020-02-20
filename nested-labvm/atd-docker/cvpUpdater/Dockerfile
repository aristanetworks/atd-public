FROM python:3.8.1

RUN pip install rcvpapi \
    ruamel.yaml

RUN mkdir -p /root/CVP

WORKDIR /root

COPY cvpUpdater.py .

VOLUME ['/root/CVP']

CMD ["python", "cvpUpdater.py"]
