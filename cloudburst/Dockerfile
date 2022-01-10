FROM python:3.10.1-slim-bullseye

RUN apt-get update && \
    apt-get install -y p7zip-full bash

RUN pip3 install --upgrade boto3 jsonschema

COPY scripts /opt/cloudburst
RUN mkdir /work
WORKDIR /work

ENTRYPOINT ["python3", "/opt/cloudburst/fw_entrypoint.py"]
