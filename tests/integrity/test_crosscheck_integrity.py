"""The dataset export and the frontend export must agree about what they both describe.

Plan §9 step 7. Two pipelines read the same tree and keep different things: the frontend
skips what it cannot chart, keeps one request per run and normalises scores; the dataset
keeps everything and refuses to normalise. Those differences are the design. Anything else
is one of them having misread a file the other read correctly.

**This is a diagnostic, not an oracle.** Since the shared results layer landed, both
pipelines walk the corpus through `scripts/results_index.py`, so a fault in that layer
would move both exports together and go unseen here. What this still catches is the two
disagreeing about a run's identity, its visibility, its recorded scores or the price each
resolved -- places where they diverge after the shared read.

Skipped unless a built dataset and a current frontend export are both present, since it
compares two artifacts rather than testing code.

Run logic-only with: pytest -m "not integrity".
"""
from pathlib import Path

import pytest

from scripts.export_dataset.crosscheck import FRONTEND_EXPORT, compare, load_dataset, load_frontend
from scripts.results_index import PROJECT_ROOT

pytestmark = pytest.mark.integrity

DATASET = PROJECT_ROOT / "dataset"


@pytest.fixture(scope="module")
def artifacts():
    if not (DATASET / "runs.parquet").is_file():
        pytest.skip("no built dataset at %s; run `python -m scripts.export_dataset`"
                    % DATASET)
    if not FRONTEND_EXPORT.is_file():
        pytest.skip("no frontend export at %s" % FRONTEND_EXPORT)
    runs, requests, scores = load_dataset(DATASET)
    return runs, requests, scores, load_frontend()


def test_the_two_exports_describe_the_same_runs(artifacts):
    runs, _requests, _scores, frontend = artifacts
    ours = set(r["run_id"] for r in runs)
    theirs = set(frontend)
    assert ours == theirs, (
        "%d runs only in the dataset, %d only in the frontend export. Both walk the same "
        "tree, so a difference means one of them is filtering where it should not."
        % (len(ours - theirs), len(theirs - ours)))


def test_no_unexpected_differences(artifacts):
    runs, requests, scores, frontend = artifacts
    findings, shared = compare(runs, requests, scores, frontend)
    assert shared > 0, "nothing was compared"

    by_check = {}
    for finding in findings:
        by_check.setdefault(finding["check"], []).append(finding["detail"])

    assert not findings, (
        "the two exports disagree on %d point(s) across %d shared runs:\n  %s\n"
        "Every legitimate difference between them is listed in crosscheck.py; anything "
        "here is not one of them."
        % (len(findings), shared,
           "\n  ".join("%s: %s" % (check, details[0])
                       for check, details in sorted(by_check.items()))))
