#!/bin/bash
set -e

if [ $# -lt 4 ];then
  echo "Usage: $0 bucket object size times"
  exit 1
fi

BENCHMARK_BIN=$HOME/grpc-gcp-cpp/bazel-bin/e2e-examples/gcs/benchmark/benchmark

$BENCHMARK_BIN \
  --operation=read \
  --bucket=$1 \
  --object=$2 \
  --write_size=$3 \
  --runs=$4 \
  --threads 1 \
  --cpolicy percall \
  ${@:4}
