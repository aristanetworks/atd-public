FROM python:3.10

RUN apt update && apt upgrade -y

RUN apt install -y vim uwsgi-plugin-python3 memcached

RUN pip install uwsgi Flask pymemcache

COPY ./src/API_Server /opt

WORKDIR /opt

RUN chmod +x start_API.sh

CMD ["/opt/start_API.sh"]
