# Multistage build from: https://pythonspeed.com/articles/conda-docker-image-size/

FROM continuumio/miniconda3 AS build

RUN conda update --all

COPY environment.yml .
RUN conda env create -f environment.yml

RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n gmprocess -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# Install the host system
# https://github.com/TACC/tacc-containers
FROM tacc/tacc-ubuntu18 AS runtime

RUN apt update && \
    apt upgrade -y && \
    apt install -y locales git texlive texlive-pictures vim && \
    fmtutil-sys --all && \
    locale-gen en_US.UTF-8 && \
    docker-clean

# Downloaded from https://build.opensuse.org/package/binaries/home:tange/parallel/Debian_Testing
COPY parallel_20210522_all.deb /tmp/
RUN yes | dpkg -i /tmp/parallel_20210522_all.deb && \
    rm /tmp/parallel_20210522_all.deb && \
    docker-clean

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

# Need to use bash for source
SHELL ["/bin/bash", "-c"]

# # Need to install as a local link for the setuptools-scm to find the version
COPY gmprocess /app/gmprocess
RUN source /venv/bin/activate && \
    cd /app/gmprocess && \
    pip install -e . && \
    docker-clean

RUN echo "Test gmrecords"
RUN source /venv/bin/activate && gmrecords -v

#COPY tools/docker/entrypoint.sh ./
#ENTRYPOINT ["./entrypoint.sh"]
CMD ["/bin/bash", "--login"]
