#!/bin/bash
set -e

if [ $# -lt 3 ];then
  echo "Usage: $0 bucket object times"
  exit 1
fi

BENCHMARK_BIN=$HOME/grpc-gcp-cpp/bazel-bin/e2e-examples/gcs/benchmark/benchmark

$BENCHMARK_BIN \
  --bucket=$1 \
  --object=$2 \
  --runs $3 \
  --threads 1 \
  --cpolicy percall \
  ${@:4}