FROM python:3.8.1

ARG UID=1000

RUN useradd -m -u $UID arista

RUN pip install rcvpapi \
    ruamel.yaml

USER arista

RUN mkdir -p /home/arista/CVP_DATA

WORKDIR /home/arista

COPY cvpUpdater.py .

VOLUME ["/home/arista/CVP_DATA"]

CMD ["python", "cvpUpdater.py"]
