# Multistage build from: https://pythonspeed.com/articles/conda-docker-image-size/

FROM python:3.9-slim-bullseye

# Install required packages
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
        gcc \
        git \
        libomp-dev \
        libhdf5-dev \
        python3-psutil \
	; \
	rm -rf /var/lib/apt/lists/*

ENV LIBRARY_PATH=/usr/local/lib:/usr/lib/llvm-11/lib
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FONTCONFIG_PATH=/etc/fonts

# Install dependencies:
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip; \
    pip install wheel; \
    pip install --no-cache-dir -r https://raw.githubusercontent.com/gem/oq-engine/master/requirements-py39-linux64.txt; \
    pip install --no-cache-dir --no-deps openquake-engine; \
    pip install --no-cache-dir -r requirements.txt; \
    pip install --no-cache-dir --no-deps git+git://github.com/usgs/groundmotion-processing@master#egg=gmprocess

RUN gmrecords -v

RUN mkdir /working
WORKDIR /working

# Copy the cloudburst framework
COPY cloudburst/scripts /opt/cloudburst

ENTRYPOINT source /venv/bin/activate && python3 /opt/cloudburst/fw_entrypoint.py
