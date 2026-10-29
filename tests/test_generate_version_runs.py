"""Run counts per benchmark version: each run counts for the version in force at its first request."""
from scripts.compare.generate_version_runs import version_runs
from scripts.results_index import TestCatalog, Version, iter_run_dirs

HISTORY = (Version("0.1.0", "2026-01-01T00:00:00", ()),
           Version("0.2.0", "2026-01-05T15:00:00", ()),
           Version("1.0.0", "2026-02-01T00:00:00", ()))


def _counts(make_corpus, spec):
    catalog = TestCatalog([{"id": "T0001", "name": "letters"}, {"id": "T0002", "name": "letters"}])
    return version_runs(iter_run_dirs(make_corpus(spec)), catalog, history_of=lambda name: HISTORY)


def test_a_run_counts_for_the_version_at_its_first_request(make_corpus):
    counts = _counts(make_corpus, {
        "2026-01-05": {"T0001": {"requests": {"a": {"timestamp": "2026-01-05T16:00:00"},
                                              "b": {"timestamp": "2026-01-05T14:00:00"}}}},
        "2026-01-06": {"T0002": {"requests": {"a": {"timestamp": "2026-01-06T09:00:00"}}}},
    })
    assert counts == {"letters": {"0.1.0": {"runs": 1, "ambiguous": 1}, "0.2.0": {"runs": 1, "ambiguous": 0}}}


def test_a_run_without_request_times_counts_from_its_date_and_unknown_tests_are_left_out(make_corpus):
    counts = _counts(make_corpus, {
        "2026-03-01": {"T0001": {"scoring": {}}, "T9999": {"requests": {"a": {"timestamp": "2026-03-01T09:00:00"}}}},
        "2026-01-02": {"T0002": {"requests": {"a": "not json"}}},
    })
    assert counts == {"letters": {"0.1.0": {"runs": 1, "ambiguous": 0}, "1.0.0": {"runs": 1, "ambiguous": 0}}}
