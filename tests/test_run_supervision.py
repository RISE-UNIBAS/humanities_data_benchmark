"""The run supervisor and the run watcher, against a fake runner and a fake results tree.

Both scripts drove paid runs for six weeks untracked and untested; these pin the three
defects a review found in them (2026-10-30): the runner was not given the date the
supervisor watched, only stall restarts counted against --max-restarts, and the watcher
marked a half-written result file as seen and never read it again.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import json

import pytest

import supervise_run
import watch_run


# --- supervise_run ---------------------------------------------------------------------

def _supervise(tmp_path, monkeypatch, exit_code, max_restarts):
    """Supervise a runner that never finishes its one test; return the date each launch got."""
    monkeypatch.setattr(supervise_run, "PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv("BENCHMARK_RUN_DATE", raising=False)
    (tmp_path / "scripts").mkdir()
    dates = tmp_path / "dates.txt"
    runfile = tmp_path / "scripts" / "run_benchmarks_fake.py"
    runfile.write_text("\n".join([
        "import os, sys",
        "with open(%r, 'a') as fh:" % str(dates),
        "    print(os.environ.get('BENCHMARK_RUN_DATE', '-'), file=fh)",
        "def main(limit_to=None, workers=1):",
        "    sys.exit(%d)" % exit_code,
        'main(limit_to=["T9999"], workers=1)',
    ]) + "\n", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["supervise_run.py", "--runfile", str(runfile),
                                     "--date", "2026-01-02", "--interval", "0.05",
                                     "--max-restarts", str(max_restarts)])
    supervise_run.main()
    return dates.read_text(encoding="utf-8").split()


@pytest.mark.parametrize("exit_code", [0, 1])
def test_a_runner_that_exits_unfinished_is_relaunched_only_up_to_the_limit(
        tmp_path, monkeypatch, capsys, exit_code):
    """Exit 0 included: the runner returns 0 having skipped blocked tests."""
    launches = _supervise(tmp_path, monkeypatch, exit_code, max_restarts=2)
    assert len(launches) == 3, "the first launch and two restarts"
    assert "GIVING UP after 2 restarts" in capsys.readouterr().out


def test_no_restarts_means_one_launch(tmp_path, monkeypatch):
    assert len(_supervise(tmp_path, monkeypatch, 1, max_restarts=0)) == 1


def test_the_runner_writes_to_the_date_the_supervisor_watches(tmp_path, monkeypatch):
    """Without it, a run past midnight writes to the next day's folder while the supervisor
    keeps checking the launch day's, and restarts into work that is already saved."""
    assert set(_supervise(tmp_path, monkeypatch, 1, max_restarts=1)) == {"2026-01-02"}


# --- watch_run -------------------------------------------------------------------------

class _Stop(Exception):
    pass


def test_a_result_file_first_seen_half_written_is_checked_once_complete(tmp_path, monkeypatch,
                                                                       capsys):
    monkeypatch.setattr(watch_run, "PROJECT_ROOT", str(tmp_path))
    results = tmp_path / "results" / "2026-01-02" / "T9999"
    results.mkdir(parents=True)
    log = tmp_path / "run.log"
    log.write_text("", encoding="utf-8")
    runfile = tmp_path / "run_benchmarks_fake.py"
    runfile.write_text('main(limit_to=["T9999"], workers=1)\n', encoding="utf-8")

    complete = json.dumps({"finish_reason": "stop", "score": {"f1": 1.0},
                           "usage": {"estimated_cost_usd": 0.9, "output_tokens": 10}})
    request = results / "request_T9999_a.json"
    request.write_text(complete[:20], encoding="utf-8")
    passes = []

    def sleep(_seconds):
        passes.append(1)
        if len(passes) == 1:
            request.write_text(complete, encoding="utf-8")
        else:
            raise _Stop

    monkeypatch.setattr(watch_run.time, "sleep", sleep)
    monkeypatch.setattr("sys.argv", ["watch_run.py", "--runfile", str(runfile),
                                     "--log", str(log), "--date", "2026-01-02",
                                     "--since", "all"])
    with pytest.raises(_Stop):
        watch_run.main()
    assert "WASTE expensive request T9999/request_T9999_a.json $0.90" in capsys.readouterr().out
