#!/bin/bash
set -e

if [ $# -lt 3 ];then
  echo "Usage: $0 bucket object times"
  exit 1
fi

URL="gs://$1/$2"
URLS=$URL
for i in $(seq 2 $3); do
   URLS+=" $URL"
done
gsutil cat ${@:4} $URLS > /dev/null
