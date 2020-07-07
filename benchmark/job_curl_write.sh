#!/bin/bash
set -e

if [ $# -lt 4 ];then
  echo "Usage: $0 bucket object srcfile times"
  exit 1
fi

ACCESS_TOKEN=`gcloud auth print-access-token`

URL="https://www.googleapis.com/upload/storage/v1/b/$1/o?uploadType=media&name=$2"
URLS=$URL
for i in $(seq 2 $4); do
   URLS+=" $URL"
done
curl -X POST --data-binary @$3 -H "Authorization: Bearer $ACCESS_TOKEN" $URLS > /dev/null
