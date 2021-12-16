#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

import boto3, os, re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path


# Copies a file from S3, providing exception handling and logging
def copy_s3_object(bucket_name, key, local_file):
    print(f"fetching file: s3://{bucket_name}/{key} to {local_file}")
    os.makedirs(os.path.dirname(local_file), exist_ok=True)

    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, key, local_file)
        return 0
    except Exception as err:
        print(f"Error fetching s3://{bucket_name}/{key} to {local_file}: {str(err)}")
        return 213

def list_objects(bucket_name, prefix):
    s3 = boto3.client('s3')
    ar = []
    files = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    for obj in files['Contents']:
        file = obj['Key']
        ar.append(file)
    return ar

def copy_s3_objects(bucket_name, prefix, local_folder):
    print(f"fetching files: s3://{bucket_name}/{prefix} to {local_folder}")
    os.makedirs(local_folder, exist_ok=True)

    s3 = boto3.client('s3')
    try:
        files = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        for obj in files['Contents']:
            file = obj['Key']
            local_file = file.replace(prefix, local_folder)
            s3.download_file(bucket_name, file, local_file)
        return 0
    except Exception as err:
        print("error copying s3://{0}/{1} to {2}: {3}".format(bucket_name, prefix, local_folder, str(err)))
        return 214

# write an object to S3, with error handling
def write_s3_object(bucket_name, key, file):

    print (f"storing {file} to s3://{bucket_name}/{key}")
    s3 = boto3.resource('s3')

    try:
        s3.Bucket(bucket_name).upload_file(Key=key,Filename=file)
        return 0
    except Exception as err:
        print ("error storing {0} to {1}/{2}: {3}".format(file, bucket_name, key, str(err)))
        return 215

# delegate to download a single file, used by multi-threader in getFiles()
def put_file(bucket: str, client: boto3.client, local_file: Path, key: str):
    """
    Download a single file from S3
    Args:
        bucket (str): S3 bucket where images are hosted
        output (str): Dir to store the images
        client (boto3.client): S3 client
        s3_file (str): S3 object name
    """
    try:
        print(f'uploading: {local_file} to {bucket}/{key}')
        client.upload_file(Bucket=bucket, Key=key, Filename=str(local_file))
    except BaseException as ex:
        print(f'failed to upload {local_file}: {str(ex)}')

# multi-threaded impl: files in folder to s3 bucket/prefix/
def put_files(bucket_name:str, local_folder:Path, prefix:str, filter:str = '*', threads:int = 10):
  
    print (f'storing files: {local_folder} to s3://{bucket_name}/{prefix}')
    session = boto3.Session()
    client = session.client('s3')

    with ThreadPoolExecutor(max_workers=threads) as executor:
        try:
            for file in Path(local_folder).rglob(filter):
                if file.is_file() and not 'DS_Store' in file.name:
                    key = str(file).replace(str(local_folder), prefix).replace('//', '/')
                    executor.submit(put_file, bucket_name, client, file, key)
            return 0
        except Exception as err:
            print(f'error copying {local_folder} to s3://{bucket_name}/{prefix}: {str(err)}')
            return 215

# delegate to download a single file, used by multi-threader in getFiles()
def get_file(bucket:str, output_folder:str, client: boto3.client, key:str):
    """
    Download a single file from S3
    Args:
        bucket (str): S3 bucket where images are hosted
        output (str): Dir to store the images
        client (boto3.client): S3 client
        s3_file (str): S3 object name
    """ 
    try:
        local_file = os.path.join(output_folder, key)
        print(f'downloading: {local_file}')
        os.makedirs(os.path.dirname(local_file), exist_ok=True)

        client.download_file(Bucket=bucket, Key=key, Filename=local_file)
    except BaseException as ex:
        print("failed to download {0}: {1}".format(local_file, str(ex)))

# multithreaded implementation
def get_files_list(bucket_name : str, keys : list, local_folder: str, threads : int = 10):

  # Creating only one session and one client
  session = boto3.Session()
  client = session.client("s3")
  # The client is shared between threads
  func = partial(get_file, bucket_name, local_folder, client)

  with ThreadPoolExecutor(max_workers=threads) as executor:
    executor.map(get_file, keys)

# multithreaded implementation
def get_files(bucket_name:str, prefix:str, local_folder:str, filter:str, threads:int = 10):

    # create only one session and one client
    session = boto3.Session()
    client = session.client("s3")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for key in list_objects(bucket_name=bucket_name, prefix=prefix):
            if filter is None or filter == '' or re.search(filter, key):
                executor.submit(get_file, bucket_name, local_folder, client, key)
