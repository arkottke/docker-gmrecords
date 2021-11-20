# docker-gmrecords

Create USGS gmprocess docker container.


# Usage

 #. make run
 #. gmrecords download -e nc73654060
 #. gmrecords assemble -e nc73654060
 #. gmrecords process -e nc73654060
 #. gmrecords sm -e nc73654060
 #. gmrecords wm -e nc73654060

Resulting data is stored in the `/data/nc73654060/workspace.h5` file.

More information on the `gmprocess` command line interface is available (here)[https://usgs.github.io/groundmotion-processing/contents/tutorials/cli.html].
