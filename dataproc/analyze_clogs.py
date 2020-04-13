#!/usr/bin/env python3

import argparse
import os
import re
import datetime
import sys
from dataclasses import dataclass


@dataclass
class ClogDigest:
  start_time: datetime.datetime = None
  end_time: datetime.datetime = None
  map_start_time: datetime.datetime = None
  map_split: int = 0
  fs_start_time: datetime.datetime = None
  fs_exec_time: float = 0
  fs_io_rate: float = 0


RE_LOG = re.compile(r"(\d+)-(\d+)-(\d+) (\d+)\:(\d+)\:(\d+),(\d+) (\w+) (.*)")
RE_SPLIT = re.compile(r"Processing split\: gs\://.+_(\d+)\:.*")
RE_TestDFSIO_T = re.compile(r"Exec time = (\d+)")
RE_TestDFSIO_R = re.compile(r"IO rate = (\d*\.\d+|\d+)")


def clog_reader(path):
  with open(os.path.join(path, "syslog")) as f:
    for l in f.readlines():
      mo = RE_LOG.match(l.strip())
      if mo:
        time = datetime.datetime(
            int(mo.group(1)),
            int(mo.group(2)),
            int(mo.group(3)),
            int(mo.group(4)),
            int(mo.group(5)),
            int(mo.group(6)),
            int(mo.group(7)) * 1000,
            tzinfo=datetime.timezone.utc)
        level = mo.group(8)
        msg = mo.group(9)
        yield (time, level, msg)


def analyze_clog(path):
  d = ClogDigest()
  for time, level, msg in clog_reader(path):
    if not d.start_time:
      d.start_time = time
    d.end_time = time
    if "org.apache.hadoop.mapred.MapTask" in msg:
      mo = RE_SPLIT.search(msg)
      if mo:
        d.map_start_time = time
        d.map_split = mo.group(1)
    if "org.apache.hadoop.fs.TestDFSIO:" in msg:
      if "in = org.apache.hadoop.fs.FSDataInputStream" in msg:
        d.fs_start_time = time
      mo = RE_TestDFSIO_T.search(msg)
      if mo:
        d.fs_exec_time = int(mo.group(1)) / 1000.0
      mo = RE_TestDFSIO_R.search(msg)
      if mo:
        d.fs_io_rate = float(mo.group(1))
  return d


def build_pipelines(digests):
  pipelines = []
  for d in sorted(digests, key=lambda x: x.start_time):
    ai = -1
    for i, pipeline in enumerate(pipelines):
      if pipeline[-1].end_time < d.start_time:
        ai = i
        break
    if ai == -1:
      pipelines.append([])
      ai = len(pipelines) - 1
    pipelines[ai].append(d)
  return pipelines


def run(args):
  ds = []
  for p in os.walk(args.input):
    if "syslog" in p[2]:
      d = analyze_clog(p[0])
      if d.fs_start_time:
        ds.append(d)
  ds = list(sorted(ds, key=lambda x: x.start_time))
  print("\t".join([
      "time", "total_elapsed", "intro_elapsed", "map_intro_elapsed",
      "fs_elapsed", "outro_elapsed", "fs_io_rate (MB/s)"
  ]))
  for d in ds:
    total_elapsed = (d.end_time - d.start_time).total_seconds()
    intro_elapsed = (d.map_start_time - d.start_time).total_seconds()
    map_intro_elapsed = (d.fs_start_time - d.map_start_time).total_seconds()
    outro_elapsed = (d.end_time -
                     d.fs_start_time).total_seconds() - d.fs_exec_time
    print("{0:%H:%M:%S}\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}"
          .format(d.start_time, total_elapsed, intro_elapsed, map_intro_elapsed,
                  d.fs_exec_time, outro_elapsed, d.fs_io_rate))
  print()
  one_sec = datetime.timedelta(seconds=1)
  pipelines = build_pipelines(ds)
  print("\t".join([
      "time",
  ] + ["p" + str(i) for i in range(len(pipelines))] + [
      "downloads",
      "throughput (MB/s)",
  ]))
  min_time = min(d.start_time for d in ds).replace(microsecond=0)
  max_time = max(d.end_time for d in ds).replace(microsecond=0)
  cur_time = min_time
  while cur_time <= max_time:
    pvalues = []
    x = 0
    s = 0
    for pipeline in pipelines:
      d = None
      for task in pipeline:
        if cur_time >= task.start_time - one_sec and cur_time < task.end_time + one_sec:
          d = task
      if d:
        if cur_time < d.fs_start_time - one_sec:
          pvalues.append("^")
        elif cur_time < d.fs_start_time + datetime.timedelta(
            seconds=d.fs_exec_time) - one_sec:
          pvalues.append("D")
          x += d.fs_io_rate
          s += 1
        else:
          pvalues.append("$")
      else:
        pvalues.append(" ")
    print("{0:%H:%M:%S}\t{1}\t{2}\t{3:.2f}".format(cur_time, "\t".join(pvalues), s, x))
    cur_time = cur_time + datetime.timedelta(seconds=1)



def main():
  parser = argparse.ArgumentParser(description='Runs command')
  parser.add_argument('-i', '--input', help="The path of input directory")
  args = parser.parse_args()
  run(args)


if __name__ == "__main__":
  main()
