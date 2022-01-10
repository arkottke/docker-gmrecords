#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

import os
from pathlib import Path

# Compresses a 7zip archive, providing exception handling and logging
def compress(zip_path:Path, source_path:Path):
    zip_path = Path(zip_path)
    source_path = Path(source_path)

    print(f'compressing: {source_path} to: {zip_path}')
    if not zip_path.parent is None and not zip_path.parent.exists():
        os.makedirs(zip_path.parent, exist_ok=True)

    try:
        if os.name == 'nt':
            exec_7z = '7z'
            redirect = ''
        else:
            exec_7z = '7z'
            redirect = ' > /dev/null'

        # resolve() is needed to normalize the path, else the containing directory shows up in the archive!
        return os.system(f'{exec_7z} a -mx1 -y "{zip_path}" "{source_path.resolve()}"{redirect}')
    except Exception as err:
        print(f'error zipping {source_path} to {zip_path}: {str(err)}')
        return 211


# expands a 7z archive from path to destination
def expand(source_path:str, destination_path:str):
    print(f'expanding: {source_path} to {destination_path}')
    os.makedirs(destination_path, exist_ok=True)

    try:
        if os.name == 'nt':
            exec_7z = '7z'
            redirect = ''
        else:
            exec_7z = '7z'
            redirect = ' > /dev/null'

        return os.system(f'{exec_7z} x -y "{source_path}" -o"{destination_path}"{redirect}')
    except Exception as err:
        print(f'error unzipping {source_path} to {destination_path}: {str(err)}')
        return 212
