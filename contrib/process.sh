#!/bin/sh
# Usage: ./download.sh <event_id>

set -eox pipefail

EID=$1

ARGS=(
    --eventid "${EID}"
    --label "default"
    --log "${EID}.log"
    --num-processes 2
)

for step in process_waveforms compute_station_metrics compute_waveform_metrics export_metric_tables; do
    gmrecords "${ARGS[@]}" $step
done

pushd data
if [ ls *.csv 1> /dev/null 2>&1 ]; then
    echo "No CSV files found in data directory."
else
    tar -czf "${EID}/mtables-${EID}.tar.gz" *.csv
fi
popd
