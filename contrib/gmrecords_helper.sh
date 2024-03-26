#!/bin/bash

set -euxo pipefail

EID=$1
ARGS=(--eventid $1 --label "default" --num-processes 0 --overwrite)

cd /working

# if [[ -f "data/$EID/workspace.h5" ]]; then
#     rm "data/$EID/workspace.h5"
# fi

# Copy the metadata into the raw directory
# if [[ -d "metadata" && -d "data/$EID/raw" ]]; then
#     cp metadata/* "data/$EID/raw/"
# fi

# if [ ! -f "data/$EID/workspace.h5" ]; then
#     # Check if files need to be downloaded
#     if [ ! -d "data/$EID/raw" ]; then
#         echo ">> `date`: Downloading $EID"
#         gmrecords download -e $EID
#     fi
#     # Assemble
#     echo ">> `date`: Assembling $EID"
#     gmrecords assemble -e $EID
#     # Remove temporary directories created in the assembly
#     rm -rf data/$EID/tmp*
# fi

echo ">> `date`: Downloading $EID"
gmrecords ${ARGS[@]} download

# echo ">> `date`: Assembling $EID"
# gmrecords ${ARGS[@]} assemble

# Repack the h5 and drop the old configuration and processed files
# echo ">> `date`: Cleaning and repacking $EID"
# python3 clean_workspace.py data/$EID/workspace.h5
# h5repack data/$EID/workspace.h5 /tmp/repacked.h5
# mv /tmp/repacked.h5 data/$EID/workspace.h5

# Update the configuration
# gmrecords ${ARGS[@]} config

# echo ">> `date`: Processing $EID"
# gmrecords ${ARGS[@]} process_waveforms

# echo ">> `date`: Computing station metrics $EID"
# gmrecords ${ARGS[@]} compute_station_metrics

# # Update the metrics
# echo ">> `date`: Computing waveform metrics $EID"
# gmrecords ${ARGS[@]} compute_waveform_metrics

# echo ">> `date`: Generating report $EID"
# gmrecords ${ARGS[@]} generate_report
# mv data/$EID/*_report_$EID.pdf data/$EID/report.pdf

# echo ">> `date`: Exporting mtables $EID"
# gmrecords ${ARGS[@]} mtables

# Move into the data directory so that the path in the archive isn't impacted
# cd data
# echo ">> `date`: Compressing CSV tables $EID"
# 7z a $EID/datatables.7z *.csv

# Remove the plots and latex files created by the report generation as these
# are stored in the report, and re-created eachtime
# rm -rf data/$EID/plots data/$EID/*.{aux,tex,log,png}
