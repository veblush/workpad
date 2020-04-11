#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass

PERCENTILES = [0.01, 0.25, 0.50, 0.75, 0.99]


@dataclass
class CpuStat:
  time: datetime.datetime
  user: float = 0
  nice: float = 0
  system: float = 0
  iowait: float = 0
  steal: float = 0
  idle: float = 0


CPU_STAT_FIELDS = ['user', 'nice', 'system', 'iowait', 'steal', 'idle']


def init_cpu_stat_proc():
  try:
    return subprocess.Popen(["iostat", "-c", "-o", "JSON", "1", "2"],
                            stdout=subprocess.PIPE)
  except OSError:
    return None


def get_cpu_stat(p):
  if p is None:
    return None
  j = json.loads(p.communicate()[0])
  cpu_stat = j["sysstat"]["hosts"][0]["statistics"][-1]["avg-cpu"]
  return CpuStat(datetime.datetime.now(), cpu_stat['user'], cpu_stat['nice'],
                 cpu_stat['system'], cpu_stat['iowait'], cpu_stat['steal'],
                 cpu_stat['idle'])


def print_stats(start_time, end_time, results, cpu_stats):
  elapsed_time = datetime.datetime.now() - start_time
  print("Elapsed time: {0} sec".format(elapsed_time.total_seconds()))
  times = sorted(r[2] - r[1] for r in results)
  print("Run:")
  for p in PERCENTILES:
    p_value = times[int(len(times) * p)].total_seconds()
    print("  p{0:.2f}: {1:.2f} sec".format(p, p_value))
  if cpu_stats:
    print("CPU:")
    for f in CPU_STAT_FIELDS:
      values = [getattr(stat, f) for stat in cpu_stats]
      print("  {0}: {1:.2f}".format(f, sum(values) / len(values)))


def write_report(start_time, end_time, results, cpu_stats, args):
  elapsed_time = datetime.datetime.now() - start_time
  times = sorted(r[2] - r[1] for r in results)
  is_new_file = not os.path.exists(args.report_file)
  with open(args.report_file, "at") as f:
    if is_new_file:
      f.write("\t".join([
          "Time", "Tag", "Elapsed", "Threads", "Runs", "Run-P01-T", "Run-P25-T",
          "Run-P50-T", "Run-P75-T", "Run-P99-T"
      ] + ["CPU-" + f for f in CPU_STAT_FIELDS]) + "\n")
    f.write("{0}\t{1}\t{2:.2f}\t{3}\t{4}".format(start_time, args.report_tag,
                                                 elapsed_time.total_seconds(),
                                                 args.threads, args.runs))
    for p in PERCENTILES:
      p_value = times[int(len(times) * p)].total_seconds()
      f.write("\t{0:.2f}".format(p_value))
    for field in CPU_STAT_FIELDS:
      if cpu_stats:
        values = [getattr(stat, field) for stat in cpu_stats]
        v = sum(values) / len(values)
      else:
        v = 0
      f.write("\t{0:.2f}".format(v))
    f.write("\n")


def run(args, cmds):
  processes = []
  results = []
  cpu_stats = []
  cpu_stats_proc = init_cpu_stat_proc()
  start_time = datetime.datetime.now()
  last_stat_time = None
  while len(results) < args.runs:
    for i in range(len(processes) - 1, -1, -1):
      p = processes[i][0]
      if p.poll() != None:
        now = datetime.datetime.now()
        if args.verbose:
          print("Done: Code={0} Elapsed={1}".format(p.poll(),
                                                    now - processes[i][1]))
        results.append((p.poll(), processes[i][1], now))
        del processes[i]
    while len(
        processes) < args.threads and len(processes) + len(results) < args.runs:
      if args.verbose:
        print("Run")
      p = subprocess.Popen(cmds)
      processes.append((p, datetime.datetime.now()))
    if cpu_stats_proc.poll() != None:
      stat = get_cpu_stat(cpu_stats_proc)
      if stat:
        cpu_stats.append(stat)
      cpu_stats_proc = init_cpu_stat_proc()
    time.sleep(0.01)

  end_time = datetime.datetime.now()
  if args.stats:
    print_stats(start_time, end_time, results, cpu_stats)
  if args.report_file:
    write_report(start_time, end_time, results, cpu_stats, args)


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
  parser.add_argument(
      "--report_tag",
      type=str,
      default="",
      help="The user-defined tag to be inserted in the report")
  parser.add_argument(
      "--report_file", type=str, help="The file to append the line for the run")

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
