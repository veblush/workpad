#!/bin/bash

REPORT_FILE=$HOME/log/benchmark-result.tsv
GCS_BUCKET=gcs-grpc-team-veblush1
GCS_OBJECT=1GB.bin
GCS_OBJECT_KB_SIZE=1048576
BENCHMARK_TIMES=10
REPEAT_TIMES=20
GCS_JAVA_OPTION="--buffSize=$GCS_OBJECT_KB_SIZE --dp=true"
# GCS_JAVA_OPTION="--buffSize=$GCS_OBJECT_KB_SIZE --dp=true --conscrypt=true"

for i in $(seq 1 $BENCHMARK_TIMES); do
  for t in 1 8; do
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
          cmd="./job_java_gcs.sh yoshi $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES $GCS_JAVA_OPTION"
          ;;
        java_gcs_grpc)
          cmd="./job_java_gcs.sh grpc $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES $GCS_JAVA_OPTION"
          ;;
        java_gcsio_http)
          cmd="./job_java_gcs.sh gcsio-http $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES $GCS_JAVA_OPTION"
          ;;
        java_gcsio_grpc)
          cmd="./job_java_gcs.sh gcsio-grpc $GCS_BUCKET $GCS_OBJECT $REPEAT_TIMES $GCS_JAVA_OPTION"
          ;;
      esac
      ../runs.py -r $t -t $t \
        --report_tag $j \
        --report_file=$REPORT_FILE \
        -- $cmd
    done
  done
done
