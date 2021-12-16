#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

import os, boto3
import argparse, clilib

parser = argparse.ArgumentParser()
parser.add_argument('-mode', dest='mode', help='The mode to run in, if not otherwise specified', default='')
parser.add_argument('-bucket', dest='bucket', help='The name of an S3 bucket to use during the process, default is the $BUCKET_NAME environment variable', default=os.getenv('BUCKET_NAME'))
parser.add_argument('-apply', dest='apply', action='store_true', help='Apply the current configuration, otherwise previews the outcome')
parser.add_argument('-jobdef', dest='jobDef', help='The name of the job definition to use when running the batch job', default=os.getenv('BATCH_JOBDEF'))
parser.add_argument('-queue', dest='jobQueue', help='The mode to run in, if not otherwise specified', default=os.getenv('BATCH_QUEUE'))
parser.add_argument('-prefix', dest='itemPrefix', help='a prefix to use when the workitems parameter provides a numeric value, a numeric range or comma-separated list (optional)', default='')
parser.add_argument('-padding', dest='itemPadding', type=int, help='when the workitems parameter provides a numeric value, a numeric range or comma-separated list, the number of padded zeros (optional)', default=3)
parser.add_argument("-name-value", action='append', type=lambda kv: kv.split("="), dest='name_values', help='one or more custom name=value pairs to pass as variables to the server process')

group1 = parser.add_mutually_exclusive_group()
group1.add_argument('-workitems', dest='items', help='An individual, list or range of work items, e.g. "item1"')
group1.add_argument('-workitemfile', dest='itemListFile', type=argparse.FileType('r'), help='A file containing the list of items to run, each line in the format needed by the application', )

# starts batch jobs in AWS using the list of work items specified
def main(args):
    if args.jobDef is None:
        print("Error: must specify -jobdef or set $BATCH_JOBDEF variable")
        exit(-1)
    if args.jobQueue is None:
        print("Error: must specify -queue or set $BATCH_QUEUE variable")
        exit(-1)
    
    b_is_site_range = False
    work_items = []
    item_prefix = args.itemPrefix
    # site list is a list of one or more sites (comma separated), or a range of sites (dash separated)
    # which is it?
    if args.items is not None:
        items = clilib.convert_input_to_list(args.items, args.itemPadding)
        for item in items:
            work_items.append(f'{item_prefix}{item}')
    elif args.itemListFile is not None:
        for wi in args.itemListFile.read().splitlines():
            work_items.append(f'{item_prefix}{wi}')
    else:
        print("Error: must provide these params: workitems, workitemfile")
        exit(-1)

    if not args.name_values is None:
        if any(len(kv) < 2 for kv in args.name_values): raise ValueError('-name-value must be given in the form "KEY=VALUE"')

    if not args.apply:
        print('previewing job startup...') 

    client = boto3.client('batch')

    count = 0
    for work_item in work_items:
        count = count + 1
        print (f'starting: region [{client.meta.region_name}] bucket [{args.bucket}] job [{str(count).zfill(4)}] with [{work_item}] in mode [{args.mode}]')
        job_queue = args.jobQueue
        job_def = args.jobDef

        env_vars = [
                    { 'name': 'AWS_REGION', 'value': client.meta.region_name },
                    { 'name': 'BUCKET_NAME', 'value': args.bucket },
                    { 'name': 'WORK_ITEM', 'value': work_item },
                    { 'name': 'MODE_STR', 'value': args.mode }]

        # add custom variables
        if not (args.name_values is None or len(args.name_values) == 0):
            for name_value in args.name_values:
                env_vars.append({ 'name' : name_value[0], 'value' : name_value[1] })

        job_name = work_item.replace('/', '_')

        if args.apply:
            response = client.submit_job(
                jobName= job_name,
                jobDefinition = job_def,
                jobQueue = job_queue,
                containerOverrides = { 'environment': env_vars })
            print(f'job created. name [{response["jobName"]}], id [{response["jobId"]}]')
        else:
            print(f'preview: submit_job({job_name}, {job_def}, {job_queue}, {env_vars})')
            print(f'run this command with -apply to actually run it')


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
