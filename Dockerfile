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
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

# Need to use bash for source
RUN echo "source /venv/bin/activate" >> /root/.bashrc
SHELL ["/bin/bash", "-l", "-c"]

RUN mkdir /working
WORKDIR /working

ENV FONTCONFIG_PATH=/etc/fonts
RUN echo "Test gmrecords"
RUN source /venv/bin/activate && gmrecords -v

# ENTRYPOINT source /venv/bin/activate && gmrecords
