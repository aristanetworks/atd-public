FROM golang:1.16.6 as builder

ENV GO111MODULE=on

WORKDIR /app

COPY src/confTopo/go.mod ./

COPY src/confTopo/go.sum ./

RUN go mod download

COPY src/confTopo/main.go ./

RUN go build -o /confTopo

CMD ["/confTopo"]

FROM debian:buster

ARG APP_HOME=/opt/confTopo


WORKDIR ${APP_HOME}

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt

COPY --from=builder /confTopo ${APP_HOME}/confTopo

EXPOSE 50010

ENTRYPOINT ["./confTopo"]