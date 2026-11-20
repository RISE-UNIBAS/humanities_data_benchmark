"""scripts/rescore.py: a check that compared nothing or failed is not a success (audit
2026-11-19 F05), and --write puts each score in its own request file (F09)."""
import contextlib
import io
import json
from types import SimpleNamespace
from unittest.mock import patch

from scripts import rescore


def _check(targets, **patches):
    args = SimpleNamespace(run=None, benchmark="company_lists", limit=0, dump=None)
    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(rescore, "iter_runs", return_value=targets))
        for name, value in patches.items():
            stack.enter_context(patch.object(rescore, name, **value))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        return rescore.check(args, {})


def test_a_scorer_that_does_not_load_fails_the_check(tmp_path):
    code = _check([(tmp_path, "T9999", "company_lists")],
                  load_scorer={"side_effect": ImportError("missing scorer")})
    assert code == 1


def _scored_run(tmp_path, fresh_scores):
    stored = {"a": {"fuzzy": 1.0}, "b": {"fuzzy": 1.0}}
    requests = [(o, {"score": stored[o]}, fresh) for o, fresh in fresh_scores.items()]
    return dict(load_scorer={"return_value": SimpleNamespace()},
                rules_of_test={"return_value": None},
                rescore_requests={"return_value": requests})


def test_a_request_whose_scorer_raises_fails_the_check(tmp_path):
    patches = _scored_run(tmp_path, {"a": {"fuzzy": 1.0}, "b": {"__error": "KeyError: x"}})
    assert _check([(tmp_path, "T9999", "company_lists")], **patches) == 1


def test_matching_scores_pass_the_check(tmp_path):
    patches = _scored_run(tmp_path, {"a": {"fuzzy": 1.0}, "b": {"fuzzy": 1.0}})
    assert _check([(tmp_path, "T9999", "company_lists")], **patches) == 0


def test_a_check_that_compared_nothing_fails(tmp_path):
    patches = dict(load_scorer={"return_value": SimpleNamespace()},
                   rules_of_test={"return_value": None},
                   rescore_requests={"return_value": [("a", {"score": None}, None)]})
    assert _check([(tmp_path, "T9999", "company_lists")], **patches) == 1


def test_a_requested_run_that_does_not_exist_fails(tmp_path):
    args = SimpleNamespace(run="2000-01-01/T0001", benchmark=None, limit=0, dump=None)
    with contextlib.redirect_stdout(io.StringIO()):
        assert rescore.check(args, {}) == 1


def test_write_puts_each_score_in_its_own_file_when_one_id_ends_another(tmp_path):
    folder = tmp_path / "2026-11-19" / "T9999"
    folder.mkdir(parents=True)
    for name in ("1", "page_1"):
        (folder / ("request_T9999_%s.json" % name)).write_text(
            json.dumps({"score": {"fuzzy": 0.0}}), encoding="utf-8")
    (folder / "scoring.json").write_text(json.dumps({"fuzzy": 0.5}), encoding="utf-8")
    fresh = {"1": {"fuzzy": 0.25}, "page_1": {"fuzzy": 0.75}}
    args = SimpleNamespace(benchmark="audit", verify=False, label="audit 2.0.0")
    with patch.object(rescore, "iter_runs", return_value=[(folder, "T9999", "audit")]), \
         patch.object(rescore, "load_scorer", return_value=SimpleNamespace()), \
         patch.object(rescore, "rules_of_test", return_value=None), \
         patch.object(rescore, "rescore_run", return_value=(fresh, {"fuzzy": 0.5})), \
         contextlib.redirect_stdout(io.StringIO()):
        rescore.verify_or_write(args, {})

    def written(name):
        path = folder / ("request_T9999_%s.json" % name)
        return json.loads(path.read_text(encoding="utf-8"))["score"]["fuzzy"]
    assert (written("1"), written("page_1")) == (0.25, 0.75)


def test_a_parsed_answer_left_unscored_by_a_failed_scorer_is_rescored(tmp_path):
    """The runner leaves such a run unfinished; --write must be able to supply the score."""
    record = {"score": None, "parsed": {"rows": []}}
    answer = SimpleNamespace(parsed={"rows": []})
    scorer = SimpleNamespace(score_unparseable_as_miss=False,
                             score_request_answer=lambda *a: {"fuzzy": 0.5})
    with patch.object(rescore, "iter_run_inputs", return_value=[("a", record, answer, {})]):
        assert list(rescore.rescore_requests(tmp_path, "T9999", scorer)) == [
            ("a", record, {"fuzzy": 0.5})]
