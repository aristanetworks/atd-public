FROM python:3.8.1

RUN pip install ruamel.yaml

WORKDIR /root

RUN mkdir /root/kvm

COPY kvm-topo-builder.py .

COPY kvm_xml/. .

CMD ["python", "kvm-topo-builder.py"]