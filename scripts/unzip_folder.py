#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

import ziplib, os, argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-zipdir', dest='zipdir', type=Path, help='The folder containing the zip files, defaults to "output.tmp"', default='output.tmp')
parser.add_argument('-outdir', dest='outdir', type=Path, help='The folder to unzip the files into. When not specified, use the same folder as specified in -zipdir')
parser.add_argument('-test', action='store_true', dest='test', help='previews the zip operation without performing it')
parser.add_argument('-remove-zip', action='store_true', dest='removeZip', help='remove the zip file, false by default')

def main(args):
	# unzip all the zips in the download folder
    items = list(Path(args.zipdir).rglob("*.7[zZ]"))
    n = 0
    for item in items:
        n += 1
        s_item = str(item)

        my_out_dir = str(item.parent)
        if args.outdir is not None:
            my_out_dir = my_out_dir.replace(str(args.zipdir),str(args.outdir))

        if args.test:
            print("test - unzip {0} to {1}".format(s_item, my_out_dir))
            ret = 1
        else:
            ret = ziplib.expand(source_path= s_item, destination_path= my_out_dir)

        if ret == 0:
            if args.removeZip:
                os.remove(s_item)
        elif not args.test:
            print("error unzipping " + s_item)

    if n == 0:
        print(f'no 7z files found under: {args.zipdir}')


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
