#!/usr/bin/env python3
"""Run a benchmark runfile and restart it whenever it stalls.

    python scripts/supervise_run.py --runfile scripts/run_benchmarks_openrouter.py

`ai_client` sends requests without a timeout, so a stalled generation hangs the run with no error,
no cost and a healthy process -- the only symptom is that no new result file appears.

Each cycle launches the runfile, watches `results/<date>/<test id>/`, and restarts when nothing has
been written for `--stall-minutes`. Each launch covers only the tests with no `scoring.json`, the
runner's own completion marker, so a restart never repeats finished work. The runner gets `--date`
as `BENCHMARK_RUN_DATE`, so it writes where this script looks even across midnight. Every
relaunch, after a stall or after the runner exits with tests outstanding, counts towards
`--max-restarts`.

Stdout is one line per event, so this can drive a Monitor.
"""
import argparse
import csv
import glob
import io
import os
import re
import signal
import subprocess
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_scope(runfile):
    """The runfile's full test list and worker count, read once and never written back.

    Its `limit_to` is the only record of what a run was meant to cover, so each cycle writes the
    outstanding subset to a generated sibling instead of trimming the original.
    """
    text = io.open(runfile, encoding="utf-8").read()
    head, _, tail = text.rpartition("main(limit_to=")
    if not head:
        raise SystemExit("no main(limit_to= call in %s" % runfile)
    workers = re.search(r"workers\s*=\s*(\d+)", tail)
    return head, re.findall(r'"(T\d{4})"', tail), workers.group(1) if workers else "10"


def write_cycle_runfile(runfile, head, todo, workers):
    """Write the outstanding subset to a generated sibling and return its path."""
    generated = os.path.join(os.path.dirname(runfile),
                             "_supervised_" + os.path.basename(runfile))
    # Name the log after the runfile as well as the clock: the runner calls its log
    # "<timestamp>.log", so a fan-out launched in the same second interleaves into one file.
    stem = os.path.splitext(os.path.basename(runfile))[0].replace("run_benchmarks_", "")
    head = head.replace(
        """{log_dir}/{time.strftime('%Y%m%d-%H%M%S')}.log""",
        """{log_dir}/{time.strftime('%%Y%%m%%d-%%H%%M%%S')}-%s.log""" % stem)
    io.open(generated, "w", encoding="utf-8", newline="").write(
        head + "main(limit_to=[%s], workers=%s)\n"
        % (", ".join('"%s"' % t for t in todo), workers))
    return generated


def outstanding(ids, date):
    return [t for t in ids
            if not os.path.exists(os.path.join(PROJECT_ROOT, "results", date, t, "scoring.json"))]


def newest_result_mtime(date, tests):
    newest = 0.0
    for test in tests:
        pattern = os.path.join(PROJECT_ROOT, "results", date, test, "request_*.json")
        for path in glob.glob(pattern):
            mtime = os.path.getmtime(path)
            if mtime > newest:
                newest = mtime
    return newest


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runfile", required=True)
    parser.add_argument("--date",
                        default=os.environ.get("BENCHMARK_RUN_DATE") or time.strftime("%Y-%m-%d"),
                        help="results folder to watch, passed to the runner as "
                             "BENCHMARK_RUN_DATE; defaults to that variable, else today")
    parser.add_argument("--stall-minutes", type=float, default=15.0,
                        help="restart once no new result file has appeared for this long")
    parser.add_argument("--max-restarts", type=int, default=20)
    parser.add_argument("--interval", type=float, default=30.0)
    args = parser.parse_args()

    runfile = os.path.abspath(args.runfile)
    head, everything, workers = read_scope(runfile)
    # The runner writes to the folder this date names, the one checked here, even after
    # midnight or for a date other than today.
    env = dict(os.environ, BENCHMARK_RUN_DATE=args.date)
    restarts = 0
    launched = False
    while True:
        todo = outstanding(everything, args.date)
        if not todo:
            print("DONE every test in %s has a scoring.json (%d tests)"
                  % (os.path.basename(runfile), len(everything)), flush=True)
            return
        # Every relaunch counts, whatever ended the last one: a runner that exits with tests
        # outstanding -- with 0, having skipped blocked tests, or with an error -- would
        # otherwise be relaunched forever.
        if launched:
            if restarts >= args.max_restarts:
                print("GIVING UP after %d restarts, %d tests outstanding"
                      % (restarts, len(todo)), flush=True)
                return
            restarts += 1
        launched = True
        generated = write_cycle_runfile(runfile, head, todo, workers)
        print("START %s: %d of %d tests outstanding%s"
              % (os.path.basename(runfile), len(todo), len(everything),
                 "" if not restarts else " (restart %d)" % restarts), flush=True)
        proc = subprocess.Popen([sys.executable, "-u", os.path.basename(generated)],
                                cwd=os.path.join(PROJECT_ROOT, "scripts"), env=env)
        last_seen = time.time()
        while True:
            time.sleep(args.interval)
            if proc.poll() is not None:
                print("EXIT %s returned %s" % (os.path.basename(runfile), proc.returncode),
                      flush=True)
                break
            newest = newest_result_mtime(args.date, todo)
            if newest > last_seen:
                last_seen = newest
            idle = (time.time() - last_seen) / 60
            if idle >= args.stall_minutes:
                print("STALL no new result for %.0f min -- restarting" % idle, flush=True)
                try:
                    proc.send_signal(signal.SIGTERM)
                    proc.wait(timeout=30)
                except Exception:
                    proc.kill()
                break


if __name__ == "__main__":
    main()
