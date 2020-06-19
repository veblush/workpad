#!/usr/bin/env python3

import argparse
import locale
import queue
import shlex
import signal
import subprocess
import os
import sys
import threading


def enqueue_output(out, que):
  for line in iter(out.readline, b''):
    que.put(line)
  out.close()


def run_command(cmd_argv, que):
  print("*** Start commands: ")
  print("- Arguments: ", cmd_argv)
  process = subprocess.Popen(
      cmd_argv, stdout=subprocess.PIPE, bufsize=1, close_fds=1)
  print("- PID={0}".format(process.pid))
  thread = threading.Thread(target=enqueue_output, args=(process.stdout, que))
  thread.daemon = True
  thread.start()
  return process


def run_perf(perf_argv, pid, on_start_script):
  args = ["perf", "record", "-p", str(pid)] + perf_argv
  print("*** Start perf: ")
  print("- Arguments: ", args)
  process = subprocess.Popen(args)
  print("- PID={0}".format(process.pid))
  if on_start_script:
    print("*** Run on_start_script:")
    script_args = shlex.split(on_start_script)
    print("- Arguments: ", script_args)
    env = os.environ.copy()
    env['PERF_TARGET_PID'] = str(pid)
    script_proc = subprocess.run(script_args, env=env)
    print("- ReturnCode: ", script_proc.returncode)

  return process


def stop_perf(perf_process, on_stop_script, pid, perf_output):
  print("*** Stop perf: ")
  perf_process.send_signal(signal.SIGINT)
  perf_process.wait()
  if on_stop_script:
    print("*** Run on_stop_script:")
    script_args = shlex.split(on_stop_script)
    print("- Arguments: ", script_args)
    env = os.environ.copy()
    env['PERF_TARGET_PID'] = str(pid)
    env['PERF_OUTPUT_PATH'] = perf_output
    script_proc = subprocess.run(script_args, env=env)
    print("- ReturnCode: ", script_proc.returncode)


def get_perf_output(perf_argv):
  output = "perf.data"
  for i, a in enumerate(perf_argv):
    if i < len(perf_argv) - 1 and (a in ["-o", "--output"]):
      output = perf_argv[i + 1]
  return output


def run(my_args, perf_argv, cmd_argv):
  que = queue.Queue()
  command_process = run_command(cmd_argv, que)
  perf_process = None
  if not my_args.cstart:
    perf_process = run_perf(perf_argv, command_process.pid, my_args.onstart)
  while True:
    try:
      line = que.get(timeout=.01)
    except queue.Empty:
      pass
    else:
      lstr = line.decode(locale.getpreferredencoding(False))
      if not perf_process and my_args.cstart:
        if my_args.cstart in lstr:
          print("*** Detect Perf-Start Output:", lstr.rstrip())
          perf_process = run_perf(perf_argv, command_process.pid,
                                  my_args.onstart)
      if perf_process and my_args.cstop:
        if my_args.cstop in lstr:
          print("*** Detect Perf-Stop Output: ", lstr.rstrip())
          perf_output = get_perf_output(perf_argv)
          stop_perf(perf_process, my_args.onstop, command_process.pid, perf_output)
    if command_process.poll() is not None:
      print("*** Command exited: {0}".format(command_process.poll()))
      break
  if perf_process is None:
      print("*** Did not start perf")
      sys.exit(1)


def parse_argument():
  parser = argparse.ArgumentParser(description='perf-crecord command')
  parser.add_argument('--cstart', help="Output pattern to start perf")
  parser.add_argument('--cstop', help="Output pattern to stop perf")
  parser.add_argument('--onstart', help="Command to run on perf-start")
  parser.add_argument('--onstop', help="Command to run on perf-stop")

  remains = sys.argv[1:]
  if "--" not in remains:
    print(sys.argv[0] +
        " [<perf-arguments>] [== <crecord-arguments>] -- <command>")
    print("")
    parser.print_help()
    sys.exit(1)

  idx = remains.index("--")
  cmd_argv = remains[idx + 1:]
  remains = remains[:idx]

  my_argv = []
  if "==" in remains:
    idx = remains.index("==")
    my_argv = remains[idx + 1:]
    remains = remains[:idx]
  perf_argv = remains

  my_args = parser.parse_args(my_argv)
  return my_args, perf_argv, cmd_argv


def main():
  my_args, perf_argv, cmd_argv = parse_argument()
  run(my_args, perf_argv, cmd_argv)


if __name__ == "__main__":
  main()
