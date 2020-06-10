FROM python:3.8.1-slim

ARG UID=1000

RUN useradd -m -u $UID arista

RUN pip install rcvpapi \
    cvprac \
    Pyyaml

WORKDIR /home/arista

COPY gitConfigletSync.py .

RUN chown -R arista:arista .

USER arista

CMD ["python", "gitConfigletSync.py"]