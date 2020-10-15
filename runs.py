#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

PERCENTILES = [0.01, 0.25, 0.50, 0.75, 0.99]


@dataclass
class PerfStat:
  task_clock: float = 0
  context_switches: int = 0
  cpu_migrations: int = 0
  page_faults: int = 0
  cycles: int = 0
  instructions: int = 0
  branches: int = 0
  branch_misses: int = 0
  wall_time: float = 0
  user_time: float = 0
  sys_time: float = 0


PERF_STAT_FIELDS = [
    'task_clock', 'context_switches', 'cpu_migrations', 'page_faults', 'cycles',
    'instructions', 'branches', 'branch_misses', 'wall_time', 'user_time',
    'sys_time'
]


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


@dataclass
class MemStat:
  time: datetime.datetime
  total: int = 0
  used: int = 0
  free: int = 0
  shared: int = 0
  cache: int = 0
  available: int = 0


MEM_STAT_FIELDS = ['total', 'used', 'free', 'shared', 'cache', 'available']


@dataclass
class NetStat:
  time: datetime.datetime
  in_bandwith: int = 0
  out_bandwith: int = 0


NET_STAT_FIELDS = ['in_bandwith', 'out_bandwith']


def init_cpu_stat_proc():
  try:
    return subprocess.Popen(["iostat", "-c", "-o", "JSON", "1", "2"],
                            stdout=subprocess.PIPE)
  except OSError as e:
    print(e)
    return None


def get_cpu_stat(p):
  if p is None:
    return None
  j = json.loads(p.communicate()[0])
  cpu_stat = j["sysstat"]["hosts"][0]["statistics"][-1]["avg-cpu"]
  return CpuStat(datetime.datetime.now(), cpu_stat['user'], cpu_stat['nice'],
                 cpu_stat['system'], cpu_stat['iowait'], cpu_stat['steal'],
                 cpu_stat['idle'])


def get_mem_stat():
  try:
    o = subprocess.check_output(["free"])
    for l in o.decode('utf-8').split("\n"):
      if l.startswith("Mem:"):
        values = [int(w) for w in l[5:].split()]
        if len(values) == 6:
          return MemStat(datetime.datetime.now(), values[0], values[1],
                         values[2], values[3], values[4], values[5])
    return None
  except OSError as e:
    print(e)
    return None


def init_net_stat_proc():
  try:
    return subprocess.Popen(["ifstat", "-Tq", "1", "1"], stdout=subprocess.PIPE)
  except OSError as e:
    print(e)
    return None


def get_net_stat(p):
  if p is None:
    return None
  o = p.communicate()[0]
  l = [l for l in o.decode('utf-8').split("\n") if l.strip()][-1]
  values = [int(float(w) * 1024) for w in l.split()]
  if len(values) >= 2:
    return NetStat(datetime.datetime.now(), values[-2], values[-1])
  return None


def parse_float(s):
  return float(s.replace(",", ""))


def parse_int(s):
  return int(s.replace(",", ""))


def parse_perf_stat_output(output):
  stat = PerfStat()
  mo = re.search(r"([0-9.,]+)\s+msec\s+task-clock", output)
  if mo:
    stat.task_clock = parse_float(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+context-switches", output)
  if mo:
    stat.context_switches = parse_int(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+cpu-migrations", output)
  if mo:
    stat.cpu_migrations = parse_int(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+page-faults", output)
  if mo:
    stat.page_faults = parse_int(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+cycles", output)
  if mo:
    stat.cycles = parse_int(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+instructions", output)
  if mo:
    stat.instructions = parse_int(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+branches", output)
  if mo:
    stat.branches = parse_int(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+branch-misses", output)
  if mo:
    stat.branch_misses = parse_int(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+seconds time elapsed", output)
  if mo:
    stat.wall_time = parse_float(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+seconds user", output)
  if mo:
    stat.user_time = parse_float(mo.group(1))
  mo = re.search(r"([0-9.,]+)\s+seconds sys", output)
  if mo:
    stat.sys_time = parse_float(mo.group(1))
  return stat


def get_mid(vals):
  if vals:
    return sorted(vals)[len(vals) / 2]
  return None


def print_stats(start_time, end_time, results, sys_stats):
  elapsed_time = datetime.datetime.now() - start_time
  error_runs = sum(1 if r[0] != 0 else 0 for r in results)
  print("Elapsed time: {0} sec".format(elapsed_time.total_seconds()))
  print("Total runs: {0} errors: {1}".format(len(results), error_runs))
  times = sorted(r[2] - r[1] for r in results)
  print("Run:")
  for p in PERCENTILES:
    p_value = times[int(len(times) * p)].total_seconds()
    print("  p{0:.2f}: {1:.2f} sec".format(p, p_value))
  perf_stats = list(sorted((r[3] for r in results), key=lambda x: x.task_clock))
  perf_stat_mid = perf_stats[len(perf_stats) // 2]
  print("Perf (p50):")
  for f in PERF_STAT_FIELDS:
    print("  {0}: {1}".format(f, getattr(perf_stat_mid, f)))
  if sys_stats:
    print("CPU:")
    for f in CPU_STAT_FIELDS:
      values = [getattr(sys_stat[0], f) for sys_stat in sys_stats]
      print("  {0}: {1:.2f}".format(f, get_mid(values)))
    print("MEM:")
    for f in MEM_STAT_FIELDS:
      values = [getattr(sys_stat[1], f) for sys_stat in sys_stats]
      print("  {0}: {1:.2f}".format(f, get_mid(values)))
    print("NET:")
    for f in NET_STAT_FIELDS:
      values = [getattr(sys_stat[2], f) for sys_stat in sys_stats]
      print("  {0}: {1:.2f}".format(f, get_mid(values)))



def write_report(start_time, end_time, results, sys_stats, args):
  elapsed_time = datetime.datetime.now() - start_time
  error_runs = sum(1 if r[0] != 0 else 0 for r in results)
  times = sorted(r[2] - r[1] for r in results)
  is_new_file = not os.path.exists(args.report_file)
  with open(args.report_file, "at") as f:
    if is_new_file:
      all_columns = ([
          "Time", "Tag", "Elapsed", "Threads", "Runs", "Errors", "Run-P01-T",
          "Run-P25-T", "Run-P50-T", "Run-P75-T", "Run-P99-T"
      ] + ["PERF-" + f for f in PERF_STAT_FIELDS] +
                     ["CPU-" + f for f in CPU_STAT_FIELDS] +
                     ["MEM-" + f for f in MEM_STAT_FIELDS] +
                     ["NET-" + f for f in NET_STAT_FIELDS])
      f.write("\t".join(all_columns) + "\n")
    f.write("{0}\t{1}\t{2:.2f}\t{3}\t{4}\t{5}".format(
        start_time, args.report_tag, elapsed_time.total_seconds(), args.threads,
        args.runs, error_runs))
    for p in PERCENTILES:
      p_value = times[int(len(times) * p)].total_seconds()
      f.write("\t{0:.2f}".format(p_value))
    perf_stats = list(
        sorted((r[3] for r in results), key=lambda x: x.task_clock))
    perf_stat_mid = perf_stats[len(perf_stats) // 2]
    for field in PERF_STAT_FIELDS:
      v = getattr(perf_stat_mid, field)
      f.write("\t{0:.2f}".format(v))
    for field in CPU_STAT_FIELDS:
      if sys_stats:
        values = [getattr(sys_stat[0], field) for sys_stat in sys_stats]
        v = get_mid(values)
      else:
        v = 0
      f.write("\t{0:.2f}".format(v))
    for field in MEM_STAT_FIELDS:
      if sys_stats:
        values = [getattr(sys_stat[1], field) for sys_stat in sys_stats]
        v = get_mid(values)
      else:
        v = 0
      f.write("\t{0:.2f}".format(v))
    for field in NET_STAT_FIELDS:
      if sys_stats:
        values = [getattr(sys_stat[2], field) for sys_stat in sys_stats]
        v = get_mid(values)
      else:
        v = 0
      f.write("\t{0:.2f}".format(v))
    f.write("\n")


def run(args, cmds):
  processes = []
  results = []
  sys_stats = []
  cpu_stats_proc = init_cpu_stat_proc()
  net_stats_proc = init_net_stat_proc()
  start_time = datetime.datetime.now()
  # Dispatching processes running cmd
  last_proc_id = 0
  while len(results) < args.runs:
    for i in range(len(processes) - 1, -1, -1):
      p = processes[i][0]
      if p.poll() != None:
        now = datetime.datetime.now()
        start_time = processes[i][1]
        perf_stat_file = processes[i][2]
        with open(perf_stat_file, 'r') as f:
          perf_stat = parse_perf_stat_output(f.read())
        if perf_stat:
          os.remove(perf_stat_file)
        if args.verbose:
          print("Done: Code={0} Elapsed={1}".format(p.poll(), now - start_time))
        results.append((p.poll(), start_time, now, perf_stat))
        del processes[i]
    while len(
        processes) < args.threads and len(processes) + len(results) < args.runs:
      if args.verbose:
        print("Run")
      perf_stat_file = tempfile.mkstemp(prefix="runs_perf_")[1]
      last_proc_id += 1
      p_env = os.environ.copy()
      p_env['RUN_PROCESS_ID'] = str(last_proc_id)
      p = subprocess.Popen(["perf", "stat", "-o", perf_stat_file] + cmds, env=p_env)
      processes.append((p, datetime.datetime.now(), perf_stat_file))
    # Collect system stats
    if cpu_stats_proc.poll() != None and net_stats_proc.poll() != None:
      cpu_stat = get_cpu_stat(cpu_stats_proc)
      mem_stat = get_mem_stat()
      net_stat = get_net_stat(net_stats_proc)
      if cpu_stat and mem_stat and net_stat:
        sys_stats.append((cpu_stat, mem_stat, net_stat))
      cpu_stats_proc = init_cpu_stat_proc()
      net_stats_proc = init_net_stat_proc()
    time.sleep(0.01)
  # Reports when done
  end_time = datetime.datetime.now()
  if args.stats:
    print_stats(start_time, end_time, results, sys_stats)
  if args.report_file:
    write_report(start_time, end_time, results, sys_stats, args)


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


# Note: Please install sysstat ifstat to get system stats
if __name__ == "__main__":
  main()
