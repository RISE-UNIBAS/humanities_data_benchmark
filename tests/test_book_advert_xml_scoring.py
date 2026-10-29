"""Scoring tests for book_advert_xml.

score_request_answer diffs the input against the reference and against the answer, after the
same normalisation (whitespace removed, Mac Roman mojibake repaired, closing tags after text
that follows a closing tag moved up to it), and scores the F1 of matched token edits.
score_benchmark averages the advert F1 (f1_macro) and pools the edit counts (f1_micro).
"""
import copy
import importlib
import json
import os

import pytest

module = importlib.import_module("benchmarks.book_advert_xml.benchmark")
BookAdvertXml = module.BookAdvertXml

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "book_advert_xml", "ground_truths")

INPUT = "<ITEM>Bey Herrn X: <BIBL><TITLE>Bibel</TITLE> <PRIZE>2. fl.</PRICE></BIBL> und <BIBL><TITLE>Psalter</TITLE></ITEM>"
REFERENCE = "<ITEM>Bey Herrn X: <BIBL><TITLE>Bibel</TITLE> <PRIZE>2. fl.</PRIZE></BIBL> und <BIBL><TITLE>Psalter</TITLE></BIBL></ITEM>"


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(BookAdvertXml, load_input=lambda name: INPUT)


def score(scorer, response, fixed_xml, reference=REFERENCE):
    return scorer.score_request_answer("advert", response(parsed={"fixed_xml": fixed_xml}), {"fixed_xml": reference})


class TestScoreRequestAnswer:
    def test_reference_scores_one(self, scorer, response):
        result = score(scorer, response, REFERENCE)
        assert (result["f1_score"], result["true_positives"], result["false_positives"], result["false_negatives"]) == (1.0, 2, 0, 0)

    def test_unchanged_input_scores_zero(self, scorer, response):
        result = score(scorer, response, INPUT)
        assert (result["f1_score"], result["true_positives"], result["false_negatives"]) == (0.0, 0, 2)

    def test_half_the_fixes(self, scorer, response):
        answer = INPUT.replace("</TITLE></ITEM>", "</TITLE></BIBL></ITEM>")
        result = score(scorer, response, answer)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (1, 0, 1)
        assert result["f1_score"] == pytest.approx(2 / 3)

    def test_mismatched_price_pair_may_be_fixed_either_way(self, scorer, response):
        answer = REFERENCE.replace("<PRIZE>2. fl.</PRIZE>", "<PRICE>2. fl.</PRICE>")
        assert score(scorer, response, answer)["f1_score"] == 1.0

    def test_renaming_a_consistent_pair_is_an_edit(self, scorer, response):
        reference = INPUT.replace("</PRICE>", "</PRIZE>")
        answer = reference.replace("<TITLE>Bibel</TITLE>", "<AUTHOR>Bibel</AUTHOR>")
        result = score(scorer, response, answer, reference=reference)
        assert result["false_positives"] == 2

    def test_text_changes_are_false_positives(self, scorer, response):
        result = score(scorer, response, REFERENCE.replace("Bey Herrn", "Bei Herrn"))
        assert (result["true_positives"], result["false_positives"]) == (2, 1)

    def test_whitespace_is_ignored(self, scorer, response):
        assert score(scorer, response, REFERENCE.replace("> <", ">\n   <").replace(" ", "  "))["f1_score"] == 1.0

    def test_closing_tag_position_in_trailing_text_is_ignored(self, make_scorer, response):
        source = "<ITEM><BIBL><TITLE>A</TITLE>, gebunden. <BIBL><TITLE>B</TITLE></BIBL></ITEM>"
        reference = "<ITEM><BIBL><TITLE>A</TITLE></BIBL>, gebunden. <BIBL><TITLE>B</TITLE></BIBL></ITEM>"
        answer = "<ITEM><BIBL><TITLE>A</TITLE>, gebunden.</BIBL> <BIBL><TITLE>B</TITLE></BIBL></ITEM>"
        s = make_scorer(BookAdvertXml, load_input=lambda name: source)
        assert score(s, response, answer, reference=reference)["f1_score"] == 1.0

    def test_mojibake_repair_is_not_an_edit(self, make_scorer, response):
        source = "<ITEM>B√ºcher <TITLE>Bibel</ITEM>"
        reference = "<ITEM>B√ºcher <TITLE>Bibel</TITLE></ITEM>"
        s = make_scorer(BookAdvertXml, load_input=lambda name: source)
        assert score(s, response, "<ITEM>Bücher <TITLE>Bibel</TITLE></ITEM>", reference=reference)["f1_score"] == 1.0

    def test_escaping_an_ampersand_is_one_edit(self, make_scorer, response):
        s = make_scorer(BookAdvertXml, load_input=lambda name: "<ITEM>A & B</ITEM>")
        result = score(s, response, "<ITEM>A &amp; B</ITEM>", reference="<ITEM>A &amp; B</ITEM>")
        assert (result["true_positives"], result["f1_score"]) == (1, 1.0)

    def test_missing_fixed_xml_misses_every_edit(self, scorer, response):
        result = scorer.score_request_answer("advert", response(parsed={}), {"fixed_xml": REFERENCE})
        assert (result["f1_score"], result["false_negatives"]) == (0.0, 2)

    def test_unparseable_response(self, scorer, response):
        result = scorer.score_request_answer("advert", response(parsed=None, text="not json"), {"fixed_xml": REFERENCE})
        assert (result["f1_score"], result["false_negatives"]) == (0.0, 2)

    def test_unparseable_answers_are_scored(self):
        assert BookAdvertXml.score_unparseable_as_miss is True

    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_every_ground_truth_matches_itself(self, make_scorer, response, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        result = make_scorer(BookAdvertXml).score_request_answer(name, response(parsed=copy.deepcopy(gt)), gt)
        assert result["f1_score"] == 1.0
        assert result["false_positives"] == result["false_negatives"] == 0


class TestScoreBenchmark:
    def test_empty(self, scorer):
        assert scorer.score_benchmark([]) == {"f1_macro": 0.0, "f1_micro": 0.0}

    def test_macro_averages_adverts_and_micro_pools_edits(self, scorer):
        scores = [
            {"f1_score": 1.0, "true_positives": 1, "false_positives": 0, "false_negatives": 0},
            {"f1_score": 0.0, "true_positives": 0, "false_positives": 3, "false_negatives": 3},
        ]
        result = scorer.score_benchmark(scores)
        assert result["f1_macro"] == pytest.approx(0.5)
        assert result["f1_micro"] == pytest.approx(0.25)
        assert (result["total_tp"], result["total_fp"], result["total_fn"], result["total_instances"]) == (1, 3, 3, 2)
