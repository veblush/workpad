#!/bin/bash
set -e

if [ $# -lt 4 ];then
  echo "Usage: $0 client bucket object times [parameters]"
  exit 1
fi

JAVA_BIN=/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64/bin/java
JAVA_OPT=-Xmx4096m
GCS_JAR=$HOME/grpc-gcp-java/end2end-test-examples/gcs/build/libs/gcs-1.0-SNAPSHOT.jar

$JAVA_BIN \
  $JAVA_OPT \
  -jar $GCS_JAR \
  --client=$1 \
  --bkt=$2 \
  --obj=$3 \
  --calls=$4 \
  --method=read \
  ${@:5}
