FROM python:3.8.1

RUN pip install rcvpapi \
    ruamel.yaml

WORKDIR /root

COPY sslUpdater.py .

CMD ["python", "sslUpdater.py"]