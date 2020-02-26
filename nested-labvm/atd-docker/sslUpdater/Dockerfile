FROM python:3.8.1

ARG UID=1000

RUN useradd -u $UID arista

RUN pip install rcvpapi \
    ruamel.yaml

USER arista

WORKDIR /home/arista

COPY sslUpdater.py .

CMD ["python", "sslUpdater.py"]