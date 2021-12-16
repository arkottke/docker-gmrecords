#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

import pathlib, argparse, clilib

parser = argparse.ArgumentParser()
parser.add_argument('-bucket', dest='bucket', help='The name of the s3 bucket to get data from',required=True)
parser.add_argument('-prefix', dest='prefix', help='the prefix to use when retrieving the files from s3, defaults to "output/"',default='output/')
parser.add_argument('-local-folder', dest='localFolder', type=pathlib.Path, help='The local folder to download the files into', default='output.tmp')
parser.add_argument('-filter', dest='filter', type=str, help='a regular expression filter matching the file names to download, get all by default')
parser.add_argument('-threads', dest='threads', type=int, help='the number of threads used in downloading files',default=10)

def main(args):
    clilib.get(bucket=args.bucket, prefix=args.prefix, local_folder=args.localFolder, filter=args.filter, thread_count=args.threads)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)


