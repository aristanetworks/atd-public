FROM python:3.8.1

ENV APPNAME=uptime.py

RUN pip install tornado

COPY ./src/$APPNAME /usr/local/bin/

RUN chmod +x /usr/local/bin/$APPNAME

EXPOSE 50010

CMD ["$APPNAME"]
