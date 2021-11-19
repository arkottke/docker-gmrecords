
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

build: pull prereqs-env
	docker build . -t gmrecords

run: build
	docker run -it --rm -v $(pwd)/data:/working -t gmrecords

push: build
	docker tag gmrecords arkottke/gmrecords
	docker push arkottke/gmrecords
