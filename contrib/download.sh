#!/bin/sh
# Usage: ./download.sh <event_id>

set -eox pipefail

EID=$1

ARGS=(
 --eventid "${EID}"
 --label "default"
 --log "${EID}.log"
)

gmrecords "${ARGS[@]}" download
gmrecords "${ARGS[@]}" assemble
