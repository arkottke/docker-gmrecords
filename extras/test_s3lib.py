#!/usr/bin/python3
import sys
sys.path.append("scripts")
import s3lib

print('1 file, get by full name, to local directory')
s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam001/Period01.7z', local_path = 'test1.tmp')

print('1 file, get by full name, to local full name')
s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam001/Period01.7z', local_path = 'test1.tmp/Period01.7z')

print('1 file, get by full name, to local rename')
s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam001/Period01.7z', local_path = 'test1.tmp/Period01_file.7z')

print('1 file, get by filter, local path = full name')
s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam001', local_path = 'test2.tmp/Period01.7z', filter='Period01')

print('1 file, get by filter, local path = directory name')
s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam001', local_path = 'test2.tmp/', filter='Period01')

print('16 files, get by full prefix, local path = directory name')
s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam001', local_path = 'test1.tmp')

print('32 files, get by partial prefix, local path = directory name')
s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam00', local_path = 'test1.tmp')

print('32 files, get by partial prefix, local path = directory name')
s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam00', local_path = 'test1.tmp', threads=40)

# use an incomplete prefix to retrieve a single file
# s3lib.get_files(bucket_name = 'test-bruceh', prefix = 'input/Dam001/Period01', local_path = 'test1.tmp', filter = None, threads = 10)
