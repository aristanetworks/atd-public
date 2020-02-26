FROM python:3.8.1

ARG UID=1000

RUN useradd -u $UID arista

RUN pip install ruamel.yaml

USER arista

WORKDIR /home/arista

RUN mkdir /home/arista/kvm

COPY kvm-topo-builder.py .

COPY kvm_xml/. .

CMD ["python", "kvm-topo-builder.py"]