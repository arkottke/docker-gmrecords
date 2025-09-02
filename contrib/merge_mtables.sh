#!/bin/bash
# merge_mtables.sh - Download, extract, merge, deduplicate, and upload Parquet files from S3
# Requirements: awscli, duckdb, tar, awk, grep, find, mktemp

set -euo pipefail

if [[ -z "${BUCKET_NAME:-}" ]]; then
  echo "Error: BUCKET_NAME environment variable is not set." >&2
  exit 1
fi
BUCKET="$BUCKET_NAME"
PREFIX="database/data"
LOGFILE="merge_mtables_$(date '+%Y%m%d').log"
EVENTS_DB="mtables/dsgmd_default_events.parquet"
TMPDIR=$(mktemp -d)

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

trap 'log "Script failed at line $LINENO"; exit 1' ERR

pushd "$TMPDIR"
log "Working in $TMPDIR"

log "Listing S3 archives..."
aws s3 ls s3://$BUCKET/$PREFIX/ --recursive | awk '{print $4}' | grep 'mtables-.*\.tar\.gz$' > archives.txt

if [[ ! -s archives.txt ]]; then
  log "No mtables-*.tar.gz files found. Exiting."
  exit 0
else
  log "Found $(wc -l < archives.txt) mtables archives:"
fi

mkdir "mtables"
# Syncing mtables from S3
log "Downloading mtables from S3..."
aws s3 sync "s3://$BUCKET/database/mtables" "mtables/"

upload_parquet() {
  log "Uploading Parquet files to S3..."
  find mtables -name '*.parquet' | while read -r pq; do
    s3key="${pq#./}"
    log "Uploading $pq to s3://$BUCKET/database/$s3key"
    if aws s3 cp "$pq" "s3://$BUCKET/database/$s3key"; then
      log "Uploaded $pq"
    else
      log "Failed to upload $pq"
    fi
  done
  log "Upload complete."
}

event_counter=0
total_events=$(wc -l < archives.txt)
while read -r key; do
  eid=$(echo "$key" | sed -e 's|.*mtables-\(.*\).tar.gz|\1|')
  event_counter=$((event_counter + 1))
  log "Processing event $event_counter of $total_events: $eid"
  # Check if eid exists in database
  if [ -e "$EVENTS_DB" ]; then
    count=$(duckdb -noheader -csv -c "SELECT COUNT(*) FROM read_parquet('$EVENTS_DB') WHERE id = '$eid';")
    if [ "$count" -gt 0 ]; then
      log "Event $eid already exists in database. Skipping download."
      continue
    fi
  fi

  log "Downloading $key..."
  if aws s3 cp "s3://$BUCKET/$key" .; then
    archive=$(basename "$key")
    dir="${archive%.tar.gz}"
    mkdir -p "$dir"
    log "Extracting $archive..."
    if tar -xzvf "$archive" -C "$dir" >> "$LOGFILE" 2>&1; then
      rm "$archive"
      rm "$dir"/*_README.csv
      for csv in "$dir"/*.csv; do
        [[ -e "$csv" ]] || continue

        base=$(basename "$csv" .csv)
        pq="mtables/$base.parquet"
        log "Merging $csv with $pq..."
        if [[ -f "$pq" ]]; then
          duckdb -c "CREATE OR REPLACE TABLE merged AS SELECT * FROM read_parquet('$pq') UNION SELECT * FROM read_csv_auto('$csv'); COPY merged TO '$pq' (FORMAT PARQUET);" >> "$LOGFILE" 2>&1
        else
          duckdb -c "COPY (SELECT * FROM read_csv_auto('$csv')) TO '$pq' (FORMAT PARQUET);" >> "$LOGFILE" 2>&1
        fi
        rm "$csv"
      done
    else
      log "Failed to extract $archive"
    fi
  else
    log "Failed to download $key"
  fi
  log "Done with $key"
  # Clean up extracted directory
  rm -rf "$dir"

  # After every 200 events, upload Parquet files to S3
  if (( event_counter % 200 == 0 )); then
    upload_parquet
  fi
done < archives.txt

log "Final upload: Uploading remaining Parquet files to S3..."
upload_parquet
log "All events processed and uploaded."

log "All done. Cleaning up."
aws s3 cp "$LOGFILE" "s3://$BUCKET/database/mtables/$LOGFILE"

popd
rm -rf "$TMPDIR"
