FROM python:3.8.1

ARG UID=1000

RUN useradd -m -u $UID atdadmin

RUN pip install ruamel.yaml psutil

WORKDIR /home/atdadmin

RUN mkdir /home/atdadmin/kvm

COPY kvm-topo-builder.py .

COPY kvm_xml/. .

RUN chown -R atdadmin:atdadmin .

USER atdadmin

CMD ["python", "kvm-topo-builder.py"]