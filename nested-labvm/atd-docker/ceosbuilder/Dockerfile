FROM python:3.8.1

ARG UID=1000

RUN useradd -m -u $UID atdadmin

RUN pip install ruamel.yaml

WORKDIR /home/atdadmin

COPY ceosbuilder.py .

RUN chown -R atdadmin:atdadmin .

USER atdadmin

CMD ["python", "ceosbuilder.py", "-t"]