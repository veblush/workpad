#!/bin/bash
if [ -z "$1" ] ; then
    echo "Client is needed. yoshi, grpc, gcsio-http, and gcsio-grpc"
    exit
fi
JAVA=/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64/bin/java
TEST_JAR=~/grpc-gcp-java/end2end-test-examples/gcs/build/libs/gcs-all-1.0-SNAPSHOT.jar
REPORT_FILE=~/log/report-gcs-java-$1.tsv
for i in {1..100}
  do
    for t in 1 2 4 6 8 10 12 14 16 18 20
      do
        echo ----- iteration:$i threads:$t -----
        ../runs.py -r $t -t $t \
          --report_tag $t \
          --report_file=$REPORT_FILE \
          -- \
          $JAVA \
          -jar $TEST_JAR \
          --client=$1 \
          --bkt=gcs-grpc-team-veblush1 \
          --obj=1GB.bin \
          --buffSize=1048576 \
          --method=read \
          --dp=true \
          --calls=20
      done
  done
