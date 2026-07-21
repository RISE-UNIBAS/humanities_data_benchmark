"""Scoring tests for benchmarks/business_letters.

Covers:
  - score_benchmark: macro/micro F1 aggregation over the three categories
    (send_date, sender_persons, receiver_persons).
  - score_request_answer: an end-to-end golden with a hand-verified score,
    exercising person matching and the inferred-person exclusion.
  - skip_object: the signature skip rules (skip_signatures / skip_non_signatures).

Person/letter ground truth is provided via a temporary benchmark_dir holding the
empty persons.json the scorer expects (and per-object letter files for skip tests).
"""
import importlib
import json

import pytest

BusinessLetters = importlib.import_module("benchmarks.business_letters.benchmark").BusinessLetters


def _score(sd=(0, 0, 0), sp=(0, 0, 0), rp=(0, 0, 0)):
    """Build a per-request score dict from (tp, fp, fn) triples."""
    return {
        "send_date_tp": sd[0], "send_date_fp": sd[1], "send_date_fn": sd[2],
        "sender_persons_tp": sp[0], "sender_persons_fp": sp[1], "sender_persons_fn": sp[2],
        "receiver_persons_tp": rp[0], "receiver_persons_fp": rp[1], "receiver_persons_fn": rp[2],
    }


@pytest.fixture
def benchmark_dir(tmp_path):
    """A benchmark dir with the empty persons.json that score_request_answer loads."""
    gt = tmp_path / "ground_truths"
    gt.mkdir()
    (gt / "persons.json").write_text("[]", encoding="utf-8")
    return tmp_path


class TestScoreBenchmark:
    @pytest.fixture
    def scorer(self, make_scorer):
        return make_scorer(BusinessLetters)

    def test_empty(self, scorer):
        assert scorer.score_benchmark([]) == {"f1_macro": 0.0, "f1_micro": 0.0}

    def test_perfect(self, scorer):
        result = scorer.score_benchmark([_score(sd=(1, 0, 0), sp=(2, 0, 0), rp=(1, 0, 0))])
        assert result == {"f1_macro": 1.0, "f1_micro": 1.0}

    def test_none_scores_skipped(self, scorer):
        perfect = _score(sd=(1, 0, 0), sp=(2, 0, 0), rp=(1, 0, 0))
        assert scorer.score_benchmark([perfect, None]) == {"f1_macro": 1.0, "f1_micro": 1.0}

    def test_macro_and_micro_diverge(self, scorer):
        # send_date f1=1, sender_persons f1=0 (all FN), receiver f1=1
        result = scorer.score_benchmark([_score(sd=(1, 0, 0), sp=(0, 0, 4), rp=(1, 0, 0))])
        assert result["f1_macro"] == pytest.approx(0.67)   # mean(1, 0, 1)
        assert result["f1_micro"] == pytest.approx(0.5)    # tp=2, fp=0, fn=4 -> P=1, R=1/3


class TestScoreRequestAnswerGolden:
    def test_golden(self, make_scorer, response, benchmark_dir):
        scorer = make_scorer(BusinessLetters, benchmark_dir=str(benchmark_dir))
        ground_truth = {
            "send_date": "1947-03-05",
            "letter_title": "Test",
            # "<Some Boss>" is inferred_from_function -> excluded from ground-truth scoring
            "sender_persons": ["Hans Mueller", "<Some Boss>"],
            "receiver_persons": ["Anna Meier", "Karl Weber"],
            "has_signatures": "TRUE",
        }
        parsed = {"metadata": {
            "send_date": "1947-03-05",                # matches -> send_date tp=1
            "sender_persons": ["Hans Mueller"],        # matches (Some Boss excluded) -> sender tp=1
            "receiver_persons": ["Anna Meier"],        # Karl Weber missing -> receiver tp=1, fn=1
        }}
        result = scorer.score_request_answer("letter_1", response(parsed=parsed), ground_truth)
        assert result == {
            "send_date_tp": 1, "send_date_fp": 0, "send_date_fn": 0,
            "sender_persons_tp": 1, "sender_persons_fp": 0, "sender_persons_fn": 0,
            "receiver_persons_tp": 1, "receiver_persons_fp": 0, "receiver_persons_fn": 1,
        }


class TestSkipObject:
    def _write_letter(self, benchmark_dir, name, has_signatures):
        (benchmark_dir / "ground_truths" / f"{name}.json").write_text(
            json.dumps({"has_signatures": has_signatures, "sender_persons": [], "receiver_persons": []}),
            encoding="utf-8",
        )

    def test_no_rules_never_skips(self, make_scorer, benchmark_dir):
        scorer = make_scorer(BusinessLetters, rules=None, benchmark_dir=str(benchmark_dir))
        assert scorer.skip_object("anything") is False

    def test_skip_signatures_skips_signed(self, make_scorer, benchmark_dir):
        self._write_letter(benchmark_dir, "sig", "TRUE")
        scorer = make_scorer(BusinessLetters, rules={"skip_signatures": True}, benchmark_dir=str(benchmark_dir))
        assert scorer.skip_object("sig") is True

    def test_skip_signatures_keeps_unsigned(self, make_scorer, benchmark_dir):
        self._write_letter(benchmark_dir, "nosig", "FALSE")
        scorer = make_scorer(BusinessLetters, rules={"skip_signatures": True}, benchmark_dir=str(benchmark_dir))
        assert not scorer.skip_object("nosig")

    def test_skip_non_signatures_skips_unsigned(self, make_scorer, benchmark_dir):
        self._write_letter(benchmark_dir, "nosig", "FALSE")
        scorer = make_scorer(BusinessLetters, rules={"skip_non_signatures": True}, benchmark_dir=str(benchmark_dir))
        assert scorer.skip_object("nosig") is True