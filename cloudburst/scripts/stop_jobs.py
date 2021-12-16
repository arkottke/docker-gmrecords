#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

import os, boto3
import argparse, clilib

parser = argparse.ArgumentParser()
parser.add_argument('-apply', dest='apply', action='store_true', help='Apply the current configuration, otherwise previews the outcome')
parser.add_argument('-queue', dest='job_queue', help='The queue to check', default=os.getenv('BATCH_QUEUE'))
parser.add_argument('-jobprefix', dest='job_prefix', help='a prefix to use when the jobnames parameter provided is numeric, a numeric range or comma-separated list (optional)', default='')
group1 = parser.add_mutually_exclusive_group()
group1.add_argument('-all', dest='stop_all', action='store_true', help='stop all jobs')
group1.add_argument('-jobnames', dest='items', help='An individual, list or range of job names, e.g. "item1"')
group1.add_argument('-jobnamefile', dest='item_list_file', type=argparse.FileType('r'), help='A file containing the list of items to run, each line in the format needed by the application')

# starts batch jobs in AWS using the list of work items specified
def main(args):
    if args.job_queue is None:
        print("Error: must specify -queue or set $BATCH_QUEUE variable")
        exit(-1)
    
    b_is_site_range = False
    work_items = []
        
    # site list is a list of one or more sites (comma separated), or a range of sites (dash separated)
    # which is it?
    if args.items is not None:
        items = clilib.convert_input_to_list(args.items, 3)
        for item in items:
            work_items.append(f'{args.job_prefix}{item}')
    elif args.item_list_file is not None:
        for wi in args.item_list_file.read().splitlines():
            work_items.append(f'{args.job_prefix}{wi}')
    elif not args.stop_all:
        print("error: must provide one of these params: -jobnames, -jobnamefile, -all")
        exit(-1)

    if not args.apply:
        print('previewing stop-job request...') 

    client = boto3.client('batch')

    if args.stop_all or len(work_items) > 0:
        response = client.list_jobs(jobQueue=args.job_queue)
    else:
        print("error: no items were provided to process")
        exit(-1)

    count = 0
    for job_item in response['jobSummaryList']:
        print(job_item)
        if job_item['status'] not in ['SUCCEEDED','FAILED']:
            if args.stop_all or len(work_items) > 0:
                if args.stop_all or job_item['jobName'] in work_items:
                    print (f'stopping job: {job_item["jobName"]} [{job_item["jobId"]}]')
                    count += 1
                    if args.apply:
                        response = client.terminate_job(jobId=job_item['jobId'], reason='user cancelled')
                    print(f'job termination attempted. id [{job_item["jobId"]}]')
    if count == 0:
        print('   there are no active jobs to cancel')
    elif not args.apply:
        print('   this is a preview only. To execute command add the -apply flag')


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
