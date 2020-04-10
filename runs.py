#!/usr/bin/env python3

import argparse
import subprocess
import sys
import datetime
import time


def run(args, cmds):
  processes = []
  results = []
  start_time = datetime.datetime.now()
  while len(results) < args.runs:
    for i in range(len(processes) - 1, -1, -1):
      p = processes[i][0]
      if p.poll() != None:
        now = datetime.datetime.now()
        if args.verbose:
            print("Done: Code={0} Elapsed={1}".format(p.poll(), now - processes[i][1]))
        results.append((p.poll(), processes[i][1], now))
        del processes[i]
    while len(
        processes) < args.threads and len(processes) + len(results) < args.runs:
      if args.verbose:
        print("Run")
      p = subprocess.Popen(cmds)
      processes.append((p, datetime.datetime.now()))
    time.sleep(0.01)
  elapsed_time = datetime.datetime.now() - start_time
  if args.stats:
      print("Elapsed time: {0} sec".format(elapsed_time.total_seconds()))
      times = sorted(r[2] - r[1] for r in results)
      p_25 = int(len(times) * 0.25)
      p_50 = int(len(times) * 0.50)
      p_75 = int(len(times) * 0.75)
      print("Run: mid {0} sec".format(times[p_50]))
      print("     p25 {0} sec".format(times[p_25]))
      print("     p70 {0} sec".format(times[p_75]))

def main():
  parser = argparse.ArgumentParser(description='Runs command')
  parser.add_argument(
      '-r', '--runs', help="The number of runs", type=int, default=1)
  parser.add_argument(
      '-t',
      '--threads',
      help="The number of concurrent execution",
      type=int,
      default=1)
  parser.add_argument(
      "-v", "--verbose", action="store_true", help="increase output verbosity")
  parser.add_argument(
      '-s',
      '--stats',
      action="store_true",
      help="Show stats at the end",
  )

  argv = sys.argv
  if "--" not in argv:
    parser.print_help()
    return 1
  idx = argv.index("--")
  argv = sys.argv[1:idx]
  cmds = sys.argv[idx + 1:]

  args = parser.parse_args(argv)
  run(args, cmds)


if __name__ == "__main__":
  main()
