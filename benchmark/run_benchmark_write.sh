#!/bin/bash

REPORT_FILE=$HOME/log/benchmark-result.tsv
GCS_BUCKET=gcs-grpc-team-veblush1
GCS_OBJECT=write/benchmark
GCS_OBJECT_MB_SIZE=1024
GCS_OBJECT_KB_SIZE=1048576
BENCHMARK_TIMES=100
REPEAT_TIMES=20
GCS_JAVA_OPTION="--dp=true"
# GCS_JAVA_OPTION="--dp=true --conscrypt=true"

CURL_DATA_FILE=/tmp/benchmark.dat
./create_data_file.sh $CURL_DATA_FILE $GCS_OBJECT_MB_SIZE

for i in $(seq 1 $BENCHMARK_TIMES); do
  for t in 1 2 3 4 5 6 7 8; do
    for j in curl cpp_gcs java_gcs_yoshi java_gcs_grpc java_gcsio_http java_gcsio_grpc; do
      echo ========================================
      echo = i:$i t:$t j:$j
      echo
      case $j in
        curl)
          cmd="./job_curl_write.sh $GCS_BUCKET $GCS_OBJECT $CURL_DATA_FILE $REPEAT_TIMES"
          ;;
        cpp_gcs)
          cmd="./job_cpp_gcs_write.sh $GCS_BUCKET $GCS_OBJECT $GCS_OBJECT_SIZE $REPEAT_TIMES"
          ;;
        java_gcs_yoshi)
          cmd="./job_java_gcs_write.sh yoshi $GCS_BUCKET $GCS_OBJECT $GCS_OBJECT_KB_SIZE $REPEAT_TIMES $GCS_JAVA_OPTION"
          ;;
        java_gcs_grpc)
          cmd="./job_java_gcs_write.sh grpc $GCS_BUCKET $GCS_OBJECT $GCS_OBJECT_KB_SIZE $REPEAT_TIMES $GCS_JAVA_OPTION"
          ;;
        java_gcsio_http)
          cmd="./job_java_gcs_write.sh gcsio-http $GCS_BUCKET $GCS_OBJECT $GCS_OBJECT_KB_SIZE $REPEAT_TIMES $GCS_JAVA_OPTION"
          ;;
        java_gcsio_grpc)
          cmd="./job_java_gcs_write.sh gcsio-grpc $GCS_BUCKET $GCS_OBJECT $GCS_OBJECT_KB_SIZE $REPEAT_TIMES $GCS_JAVA_OPTION"
          ;;
      esac
      ../runs.py -r $t -t $t \
        --report_tag $j \
        --report_file=$REPORT_FILE \
        -- $cmd
    done
  done
done
