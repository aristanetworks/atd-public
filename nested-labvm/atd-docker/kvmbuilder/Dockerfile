FROM python:3.8.1

ARG UID=1000

RUN useradd -m -u $UID arista

RUN pip install ruamel.yaml

WORKDIR /home/arista

RUN mkdir /home/arista/kvm

COPY kvm-topo-builder.py .

COPY kvm_xml/. .

RUN chown -R arista:arista .

USER arista

CMD ["python", "kvm-topo-builder.py"]