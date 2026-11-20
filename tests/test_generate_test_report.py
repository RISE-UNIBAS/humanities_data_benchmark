"""scripts/generate_test_report.py: model output stays text (audit 2026-11-19 F04), every
benchmark's aggregate is shown (F07), and the test config is read as CSV (F10)."""
import csv
from html.parser import HTMLParser
from pathlib import Path

import pytest

from scripts.generate_test_report import generate_html_content, get_test_config

TESTS_CSV = Path(__file__).resolve().parents[1] / "benchmarks" / "benchmarks_tests.csv"


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)


def _report(parsed=None, ground_truth=None, field_scores=None, scoring=None, raw=None):
    request = {"parsed": parsed, "score": {"field_scores": field_scores or {}},
               "raw_response": raw}
    return generate_html_content("T0001", "2026-11-19", {"benchmark": "audit"}, None,
                                 scoring or {}, [{"item_id": "a", "ground_truth": ground_truth,
                                                  "request_data": request}], raw is not None)


def test_model_output_is_shown_as_text_not_markup():
    probe = "</pre><script>alert(1)</script> & <entry>Buch</entry>"
    text = _report(parsed={"text": probe}, ground_truth={"xml": "<entry>Buch</entry>"},
                   field_scores={"<b>f</b>": {"response": probe, "ground_truth": "x", "score": 1}},
                   raw={"content": probe})
    parser = _Tags()
    parser.feed(text)
    assert not {"script", "entry", "b"} & set(parser.tags)
    assert "&lt;entry&gt;Buch&lt;/entry&gt;" in text and "&amp;" in text


@pytest.mark.parametrize("key, value", [("fuzzy", 0.876543), ("cer", 0.123456), ("f1", 0.456789)])
def test_the_aggregate_of_every_ranking_metric_is_shown(key, value):
    text = _report(scoring={key: value})
    summary = text.split("Scoring Summary", 1)[1].split("Individual Results", 1)[0]
    assert format(value, ".3f") in summary


def test_a_zero_aggregate_is_shown():
    text = _report(scoring={"cer": 0.0})
    assert "0.000" in text.split("Scoring Summary", 1)[1].split("Individual Results", 1)[0]


def test_the_config_matches_the_csv_for_every_test():
    with TESTS_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        config = get_test_config(row["id"])
        assert (config["benchmark"], config["rules"], config["role_description"],
                config["prompt_file"], config["legacy_test"]) == (
            row["name"], row["rules"], row["role_description"], row["prompt_file"],
            row["legacy_test"] or "false"), row["id"]
