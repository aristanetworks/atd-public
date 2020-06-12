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

RUN mkdir -p /root/labguides/web

WORKDIR /root

COPY ./src/build_labguides.sh .

COPY ./src/labguides.py .

RUN chmod +x labguides.py && chmod +x build_labguides.sh

EXPOSE 80

CMD ["bash", "build_labguides.sh"]
