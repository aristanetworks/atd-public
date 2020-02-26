FROM python:3.8.1

ARG UID=1000

RUN useradd -u $UID arista

RUN pip install \
    sphinx \
    sphinx-bootstrap-theme \
    shyaml

RUN apt update

RUN apt install -y \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    latexmk

USER arista

WORKDIR /home/arista

COPY build_labguides.sh .

RUN mkdir -p labguides/src && mkdir -p labguides/web

CMD ["bash", "build_labguides.sh"]
