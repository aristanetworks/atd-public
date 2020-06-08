FROM python:3.8.1

RUN pip install tornado psutil

COPY ./src/uptime.py /usr/local/bin/

RUN chmod +x /usr/local/bin/uptime.py

EXPOSE 50010

CMD ["uptime.py"]
