FROM python:3.8.1

ARG UID=1000

RUN useradd -m -u $UID arista

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

WORKDIR /home/arista

COPY build_labguides.sh .

RUN mkdir -p labguides/src && mkdir -p labguides/web

RUN chown -R arista:arista .

USER arista

CMD ["bash", "build_labguides.sh"]
