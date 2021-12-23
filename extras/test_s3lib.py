#!/usr/bin/python3
import sys
sys.path.append("scripts")
import s3lib

s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam00', local_folder = 'test1.tmp', filter = None, threads = 10)

