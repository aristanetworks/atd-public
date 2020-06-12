FROM python:3.8.1


RUN pip install --upgrade pip

RUN pip install tornado requests ruamel.yaml \
    sphinx \
    sphinx-bootstrap-theme \
    shyaml

RUN apt update

RUN apt install -y \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    latexmk

RUN mkdir -p /opt/topo/html

RUN mkdir -p /root/labguides

WORKDIR /root

COPY ./src/html /opt/topo/html/

COPY ./src/start_frontend.sh /usr/local/bin/start_frontend

COPY ./src/uilanding.py /usr/local/bin/uilanding

RUN chmod +x /usr/local/bin/start_frontend

RUN chmod +x /usr/local/bin/uilanding

EXPOSE 80

CMD ["start_frontend"]

