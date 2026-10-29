"""Scoring tests for benchmarks/fraktur_adverts (CER + fuzzy).

Covers calculate_cer (note: unlike medieval_manuscripts, an empty reference is always max
error), score_benchmark averaging, the number-prefix parser, the pairing of adverts by
section and number in compare_ads, and every ground-truth file against itself.
"""
import copy
import importlib
import json
import os

import pytest

_fraktur = importlib.import_module("benchmarks.fraktur_adverts.benchmark")
FrakturAdverts = _fraktur.FrakturAdverts
DEFAULT_SECTION = _fraktur.DEFAULT_SECTION


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(FrakturAdverts)


class TestCalculateCer:
    def test_identical_is_zero(self, scorer):
        assert scorer.calculate_cer("hello world", "hello world") == 0.0

    def test_empty_reference_is_max(self, scorer):
        assert scorer.calculate_cer("", "anything") == 1.0
        assert scorer.calculate_cer("", "") == 1.0  # empty ref -> 1.0 even if both empty

    def test_empty_hypothesis_is_max(self, scorer):
        assert scorer.calculate_cer("text", "") == 1.0

    def test_single_substitution(self, scorer):
        assert scorer.calculate_cer("kitten", "sitten") == pytest.approx(1 / 6)

    def test_case_and_whitespace_normalized(self, scorer):
        assert scorer.calculate_cer("Hello   World", "hello world") == 0.0

    def test_capped_at_one(self, scorer):
        assert scorer.calculate_cer("ab", "xyzwvurst") == 1.0


class TestScoreBenchmark:
    def test_empty_returns_worst_cer(self, scorer):
        assert scorer.score_benchmark([]) == {"fuzzy": 0.0, "cer": 1.0}

    def test_averages(self, scorer):
        assert scorer.score_benchmark([{"fuzzy": 1.0, "cer": 0.0}, {"fuzzy": 0.0, "cer": 1.0}]) == {
            "fuzzy": 0.5, "cer": 0.5}


class TestExtractNumberPrefix:
    def test_leading_number(self, scorer):
        assert scorer.extract_number_prefix("16. Bey Hrn. Rudolf") == 16

    def test_leading_whitespace_tolerated(self, scorer):
        assert scorer.extract_number_prefix("  3. etwas") == 3

    def test_no_prefix(self, scorer):
        assert scorer.extract_number_prefix("Bey Hrn. ohne Nummer") is None


class TestScoreRequestAnswerGolden:
    """End-to-end goldens with hand-verified expected scores."""

    def test_standard_match_and_miss(self, scorer, response, metrics):
        section = "Es werden zum Verkauff offerirt"
        gt = {section: [
            {"tags_section": section, "text": "1. Ein schoenes Buch"},
            {"tags_section": section, "text": "2. Ein altes Haus"},
        ]}
        parsed = {"advertisements": [
            {"tags_section": section, "text": "1. Ein schoenes Buch"},  # ad #2 omitted
        ]}
        # ad 1: exact match -> similarity 1.0, cer 0.0
        # ad 2: no response  -> similarity 0.0, cer 1.0
        # averages: fuzzy (1.0+0.0)/2 = 0.5, cer (0.0+1.0)/2 = 0.5
        assert metrics(scorer.score_request_answer("image_1", response(parsed=parsed), gt)) == {"fuzzy": 0.5, "cer": 0.5}

    def test_image_4_default_section_forced(self, scorer, response, metrics):
        gt = {DEFAULT_SECTION: [{"tags_section": DEFAULT_SECTION, "text": "1. Foo"}]}
        # response ad has no tags_section -> image_4 handling forces DEFAULT_SECTION, then matches
        parsed = {"advertisements": [{"text": "1. Foo"}]}
        assert metrics(scorer.score_request_answer("image_4", response(parsed=parsed), gt)) == {"fuzzy": 1.0, "cer": 0.0}

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "fraktur_adverts", "ground_truths")


def ad(section, text):
    return {"tags_section": section, "text": text, "date": "1762-02-11"}


class TestCompareAds:
    def test_pairs_by_section_and_number(self, scorer):
        gt = [ad("Verkauf", "1. Ein Haus"), ad("Verkauf", "2. Ein Garten")]
        response = {"advertisements": [ad("Verkauf", "2. Ein Garten"), ad("Verkauf", "1. Ein Haus")]}
        results = scorer.compare_ads(response, gt, "image_1")
        assert [(r["number"], r["match_found"], r["similarity"]) for r in results] == [(1, True, 1.0), (2, True, 1.0)]

    def test_missing_advert_is_not_found(self, scorer):
        results = scorer.compare_ads({"advertisements": []}, [ad("Verkauf", "1. Ein Haus")], "image_1")
        assert results[0]["match_found"] is False and results[0]["similarity"] == 0.0

    def test_section_name_matches_fuzzily(self, scorer):
        gt = [ad("Es wird zum Verkauf angetragen", "1. Ein Haus")]
        response = {"advertisements": [ad("Es wird zum Verkauff angetragen", "1. Ein Haus")]}
        assert scorer.compare_ads(response, gt, "image_1")[0]["match_found"] is True

    def test_unnumbered_entries_are_not_scored(self, scorer):
        gt = [ad("Nachrichten", "Nachdeme die Stadt"), ad("Verkauf", "1. Ein Haus")]
        assert [r["number"] for r in scorer.compare_ads({"advertisements": []}, gt, "image_1")] == [1]

    def test_extra_response_adverts_cost_nothing(self, scorer):
        gt = [ad("Verkauf", "1. Ein Haus")]
        response = {"advertisements": [ad("Verkauf", "1. Ein Haus"), ad("Verkauf", "2. Erfunden")]}
        assert len(scorer.compare_ads(response, gt, "image_1")) == 1

    def test_image_4_defaults_missing_sections_and_finds_numbers_anywhere(self, scorer):
        gt = [ad("", "1. Ein Haus"), ad(None, "2. Ein Garten")]
        response = {"advertisements": [ad(None, "1. Ein Haus"), ad("Anderswo", "2. Ein Garten")]}
        results = scorer.compare_ads(response, gt, "image_4")
        assert all(r["section"] == DEFAULT_SECTION and r["match_found"] for r in results)

    def test_unusable_response(self, scorer):
        results = scorer.compare_ads(None, [ad("Verkauf", "1. Ein Haus")], "image_1")
        assert results[0]["match_found"] is False


class TestGroundTruth:
    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_every_ground_truth_matches_itself(self, scorer, response, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        result = scorer.score_request_answer(name, response(parsed={"advertisements": copy.deepcopy(gt)}), gt)
        assert (result["fuzzy"], result["cer"]) == (1.0, 0.0)

    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_numbers_are_unique_within_a_section(self, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            entries = json.load(f)
        seen = [(e["tags_section"], e["text"].split(".", 1)[0]) for e in entries
                if (e["text"] or "")[:1].isdigit()]
        assert len(seen) == len(set(seen)), "duplicate advert number in one section"


class TestUnparseable:
    def test_unparseable_answer_misses_every_advert(self, scorer, response):
        assert FrakturAdverts.score_unparseable_as_miss is True
        gt = [ad("Verkauf", "1. Ein Haus"), ad("Verkauf", "2. Ein Garten")]
        result = scorer.score_request_answer("image_1", response(parsed=None, text="prose"), gt)
        assert (result["fuzzy"], result["cer"]) == (0.0, 1.0)
