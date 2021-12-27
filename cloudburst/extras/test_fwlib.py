#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com
# tests fwlib. These are manual tests, i.e. no conditions are checked, but results must
# be observed. In future we will use a known test data set and add verification code
import sys
sys.path.append("scripts")
import fwlib
import json

def test_store_multiple(bucket:str):
    store = [{
            "name" : "store-output",
            "bucket" : bucket,
            "source" : "./test1/",
            "dest" : "test1_out/",
            "compress" : False
        }]
    # TODO: does not yet work, debug further
    fwlib.process_store(store, 'default')

test_store_multiple('test-bruceh')
