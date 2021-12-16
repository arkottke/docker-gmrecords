#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

import pathlib, argparse, clilib

parser = argparse.ArgumentParser()
parser.add_argument('-bucket', dest='bucket', help='The name of the s3 bucket to upload data into',required=True)
parser.add_argument('-local-folder', dest='localFolder', type=pathlib.Path, help='The local folder containing the files to upload', default='./zips.tmp')
parser.add_argument('-prefix', dest='prefix', help='the prefix to use for storing files in s3, defaults to "input/"',default='input/')
parser.add_argument('-filter', dest='filter', help='a filter matching the file names to upload, all by default',default='*')
parser.add_argument('-threads', dest='threads', type=int, help='the number of threads used in uploading files',default=10)

def main(args):
    clilib.upload(bucket_name=args.bucket, local_folder=args.localFolder, prefix=args.prefix, filter=args.filter, thread_count=args.threads)

if __name__ == "__main__":
    # testargs = ['-bucket','test-bruceh','-local-folder','input.tmp','-prefix','test1/','-filter','*','-threads','10']
    args = parser.parse_args()
    main(args)
