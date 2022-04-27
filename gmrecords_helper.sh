#!/bin/bash

set -euo pipefail

EID=$1
LABEL="default"

cd /working

if [ ! -f "data/$EID/workspace.h5" ]; then
    # Check if files need to be downloaded
    if [ ! -d "data/$EID/raw" ]; then
        echo ">> `date`: Downloading $EID"
        gmrecords download -e $EID
    fi
    # Assemble
    echo ">> `date`: Assembling $EID"
    gmrecords assemble -e $EID
    # Remove temporary directories created in the assembly
    rm -rf data/$EID/tmp*
fi

echo ">> `date`: Processing $EID"
gmrecords process -e $EID -l $LABEL
echo ">> `date`: Computing station metrics $EID"
gmrecords compute_station_metrics -e $EID -o -l $LABEL
echo ">> `date`: Computing waveform metrics $EID"
gmrecords compute_waveform_metrics -e $EID -o -l $LABEL

# echo ">> `date`: Generating report $EID"
# gmrecords report -e $EID -l default
# Remove the plots and latex files created by the report generation as these
# are stored in the report, and re-created eachtime
# rm -rf data/$EID/plots data/$EID/*.{aux,tex,log,png}
