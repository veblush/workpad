#!/bin/bash
REPORT_FILE=~/log/report-curl.tsv
for i in {1..100}
  do
    for t in 1 2 4 6 8 10 12 14 16 18 20
      do
        echo ***** iteration:$i threads:$t
        ../runs.py -r 100 -t $t \
          --report_tag $t \
          --report_file=$REPORT_FILE \
          -- \
          ./curl_1GB.sh
      done
  done
