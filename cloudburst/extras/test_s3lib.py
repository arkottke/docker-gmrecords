#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com
# tests s3lib. These are manual tests, i.e. no conditions are checked, but results must
# be observed. In future we will use a known test data set and add verification code
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.joinpath("scripts")))

import s3lib

def test_get_files(bucket:str):
    print('1 file, get by full name, to local directory')
    s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam001/Period01.7z', local_path = 'test1.tmp')

    print('1 file, get by full name, to local full name')
    s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam001/Period01.7z', local_path = 'test1.tmp/Period01.7z')

    print('1 file, get by full name, to local rename')
    s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam001/Period01.7z', local_path = 'test1.tmp/Period01_file.7z')

    print('1 file, get by filter, local path = full name')
    s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam001', local_path = 'test2.tmp/Period01.7z', filter='Period01')

    print('1 file, get by filter, local path = directory name')
    s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam001', local_path = 'test2.tmp/', filter='Period01')

    print('16 files, get by full prefix, local path = directory name')
    s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam001', local_path = 'test1.tmp')

    print('32 files, get by partial prefix, local path = directory name')
    s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam00', local_path = 'test1.tmp')

    print('32 files, get by partial prefix, local path = directory name')
    s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam00', local_path = 'test1.tmp', threads=40)


def test_put_files(bucket:str):
    print('upload multiple_files, multithreaded')
    s3lib.put_files(bucket_name = bucket, prefix = 'test1_out', local_folder = 'test1.tmp', threads=40)

test_put_files('test-bruceh')

# use an incomplete prefix to retrieve a single file
# s3lib.get_files(bucket_name = bucket, prefix = 'input/Dam001/Period01', local_path = 'test1.tmp', filter = None, threads = 10)
