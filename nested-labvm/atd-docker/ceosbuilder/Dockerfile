FROM python:3.8.1

RUN pip install ruamel.yaml

WORKDIR /usr/local/bin

COPY ceosbuilder.py .

CMD ["python", "ceosbuilder.py", "-t"]