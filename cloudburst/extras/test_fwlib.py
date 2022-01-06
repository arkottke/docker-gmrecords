#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com
# tests fwlib. These are manual tests, i.e. no conditions are checked, but results must
# be observed. In future we will use a known test data set and add verification code
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.joinpath("scripts")))
import fwlib
import json

def test_store_sub(bucket:str):
    store = [{
            "name": "store-output",
            "bucket": bucket,
            "source": "./output.tmp/Site00001/",
            "dest": "output.tmp/Site00001/",
            "compressSubDirectories": True
        }]

    # TODO: does not yet work, debug further
    fwlib.process_store(store, 'default')

test_store_sub('test-bh22')
