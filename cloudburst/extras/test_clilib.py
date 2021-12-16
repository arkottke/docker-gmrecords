#!/usr/bin/python3
import os
import clilib

def validateSchema():
    import json, jsonschema
    my_inst = json.loads('tasks.json') #or however else you end up with a dict of the schema
    my_schema = json.loads('tasks.schema.json') #or however else you end up with a dict of the schema
    jsonschema.validate(my_inst, my_schema)

def testCompress():
    clilib.compress_inputs()

def testUploadCode():
    clilib.upload_code('haz-test.us-west-1')

def testUploadInputs():
    clilib.uploadInputs('haz-test.us-west-1', sitesOnly=True)

def testStartJobs():
    clilib.startJobs(bucket_name='haz-test.us-west-1', siteList='00001-00009',test=True)

def testGetOutputs():
    # clilib.unzipOutputs(localPath='./InputData.tmp', outputDir='./outputs.tmp/foo', test=True)
#    clilib.getOutputs(bucket_name='haz-test.us-west-1', getFaultsOnly=True, test=True, clean = True, downloadOnly=True)
    clilib.getOutputs(bucket_name='haz-test.us-west-1', clean = True, downloadOnly=True)

def testExpandOutputs():
    # clilib.unzipOutputs(localPath='./InputData.tmp', outputDir='./outputs.tmp/foo', test=True)
    clilib.expand_outputs()

# testUploadCode()
#testUploadInputs()
# testExpandOutputs()
#testGetOutputs()
validateSchema()
