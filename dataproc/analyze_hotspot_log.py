#!/usr/bin/env python3

import argparse
import os
import re
import datetime
import sys
import xml.etree.ElementTree as ET
import collections

RE_LOADED = re.compile(r"\[Loaded ([^ ]+) from ([^ ]+)\]")
SHADED_CLASS_PREFIX = "com.google.cloud.hadoop.repackaged.gcs."
SHADED_METHOD_PREFIX = "com/google/cloud/hadoop/repackaged/gcs/"
TOP_CLASSES = 5
TOP_METHODS = 5


def get_class_group(c):
  if c.startswith(SHADED_CLASS_PREFIX):
    c = c[len(SHADED_CLASS_PREFIX):]
  return ".".join(c.split(".")[:4])


def get_method_group(m):
  if m.startswith(SHADED_METHOD_PREFIX):
    m = m[len(SHADED_METHOD_PREFIX):]
  return "/".join(m.split(" ")[0].split("/")[:4])


def run(args):
  times = {}
  loadeds = []
  methods = []
  last_stamp = 0
  with open(args.input) as f:
    for line in f:
      l = line.strip()
      mo = RE_LOADED.match(l)
      if mo:
        name = mo.group(1)
        loadeds.append(name)
        v = times.setdefault(
            int(last_stamp),
            [0, collections.Counter(), 0,
             collections.Counter()])
        v[0] += 1
        v[1].update([get_class_group(name)])
      elif l.startswith("<nmethod "):
        nm = ET.fromstring(l)
        method = nm.attrib['method']
        methods.append(method)
        last_stamp = float(nm.attrib['stamp'])
        v = times.setdefault(
            int(last_stamp),
            [0, collections.Counter(), 0,
             collections.Counter()])
        v[2] += 1
        v[3].update([get_method_group(method)])
  with open(args.output + ".loadeds", "wt") as f:
    for x in sorted(set(loadeds)):
      f.write(x + "\n")
  with open(args.output + ".methods", "wt") as f:
    for x in sorted(set(methods)):
      f.write(x + "\n")
  with open(args.output + ".time.csv", "wt") as f:
    f.write("time\tloaded\tmethods")
    for i in range(TOP_CLASSES):
      f.write("\tc{0}\tc{0}".format(i + 1))
    for i in range(TOP_METHODS):
      f.write("\tm{0}\tm{0}".format(i + 1))
    f.write("\n")
    for k in sorted(times.keys()):
      v = times[k]
      f.write("{0}\t{1}\t{2}".format(k, v[0], v[2]))
      clses = v[1].most_common(TOP_CLASSES)
      for t, n in clses:
        f.write("\t{0}\t{1}".format(t, n))
      for _ in range(TOP_CLASSES - len(clses)):
        f.write("\t\t")
      mtds = v[3].most_common(TOP_METHODS)
      for t, n in mtds:
        f.write("\t{0}\t{1}".format(t, n))
      for _ in range(TOP_METHODS - len(mtds)):
        f.write("\t\t")
      f.write("\n")


def main():
  parser = argparse.ArgumentParser(description='Runs command')
  parser.add_argument('-i', '--input', help="The path of input file")
  parser.add_argument('-o', '--output', help="The path of output file")
  args = parser.parse_args()
  run(args)


if __name__ == "__main__":
  main()
