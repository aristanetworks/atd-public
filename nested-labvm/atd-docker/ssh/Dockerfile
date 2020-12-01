FROM node:8.6

ARG TAG=0.3.0

WORKDIR /opt

RUN git clone https://github.com/billchurch/webssh2.git

WORKDIR /opt/webssh2

RUN git checkout $TAG

WORKDIR /opt/webssh2/app

RUN npm install --production

EXPOSE 2222

CMD npm run start
