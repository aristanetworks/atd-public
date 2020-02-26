FROM python:3.8.1

ARG UID=1000

RUN useradd -m -u $UID arista

RUN pip install rcvpapi \
    cvprac \
    Pyyaml

USER arista

WORKDIR /home/arista

COPY gitConfigletSync.py .

CMD ["python", "gitConfigletSync.py"]