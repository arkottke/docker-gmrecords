#! /bin/bash

JOBQUEUE=$1

for state in SUBMITTED PENDING RUNNABLE STARTING RUNNING
do
    for job in $(aws batch list-jobs --job-queue $JOBQUEUE --job-status $state --output text --query jobSummaryList[*].[jobId])
    do
        echo -ne "Stopping job $job in state $state\t"
        aws batch terminate-job --reason "Terminating job." --job-id $job && echo "Done." || echo "Failed."
    done
done
