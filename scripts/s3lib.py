#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

import boto3, os, re
import concurrent.futures
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

def list_objects(bucket_name, client, prefix):
    ar = []
    files = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in files:
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
    return_code = 0

    print (f'storing files: {local_folder} to s3://{bucket_name}/{prefix}')
    session = boto3.Session()
    client = session.client('s3')

    futures = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            for file in Path(local_folder).rglob(filter):
                if file.is_file() and not 'DS_Store' in file.name:
                    key = str(file).replace(str(local_folder), prefix).replace('//', '/')
                    futures.append(executor.submit(put_file, bucket_name, client, file, key))

            for future in concurrent.futures.as_completed(futures):
                process_result = future.result()
                if process_result != 0:
                    return_code = process_result
    except Exception as err:
        print(f'error copying {local_folder} to s3://{bucket_name}/{prefix}: {str(err)}')
        return_code = 216

    return return_code


# delegate to download a single file, used by multi-threader in getFiles()
def get_file(bucket:str, local_file:str, client: boto3.client, key:str):
    return_code = 0
    """
    Download a single file from S3
    Args:
        bucket (str): S3 bucket where images are hosted
        output (str): Dir to store the images
        client (boto3.client): S3 client
        s3_file (str): S3 object name
    """ 
    try:
        print(f'downloading: {local_file} from s3://{bucket}/{key}')
        os.makedirs(os.path.dirname(local_file), exist_ok=True)

        client.download_file(Bucket=bucket, Key=str(key), Filename=str(local_file))
    except BaseException as ex:
        print("failed to download {0}: {1}".format(local_file, str(ex)))
        return_code = 217
    
    return return_code


# multithreaded implementation
def get_files_list(bucket_name : str, keys : list, local_folder: str, threads : int = 10):
    return_code = 0
    # Creating only one session and one client
    session = boto3.Session()
    client = session.client("s3")

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for key in keys:
            rel_key = Path(key).name
            local_file = Path(local_folder).joinpath(rel_key)
            future = executor.submit(get_file, bucket_name, local_file, client, key)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
                process_result = future.result()
                if process_result != 0:
                    return_code = process_result

    return return_code

def get_files(bucket_name:str, prefix:str, local_path:str, filter:str = None, threads:int = 10):
    return_code = 0
    # create only one session and one client
    session = boto3.Session()
    client = session.client("s3")
    print(f'fetching: {local_path} from s3://{bucket_name}/{prefix}')

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for key in list_objects(bucket_name=bucket_name, client=client, prefix=prefix):
            if filter is None or filter == '' or re.search(filter, key):
                # get last index of '/'
                if len(prefix) == 0:
                    rel_key = key
                else:
                    if local_path.endswith('/'):
                        tmp_prefix = prefix
                        if prefix[-1] != '/':
                            tmp_prefix = os.path.dirname(prefix)
                        rel_key = key.replace(tmp_prefix,'')
                        if rel_key[0] == '/':
                            rel_key = rel_key[1:]
                        local_file = os.path.join(local_path, rel_key)
                    else:
                        local_file = local_path

                # print(f'prefix: {prefix}  tmp_prefix: {tmp_prefix} rel_key: {rel_key} local_file {local_file}')
                futures.append(executor.submit(get_file, bucket_name, local_file, client, key))
        
        for future in concurrent.futures.as_completed(futures):
                process_result = future.result()
                if process_result != 0:
                    return_code = process_result

    return return_code
