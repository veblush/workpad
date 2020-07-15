#!/bin/bash
set -e

if [ $# -lt 4 ];then
  echo "Usage: $0 bucket object srcfile times"
  exit 1
fi

ACCESS_TOKEN=`gcloud auth print-access-token`

URL="https://www.googleapis.com/upload/storage/v1/b/$1/o?uploadType=media&name=${2}_${RUN_PROCESS_ID}"
for i in $(seq 2 $4); do
  if [ $UPLOAD_FILE_DIRECTLY ]; then
    url -X POST --data-binary "@$3" -H "Authorization: Bearer $ACCESS_TOKEN" $URL > /dev/null
  else
    cat "$3" | url -X POST --data-binary @- -H "Authorization: Bearer $ACCESS_TOKEN" $URL > /dev/null
  fi
done
