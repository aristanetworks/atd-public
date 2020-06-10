FROM python:3.8.1-slim

ARG UID=1000

RUN useradd -m -u $UID arista

RUN pip install rcvpapi \
    ruamel.yaml

WORKDIR /home/arista

COPY sslUpdater.py .

RUN chown -R arista:arista .

USER arista

CMD ["python", "sslUpdater.py"]