FROM nginx:latest

COPY src/atd.conf /etc/nginx/conf.d/

COPY src/atd-certs.sh /docker-entrypoint.d/

RUN mkdir /etc/nginx/certs

RUN chmod +x /docker-entrypoint.d/atd-certs.sh

EXPOSE 80 443