"""field_scores contract guard.

Every benchmark's `score_request_answer` records what it compared under `field_scores`,
so a comparison view can show the scorer's own verdict instead of an independent diff
that would contradict it -- box overlap, folio alignment by position and fuzzy
thresholds all disagree with a naive equality check. `generate_test_report.py` has
consumed this key since before it was universal; four benchmarks emitted it and eight
did not. This guard is what makes it safe to rely on, and what stops a new benchmark
from silently omitting it.

The whole returned score is written verbatim into the stored answer
(`Benchmark.save_answer`), which is why serializability is checked here rather than
discovered as a run-time crash: business_letters first reported Person dataclasses.

Run logic-only with: pytest -m "not integrity".

Rules enforced here, per benchmark, against one real stored response:
  1. `score_request_answer` returns a dict containing `field_scores`.
  2. `field_scores` is a dict, and each entry is a dict carrying `response`,
     `ground_truth` and `score`.
  3. `score` is a real number or None -- None where the scorer counts true and false
     positives rather than assigning a similarity, never a placeholder zero.
  4. The whole returned score is JSON-serializable.
"""
import json

import pytest

from scripts.offline_scoring import (SCAFFOLD_BENCHMARKS, benchmark_of_test,
                                     iter_run_inputs, iter_runs, load_scorer, read_tests,
                                     rules_of_test)

pytestmark = pytest.mark.integrity

# A scorer may legitimately reject a particular input -- an unusable ground truth
# returns None, and medieval_manuscripts raises on a subset of stored responses whose
# shape predates its current parser. Try a few before concluding the scorer is broken.
MAX_INPUTS_TRIED = 25


def _real_benchmarks():
    return sorted(set(benchmark_of_test().values()) - SCAFFOLD_BENCHMARKS)


def _first_score(benchmark):
    """The scorer's output for the first stored input it accepts, newest runs first."""
    tests = read_tests()
    scorer = load_scorer(benchmark)
    errors = []
    tried = 0

    for run_dir, test_id, _ in iter_runs(benchmark, newest_first=True):
        # personnel_cards selects which fields it scores from the run's rules.
        scorer.rules = rules_of_test(test_id, tests)
        for object_id, _record, answer, truth in iter_run_inputs(run_dir, test_id):
            if tried >= MAX_INPUTS_TRIED:
                break
            tried += 1
            try:
                score = scorer.score_request_answer(object_id, answer, truth)
            except Exception as error:
                errors.append("%s/%s: %s: %s"
                              % (test_id, object_id, type(error).__name__, error))
                continue
            if isinstance(score, dict):
                return "%s/%s" % (test_id, object_id), score
        if tried >= MAX_INPUTS_TRIED:
            break

    if errors:
        pytest.fail("%s scored none of the %d stored inputs tried:%s"
                    % (benchmark, tried,
                       "".join("\n  " + line for line in errors[:5])))
    pytest.skip("no stored input with a ground truth found for %s" % benchmark)


@pytest.mark.parametrize("benchmark", _real_benchmarks())
def test_score_request_answer_records_field_scores(benchmark):
    where, score = _first_score(benchmark)

    assert "field_scores" in score, (
        "%s: score_request_answer returned %s without field_scores. Record what the "
        "scorer compared, keyed by field, so a comparison view does not have to invent "
        "its own diff." % (where, sorted(score)))

    fields = score["field_scores"]
    assert isinstance(fields, dict), "%s: field_scores is %s, expected a dict" % (
        where, type(fields).__name__)

    for key, row in fields.items():
        at = "%s field_scores[%r]" % (where, key)
        assert isinstance(row, dict), "%s is %s, expected a dict" % (at, type(row).__name__)
        for required in ("response", "ground_truth", "score"):
            assert required in row, "%s has no %r (has %s)" % (at, required, sorted(row))
        value = row["score"]
        assert value is None or (isinstance(value, (int, float))
                                 and not isinstance(value, bool)), (
            "%s has score %r; expected a number, or None where the scorer assigns no "
            "per-field similarity" % (at, value))


@pytest.mark.parametrize("benchmark", _real_benchmarks())
def test_score_is_json_serializable(benchmark):
    where, score = _first_score(benchmark)
    try:
        json.dumps(score)
    except TypeError as error:
        pytest.fail(
            "%s: the score does not serialize (%s). Benchmark.save_answer writes it "
            "verbatim into the stored answer, so this is a run-time crash: report plain "
            "strings and numbers, not the objects the scorer compared." % (where, error))
