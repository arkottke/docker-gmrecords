# Multistage build from: https://pythonspeed.com/articles/conda-docker-image-size/

FROM continuumio/miniconda3 AS build

RUN conda update --all

RUN apt-get update -q && \
  apt-get -y install git gcc sed && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN cd /root && \
  git clone --depth 1 https://github.com/arkottke/groundmotion-processing gmprocess && \
  cd gmprocess && \
# Need to install an non-editable version. Install script typically just links
  sed -i 's/pip install -e ./pip install ./' install.sh && \
  bash install.sh

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda install -c conda-forge conda-pack && \
  conda-pack -n gmprocess -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# Install the host system
FROM debian:bookworm-slim AS runtime

RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y p7zip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

# Need to use bash for source
RUN echo "source /venv/bin/activate" >> /root/.bashrc
SHELL ["/bin/bash", "-l", "-c"]

RUN pip install boto3 jsonschema
RUN mkdir /working
WORKDIR /working

# Copy the cloudburst framework and the data directory
COPY cloudburst/scripts /opt/cloudburst
COPY data /working

ENV FONTCONFIG_PATH=/etc/fonts

ENTRYPOINT source /venv/bin/activate && python3 /opt/cloudburst/fw_entrypoint.py
