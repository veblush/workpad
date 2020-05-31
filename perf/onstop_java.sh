#!/bin/bash

if [ -z "$PERF_MAP_DIR" ]; then
  PERF_MAP_DIR=$HOME/perf-map-agent
fi

if [ -z "$PERF_JAVA_TMP" ]; then
  PERF_JAVA_TMP=/tmp
fi

if [ -z "$PERF_REPORT_OUTPUT" ]; then
  PERF_REPORT_OUTPUT=${PERF_OUTPUT_PATH%.data}.txt
fi

STACKS=$PERF_JAVA_TMP/out-$PERF_TARGET_PID.stacks
COLLAPSED=$PERF_JAVA_TMP/out-$PERF_TARGET_PID.collapsed

if [ ! -x "$FLAMEGRAPH_DIR/stackcollapse-perf.pl" ]; then
  echo "FlameGraph executable not found at '$FLAMEGRAPH_DIR/stackcollapse-perf.pl'. Please set FLAMEGRAPH_DIR to the root of the clone of https://github.com/brendangregg/FlameGraph."
  exit
fi

if [ -z "$PERF_FLAME_OUTPUT" ]; then
  PERF_FLAME_OUTPUT=${PERF_OUTPUT_PATH%.data}-flamegraph.svg
fi

if [ -z "$PERF_FLAME_OPTS" ]; then
  PERF_FLAME_OPTS="--color=java"
fi

# Create symbol map using https://github.com/jvm-profiling-tools/perf-map-agent
$PERF_MAP_DIR/bin/create-java-perf-map.sh $PERF_TARGET_PID "$PERF_MAP_OPTIONS"

# Create a report
perf report -i $PERF_OUTPUT_PATH --stdio --no-children --header > $PERF_REPORT_OUTPUT

# Create a flamegraph
perf script -i $PERF_OUTPUT_PATH > $STACKS
$FLAMEGRAPH_DIR/stackcollapse-perf.pl $PERF_COLLAPSE_OPTS $STACKS | tee $COLLAPSED | $FLAMEGRAPH_DIR/flamegraph.pl $PERF_FLAME_OPTS > $PERF_FLAME_OUTPUT
