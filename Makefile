PWD = $(shell pwd)

build: 
	docker build . -t gmrecords

run: build
	docker run -it --rm -v $(PWD)/data:/working -t gmrecords /bin/bash

push: build
	docker tag gmrecords arkottke/gmrecords
	docker push arkottke/gmrecords:latest
