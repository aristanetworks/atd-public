FROM python:3.8.1

RUN pip install rcvpapi \
    cvprac \
    Pyyaml

WORKDIR /root

COPY gitConfigletSync.py .

CMD ["python", "gitConfigletSync.py"]