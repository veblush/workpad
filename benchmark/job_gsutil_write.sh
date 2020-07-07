#!/bin/bash
set -e

if [ $# -lt 4 ];then
  echo "Usage: $0 bucket object srcfile times"
  exit 1
fi

URL="gs://$1/$2"
for i in $(seq 1 $4); do
  gsutil cp ${@:5} $3 ${URL}_${RUN_PROCESS_ID}
done
