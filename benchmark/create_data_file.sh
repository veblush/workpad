#!/bin/bash
set -e

if [ $# -lt 2 ];then
  echo "Usage: $0 file size(MB)"
  exit 1
fi

dd if=/dev/urandom of=$1 bs=1M count=$2 iflag=fullblock
