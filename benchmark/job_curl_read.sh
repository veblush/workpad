#!/bin/bash
set -e

if [ $# -lt 3 ];then
  echo "Usage: $0 bucket object times"
  exit 1
fi

URL="https://www.googleapis.com/storage/v1/b/$1/o/$2?alt=media"
URLS=$URL
for i in $(seq 2 $3); do
   URLS+=" $URL"
done
curl ${@:4} -s $URLS > /dev/null
