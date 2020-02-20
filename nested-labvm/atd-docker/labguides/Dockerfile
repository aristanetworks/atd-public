FROM python:3.8.1

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

WORKDIR /root

COPY build_labguides.sh .

RUN mkdir -p labguides/src && mkdir -p labguides/web

CMD ["bash", "build_labguides.sh"]
