#!/usr/bin/env python3

import argparse
import re
import datetime

RE_TIME = re.compile(r"(\d+)\:(\d+)\:(\d+)")
RE_IPPORT = re.compile(r"\[/[0-9.]+\:[0-9]*\]")

def run(args):
  all_ipports_set = set()
  time_count = 0
  prev = set()
  print("\t".join(("time", "size", "unique", "new", "del", "ipports")))
  l, prev_l = "", ""
  with open(args.input, "rt") as f:
    for line in f:
      prev_l, l = l, line.strip()
      if l.find("cluster-impl-lb") < 0 or l.find("(storage.googleapis.com)] Received resolution result") < 0:
        continue
      mo = RE_TIME.search(prev_l)
      if mo is None:
        print("What? " + prev_l)
        continue
      time = datetime.time(
          int(mo.group(1)),
          int(mo.group(2)),
          int(mo.group(3)))
      ipports = [x[2:-1] for x in RE_IPPORT.findall(l)]
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
