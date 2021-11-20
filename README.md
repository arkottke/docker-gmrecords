# docker-gmrecords

Create USGS gmprocess docker container. Can be installed with `docker pull arkottke/gmrecords:latest`

# Usage

Using the docker container can be started using `make run`, or with `docker run -it --rm -v $(PWD)/data:/working -t gmrecords /bin/bash`. It is important that the volume have the necessary configuration files. Once in the docker shell, the following commands should be used to download and process an earthquake:
 1. `gmrecords download -e nc73654060`
 2. `gmrecords assemble -e nc73654060`
 3. `gmrecords process -e nc73654060`
 4. `gmrecords sm -e nc73654060`
 5. `gmrecords wm -e nc73654060`

Resulting data is stored in the `/data/nc73654060/workspace.h5` file. More information on the `gmprocess` command line interface is available [here](https://usgs.github.io/groundmotion-processing/contents/tutorials/cli.html).
