#!/bin/bash
set -e

if [ $# -lt 4 ];then
  echo "Usage: $0 client bucket object times [parameters]"
  exit 1
fi

GCS_PATH=$HOME/grpc-gcp-java/end2end-test-examples/gcs

pushd $GCS_PATH

ARGS="--client=$1 --bkt=$2 --obj=$3 --method=read --calls=$4 ${@:5}"
./gradlew run --args="$ARGS"

popd
