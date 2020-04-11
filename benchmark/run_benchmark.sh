#!/bin/bash

REPORT_FILE=$HOME/log/benchmark-result.tsv
GCS_BUCKET=gcs-grpc-team-veblush1
GCS_OBJECT=1GB.bin
REPEAT_TIMES=20

for i in {1..2}; do
  for t in 1 2 4 6 8 10 12 14 16 18 20; do
    for j in curl cpp_gcs java_gcs_yoshi java_gcs_grpc java_gcsio_http java_gcsio_grpc; do
      echo ========================================
      echo = i:$i t:$t j:$j
      echo
      case $j in
        curl)
          cmd="./job_curl.sh $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES"
          ;;
        cpp_gcs)
          cmd="./job_cpp_gcs.sh $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES"
          ;;
        java_gcs_yoshi)
          cmd="./job_java_gcs.sh yoshi $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES"
          ;;
        java_gcs_grpc)
          cmd="./job_java_gcs.sh grpc $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES"
          ;;
        java_gcsio_http)
          cmd="./job_java_gcs_gradle.sh gcsio-http $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES"
          ;;
        java_gcsio_grpc)
          cmd="./job_java_gcs_gradle.sh gcsio-grpc $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES"
          ;;
      esac
      ../runs.py -r $t -t $t \
        --report_tag $j \
        --report_file=$REPORT_FILE \
        -- $cmd
    done
  done
done
