#!/usr/bin/env python3

import argparse
import re
import datetime

RE_LOG = re.compile(r"(\d+)-(\d+)-(\d+) (\d+)\:(\d+)\:(\d+),(\d+) (\w+) (.*)")
RE_IPPORT = re.compile(r"\[/[0-9.]+\:[0-9]*\]")

def run(args):
  all_ipports_set = set()
  time_count = 0
  prev = set()
  print("\t".join(("time", "size", "unique", "new", "del", "ipports")))
  with open(args.input, "rt") as f:
    for line in f:
      l = line.strip()
      i = l.find("Using RR list=")
      if i < 0:
        continue
      if l.find("grpclb-<storage.googleapis.com>") < 0:
        continue
      mo = RE_LOG.search(l)
      if mo is None:
        print("What? " + l)
        continue
      time = datetime.datetime(
          int(mo.group(1)),
          int(mo.group(2)),
          int(mo.group(3)),
          int(mo.group(4)),
          int(mo.group(5)),
          int(mo.group(6)),
          int(mo.group(7)) * 1000,
          tzinfo=datetime.timezone.utc)      
      msg = l[i+14:]
      ipports = [x[2:-1] for x in RE_IPPORT.findall(msg)]
      ipports_set = set(ipports)
      print("{}\t{}\t{}\t{}\t{}\t{}".format(time, len(ipports), len(ipports_set), len(ipports_set - prev),len(prev - ipports_set), ", ".join(ipports)))
      prev = ipports_set
      all_ipports_set |= ipports_set
      time_count += 1
  print("all_ipports_set={0}".format(len(all_ipports_set)))
  print("avg_ipports_set={0}".format(len(all_ipports_set) / time_count))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', help="The path of grpc log")
  args = parser.parse_args()
  run(args)


if __name__ == "__main__":
  main()
