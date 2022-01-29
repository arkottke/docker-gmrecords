# Multistage build from: https://pythonspeed.com/articles/conda-docker-image-size/

FROM debian:testing

# Install required packages
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
        cython3 \
        gcc \
        git \
        libhdf5-dev \
        libomp-dev \
        p7zip-full \
        python3-asgiref \
        python3-boto3 \
        python3-bs4 \
        python3-cartopy \
        python3-certifi \
        python3-configobj \
        python3-cycler \
        python3-dask \
        python3-dateutil \
        python3-decorator \
        python3-defusedxml \
        python3-dev \
        python3-dill \
        python3-django \
        python3-docutils \
        python3-fiona \
        python3-folium \
        python3-future \
        python3-gdal \
        python3-h5py \
        python3-idna \
        python3-jsonschema \
        python3-kiwisolver \
        python3-lxml \
        python3-matplotlib \
        python3-numpy \
        python3-openpyxl \
        python3-pandas \
        python3-pbr \
        python3-pip \
        python3-prov \
        python3-psutil \
        python3-pyparsing \
        python3-pyproj \
        python3-pyshp \
        python3-rasterio \
        python3-requests \
        python3-ruamel.yaml \
        python3-schema \
        python3-scipy \
        python3-setproctitle \
        python3-setuptools \
        python3-setuptools-scm \
        python3-shapely \
        python3-six \
        python3-sqlalchemy \
        python3-sqlparse \
        python3-statsmodels \
        python3-toml \
        python3-urllib3 \
        python3-wheel \
        python3-yapf \
	; \
	rm -rf /var/lib/apt/lists/*

ENV LIBRARY_PATH=/usr/local/lib:/usr/lib/llvm-13/lib
ENV FONTCONFIG_PATH=/etc/fonts

# Install dependencies. Here we prevent groundmotion-processing from looking for dependencies during the installation.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    pip install --no-cache-dir --no-deps git+git://github.com/usgs/groundmotion-processing@master#egg=gmprocess

# Import matplotlib the first time to build the font cache.
RUN MPLBACKEND=Agg python3 -c "import matplotlib.pyplot"

RUN gmrecords -v

RUN mkdir -p /working/data
WORKDIR /working

# Copy the cloudburst framework and helper script
COPY cloudburst/scripts /opt/cloudburst
COPY gmrecords_helper.sh /working

ENTRYPOINT python3 /opt/cloudburst/fw_entrypoint.py
