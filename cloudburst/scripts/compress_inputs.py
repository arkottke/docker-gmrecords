#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com
import pathlib, argparse, clilib

parser = argparse.ArgumentParser()
parser.add_argument('-source-folder', dest='sourceFolder', type=pathlib.Path, help='The name of the input folder that contains folders to be compressed', default='./source.tmp')
parser.add_argument('-zip-folder', dest='zipFolder', type=pathlib.Path, help='The name of the folder to write zip files into', default='./zips.tmp')
parser.add_argument('-filter', dest='filter', help='Filters the folder names to be zipped in the source folder, eg. "Site"')

def main(args):
    clilib.compress_inputs(source_folder=args.sourceFolder, zip_folder=args.zipFolder, filter=args.filter)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
