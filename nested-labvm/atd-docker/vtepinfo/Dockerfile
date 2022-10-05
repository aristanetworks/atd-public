FROM python:3.10

RUN pip install ruamel.yaml requests

COPY ./src/vtepinfo.py /usr/local/bin/

RUN chmod +x /usr/local/bin/vtepinfo.py

CMD ["vtepinfo.py"]
