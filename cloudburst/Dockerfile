FROM python:3.10.1-slim-bullseye

RUN pip3 install --upgrade boto3 jsonschema bash

COPY scripts /opt/cloudburst
RUN mkdir /work
WORKDIR /work

ENTRYPOINT ["python3", "/opt/cloudburst/fw_entrypoint.py"]
