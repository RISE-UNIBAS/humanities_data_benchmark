"""Scoring tests for bibliographic_data.

score_request_answer aligns response entries to ground-truth entries in page order, looks up
every terminal ground-truth field outside `metadata` at the same path in the aligned response,
and averages their fuzzy similarity.
"""
import copy
import importlib
import json
import os

import pytest

BibliographicData = importlib.import_module("benchmarks.bibliographic_data.benchmark").BibliographicData

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "bibliographic_data", "ground_truths")


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(BibliographicData)


class TestScoreRequestAnswer:
    def test_relation_is_the_reviewed_id(self, scorer, response):
        gt = {"entries": [{"id": "5", "title": "A"}, {"id": "6", "relation": "5"}]}
        result = scorer.score_request_answer("page", response(parsed=copy.deepcopy(gt)), gt)
        assert result["field_scores"]["entries[1].relation"]["score"] == 1.0
        assert result["fuzzy"] == 1.0

    def test_missed_entry_costs_only_itself(self, scorer, response):
        gt = {"entries": [{"id": "1", "title": "Alpha"}, {"id": "2", "title": "Beta"}, {"id": "3", "title": "Gamma"}]}
        pred = {"entries": [{"id": "1", "title": "Alpha"}, {"id": "3", "title": "Gamma"}]}
        result = scorer.score_request_answer("page", response(parsed=pred), gt)
        assert result["field_scores"]["entries[2].title"]["score"] == 1.0
        assert result["field_scores"]["entries[1].title"]["score"] == 0.0
        assert result["fuzzy"] == pytest.approx(4 / 6)

    def test_extra_entry_is_not_scored(self, scorer, response):
        gt = {"entries": [{"id": "1", "title": "Alpha"}, {"id": "2", "title": "Beta"}]}
        pred = {"entries": [{"id": "1", "title": "Alpha"}, {"id": "x", "title": "Relevant articles"},
                            {"id": "2", "title": "Beta"}]}
        assert scorer.score_request_answer("page", response(parsed=pred), gt)["fuzzy"] == 1.0

    def test_alignment_keeps_page_order(self, scorer, response):
        gt = {"entries": [{"title": "Alpha"}, {"title": "Beta"}]}
        pred = {"entries": [{"title": "Beta"}, {"title": "Alpha"}]}
        # Only one of the two can be matched without crossing.
        assert scorer.score_request_answer("page", response(parsed=pred), gt)["fuzzy"] == pytest.approx(0.5)

    def test_single_key_wrapper_is_unwrapped(self, scorer, response):
        gt = {"entries": [{"id": "1", "title": "Alpha"}]}
        pred = {"document": {"metadata": {}, "entries": [{"id": "1", "title": "Alpha"}]}}
        assert scorer.score_request_answer("page", response(parsed=pred), gt)["fuzzy"] == 1.0

    def test_unparseable_response_misses_every_field(self, scorer, response):
        gt = {"entries": [{"id": "1", "title": "Alpha"}]}
        result = scorer.score_request_answer("page", response(parsed=None, text="not json"), gt)
        assert result["fuzzy"] == 0.0

    def test_unparseable_answers_are_scored(self):
        assert BibliographicData.score_unparseable_as_miss is True

    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_every_ground_truth_matches_itself(self, scorer, response, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        assert scorer.score_request_answer(name, response(parsed=copy.deepcopy(gt)), gt)["fuzzy"] == 1.0

    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_relations_are_id_strings(self, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        bad = [e.get("id") for e in gt["entries"] if "relation" in e and not isinstance(e["relation"], str)]
        assert not bad, f"relation must be the reviewed entry's id string: {bad}"


class TestPromptKwargs:
    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_printed_page_matches_ground_truth(self, scorer, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        assert scorer.get_prompt_kwargs(name, [])["printed_page_number"] == gt["metadata"]["page_number"]

    def test_prompt_v2_formats(self, scorer):
        path = os.path.join(GROUND_TRUTHS, "..", "prompts", "prompt_v2.txt")
        with open(path, encoding="utf-8") as f:
            prompt = f.read().format(**scorer.get_prompt_kwargs("page_2", []))
        assert "page number of this page is 1." in prompt
