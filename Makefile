
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open(sys.argv[1])
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

# Need to use bash for conda
SHELL=/bin/bash

pull: 
	git clone https://github.com/arkottke/groundmotion-processing.git gmprocess

.ONESHELL:
prereqs-env:
	# Export the conda environment
	source /home/albert/miniconda3/bin/activate
	conda activate gmprocess
	conda env export > environment.yml
	conda deactivate

prereqs-parallel: 
	# Download the parallel package
	# $(BROWSER) "https://download.opensuse.org/repositories/home:/tange/xUbuntu_18.10/all/"
	wget https://download.opensuse.org/repositories/home:/tange/xUbuntu_18.10/all/parallel_20210522_all.deb

build: gmprocess/ environment.yml parallel_20210522_all.deb
	docker build . -t gmrecords

run: build
	docker run -it --rm -v /mnt/hdd/dsgmd:/app/working gmrecords /bin/bash

push: build
	docker tag gmrecords arkottke/gmrecords
	docker push arkottke/gmrecords
