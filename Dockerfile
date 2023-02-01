FROM python:3.10-bullseye

# Install required packages
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
        hdf5-tools \
        p7zip-full \
        vim \
        wget \
	; \
	rm -rf /var/lib/apt/lists/*

ENV LIBRARY_PATH=/usr/local/lib:/usr/lib/llvm-13/lib
ENV FONTCONFIG_PATH=/etc/fonts

# Install a miminum tex environment
# https://yihui.org/tinytex/
ENV PATH="/root/bin:${PATH}"
RUN wget -qO- "https://yihui.org/tinytex/install-bin-unix.sh" | sh && \
    tlmgr install extsizes pgf grffile sansmathfonts babel-english fancyhdr

# Use pip to install gmprocess
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade gmprocess boto3 jsonschema

# Import matplotlib the first time to build the font cache.
RUN MPLBACKEND=Agg python3 -c "import matplotlib.pyplot"

RUN gmrecords -v

RUN mkdir -p /working/data
WORKDIR /working

# Copy the cloudburst framework and helper script
COPY cloudburst/scripts /opt/cloudburst

COPY clean_workspace.py /working
COPY gmrecords_helper.sh /working

ENTRYPOINT python /opt/cloudburst/fw_entrypoint.py
