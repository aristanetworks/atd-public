FROM python:3.13

RUN pip install --upgrade pip && \
    pip install cloudvision \
               fastapi \
               "uvicorn[standard]" \
               sse-starlette \
               grpcio \
               grpclib \
               requests \
               ruamel.yaml

WORKDIR /app

COPY src/ .

RUN chmod +x entrypoint.sh

EXPOSE 8880

ENTRYPOINT ["/app/entrypoint.sh"]
