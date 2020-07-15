#!/bin/bash
set -e

if [ $# -lt 4 ];then
  echo "Usage: $0 bucket object srcfile times"
  exit 1
fi

URL="gs://$1/$2_${RUN_PROCESS_ID}"
for i in $(seq 1 $4); do
  if [ $UPLOAD_FILE_DIRECTLY ]; then
    gsutil cp ${@:5} "$3" ${URL}
  else
    cat "$3" | gsutil cp ${@:5} - ${URL}
  if
done
