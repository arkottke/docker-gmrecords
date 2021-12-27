# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com
import os
from pathlib import Path
import s3lib, fwlib, ziplib

# this will compress folders in the input folder into zip files
def compress_inputs(source_folder:Path = 'source.tmp/', zip_folder : Path = 'zipped.tmp/', level:int = 1, filter:str = None):
    if not (os.path.exists(source_folder)):
        print("Cannot find inputFolder {0}, exiting".format(source_folder))
        exit(-1)

    if not (os.path.exists(zip_folder)):
        os.makedirs(zip_folder)

    for dir in source_folder.rglob(filter):
        if dir.is_dir():
            out_file = f'{str(dir).replace(str(source_folder), str(zip_folder))}.7z'
            print(out_file)
            
            if os.path.exists(out_file):
                os.remove(out_file)
            
            ziplib.compress(source_path=dir, zip_path=out_file)
            
# load the data into S3 
def upload(
    bucket_name: str,
    local_folder: Path = Path('./input.tmp/'),
    prefix:str = 'input/',
    filter:str = '*',
    thread_count : int = 10):

    #load the bucket with files from a local directory. Exclude directory names!
    print(f'loading input data to bucket: s3://{bucket_name}/{prefix} from {local_folder}')
    s3lib.put_files(bucket_name=bucket_name, local_folder=local_folder, prefix=prefix, filter=filter, threads=thread_count)

def expand_outputs(local_path ='./output.tmp/', output_dir ='', test:bool=False, remove_zip:bool=False):
	# unzip all the zips in the download folder
    items = list(Path(local_path).rglob("*.7[zZ]"))
    n = 0
    for item in items:
        n += 1
        s_item = str(item)

        if output_dir == '':
            my_out_dir = str(item.parent)
        else:
            my_out_dir = output_dir

        if item.name.startswith('Logs'): # handle log directories a little differently
            destination_path = os.path.join(my_out_dir, item.stem)
        else:
            destination_path = my_out_dir
        
        if test:
            print("test - unzip {0} to {1}".format(s_item, my_out_dir))
            ret = 1
        else:
            ret = ziplib.expand(source_path= s_item, destination_path= my_out_dir)

        if ret == 0:
            if remove_zip:
                os.remove(s_item)
        elif not test:
            print("error unzipping " + s_item)

    if n == 0:
        print("no 7z files found under: " + local_path)

def get(bucket:str, prefix:str, filter:str, local_folder='output.tmp', thread_count:int=10):
    os.makedirs(local_folder, exist_ok=True)

    print(f'getting data from bucket: s3://{bucket}/{prefix} from {local_folder}')
    s3lib.get_files(bucket_name=bucket, local_path=local_folder, prefix=prefix, filter=filter, threads=thread_count)

# convert an input string e.g. comma separated list or a range to a padded list
def convert_input_to_list(input_string:str, padding:int):
    items = []
    b_is_range = '-' in input_string
    if b_is_range:
        items = input_string.split('-')
    else:
        items = input_string.split(',')
    
    output_items = []

    # convert the range to a list, assumes that the numbers are continuous
    if b_is_range:
        # if it's a range, assume first and last are in order and we fetch each site in between
        i_first = int(items[0])
        i_last = int(items[1])

        # build a list of sites
        for i in range(i_first, i_last+1):
            item = str(i).zfill(padding)
            output_items.append(item)
    else:
        # format the numbers in the list with the correct padding
        for i in items:
            item = str(i).zfill(padding)
            output_items.append(item)
    return output_items
