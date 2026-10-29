"""Benchmark versions per run and run counts per version: a recorded version wins, else the version
in force at the run's first request; scored with the latest re-scoring since."""
from scripts.compare.generate_version_runs import run_versions
from scripts.results_index import TestCatalog, Version, iter_run_dirs

HISTORY = (Version("0.1.0", "2026-01-01T00:00:00", ()),
           Version("0.2.0", "2026-01-05T15:00:00", ()),
           Version("1.0.0", "2026-02-01T00:00:00", ()))


def _versions(make_corpus, spec):
    catalog = TestCatalog([{"id": "T0001", "name": "letters"}, {"id": "T0002", "name": "letters"}])
    return run_versions(iter_run_dirs(make_corpus(spec)), catalog, history_of=lambda name: HISTORY)


def test_a_run_counts_for_the_version_at_its_first_request(make_corpus):
    counts, runs = _versions(make_corpus, {
        "2026-01-05": {"T0001": {"requests": {"a": {"timestamp": "2026-01-05T16:00:00"},
                                              "b": {"timestamp": "2026-01-05T14:00:00"}}}},
        "2026-01-06": {"T0002": {"requests": {"a": {"timestamp": "2026-01-06T09:00:00"}}}},
    })
    assert counts == {"letters": {"0.1.0": {"runs": 1, "ambiguous": 1}, "0.2.0": {"runs": 1, "ambiguous": 0}}}
    assert runs["2026-01-05/T0001"] == {"made": "0.1.0", "scored": "0.1.0", "basis": "ambiguous", "or": "0.2.0"}
    assert "or" not in runs["2026-01-06/T0002"]


def test_a_run_without_request_times_counts_from_its_date_and_unknown_tests_are_left_out(make_corpus):
    counts, runs = _versions(make_corpus, {
        "2026-03-01": {"T0001": {"scoring": {}}, "T9999": {"requests": {"a": {"timestamp": "2026-03-01T09:00:00"}}}},
        "2026-01-02": {"T0002": {"requests": {"a": "not json"}}},
    })
    assert counts == {"letters": {"0.1.0": {"runs": 1, "ambiguous": 0}, "1.0.0": {"runs": 1, "ambiguous": 0}}}
    assert sorted(runs) == ["2026-01-02/T0002", "2026-03-01/T0001"]


def test_a_recorded_version_wins_and_uncommitted_changes_make_it_ambiguous(make_corpus):
    _, runs = _versions(make_corpus, {"2026-01-05": {
        "T0001": {"requests": {"a": {"timestamp": "2026-01-05T09:00:00"}},
                  "scoring": {"benchmark_version": {"version": "0.2.0", "commit": "c", "uncommitted": []}}},
        "T0002": {"requests": {"a": {"timestamp": "2026-01-05T09:00:00"}},
                  "scoring": {"benchmark_version": {"version": "0.1.0", "commit": "c",
                                                    "uncommitted": ["benchmarks/letters/prompts/new.txt"]}}},
    }})
    assert runs["2026-01-05/T0001"]["made"] == "0.2.0" and runs["2026-01-05/T0001"]["basis"] == "recorded"
    assert runs["2026-01-05/T0002"]["made"] == "0.1.0" and runs["2026-01-05/T0002"]["basis"] == "ambiguous"


def test_a_rescoring_covers_every_run_stored_by_its_day(make_corpus):
    _, runs = _versions(make_corpus, {
        "2026-01-02": {"T0001": {"requests": {"a": {"timestamp": "2026-01-02T09:00:00"}},
                                 "scoring": {"rescored": "letters 1.0.0 on 2026-02-01"}},
                       "T0002": {"requests": {"a": {"timestamp": "2026-01-02T10:00:00"}}}},
        "2026-02-03": {"T0002": {"requests": {"a": {"timestamp": "2026-02-03T10:00:00"}}}},
    })
    assert [runs[k]["scored"] for k in ("2026-01-02/T0001", "2026-01-02/T0002", "2026-02-03/T0002")] == \
        ["1.0.0", "1.0.0", "1.0.0"]
    assert runs["2026-01-02/T0002"]["made"] == "0.1.0"
