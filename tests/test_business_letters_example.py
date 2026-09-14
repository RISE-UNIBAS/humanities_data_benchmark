"""The worked example's reporting rules.

The script ships inside the dataset and is the one place the schema is exercised the way
an analyst would exercise it, so its arithmetic is less interesting than its refusals.
Four things it must not do, each of which would produce a plausible-looking wrong number:

  1. Count an unscored request as zero correct extractions.
  2. Divide a cell's whole spend by a subset's true positives.
  3. Report a ratio when the true positives are zero.
  4. Present a $0.00 price from the pricing table as a free model.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import importlib.util
from pathlib import Path

import pytest

_PATH = (Path(__file__).parent.parent / "scripts" / "export_dataset" / "examples"
         / "business_letters_cost.py")
_spec = importlib.util.spec_from_file_location("business_letters_cost", _PATH)
example = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(example)


def _run(run_id="T0001@2026-01-01", provider="openai", model="gpt-4o", hidden=False):
    return {"run_id": run_id, "benchmark": "business_letters", "date": run_id.split("@")[1],
            "configured_provider": provider, "configured_model": model, "hidden": hidden}


def _request(run_id, object_id, cost):
    return {"run_id": run_id, "object_id": object_id, "derived_total_cost_usd": cost,
            "stored_estimated_cost_usd": cost, "response_model": "gpt-4o"}


def _analyse(runs, requests, tp, **kw):
    kw.setdefault("min_coverage", 0.0)
    return example.analyse(runs, requests, tp, "derived_total_cost_usd", **kw)


def test_a_complete_cohort_is_labelled_as_one():
    runs = [_run()]
    requests = [_request("T0001@2026-01-01", "a", 1.0), _request("T0001@2026-01-01", "b", 1.0)]
    tp = {("T0001@2026-01-01", "a"): 2.0, ("T0001@2026-01-01", "b"): 2.0}
    cells, _ = _analyse(runs, requests, tp)
    assert cells[0]["ratio_basis"] == "complete_cohort"
    assert cells[0]["usd_per_correct_extraction"] == 0.5
    assert cells[0]["true_positives"] == 4


def test_an_unscored_request_is_excluded_not_counted_as_zero():
    """Counting it as zero correct would make this cell look twice as expensive."""
    runs = [_run()]
    requests = [_request("T0001@2026-01-01", "a", 1.0), _request("T0001@2026-01-01", "b", 1.0)]
    tp = {("T0001@2026-01-01", "a"): 2.0}          # b was never scored
    cells, _ = _analyse(runs, requests, tp)
    cell = cells[0]
    assert cell["ratio_basis"] == "matched_subset"
    assert cell["usd_per_correct_extraction"] == 0.5, (
        "the ratio must use only the scored request's own cost, not the cell's spend")
    assert cell["observed_spend_usd"] == 2.0, "observed spend still covers both requests"
    assert cell["scored_coverage"] == 0.5


def test_the_ratio_never_divides_total_spend_by_a_subset_denominator():
    runs = [_run()]
    requests = [_request("T0001@2026-01-01", "a", 1.0),
                _request("T0001@2026-01-01", "b", 99.0)]
    tp = {("T0001@2026-01-01", "a"): 1.0}
    cell = _analyse(runs, requests, tp)[0][0]
    assert cell["usd_per_correct_extraction"] == 1.0, (
        "numerator and denominator must come from exactly the same requests")
    assert cell["observed_spend_usd"] == 100.0


def test_no_true_positives_returns_null_with_a_reason():
    runs = [_run()]
    requests = [_request("T0001@2026-01-01", "a", 1.0)]
    tp = {("T0001@2026-01-01", "a"): 0.0}
    cell = _analyse(runs, requests, tp)[0][0]
    assert cell["usd_per_correct_extraction"] is None
    assert cell["ratio_unavailable_code"] == "no_true_positives"


def test_no_eligible_request_returns_null_with_a_reason():
    runs = [_run()]
    requests = [_request("T0001@2026-01-01", "a", None)]
    cell = _analyse(runs, requests, {})[0][0]
    assert cell["usd_per_correct_extraction"] is None
    assert cell["ratio_unavailable_code"] == "no_eligible"
    assert cell["observed_spend_usd"] is None


def test_coverage_below_the_threshold_withholds_the_ratio():
    runs = [_run()]
    requests = [_request("T0001@2026-01-01", str(i), 1.0) for i in range(10)]
    tp = {("T0001@2026-01-01", "0"): 5.0}
    cell = example.analyse(runs, requests, tp, "derived_total_cost_usd",
                           min_coverage=0.5)[0][0]
    assert cell["usd_per_correct_extraction"] is None
    assert cell["ratio_unavailable_code"] == "low_coverage"
    assert cell["eligible_coverage"] == 0.1


def test_a_zero_price_is_flagged_rather_than_reported_as_cheapest():
    """One pricing entry resolves to $0.00/$0.00 from a bad scrape."""
    runs = [_run(provider="cohere", model="command-a-vision-07-2025")]
    requests = [_request("T0001@2026-01-01", "a", 0.0)]
    tp = {("T0001@2026-01-01", "a"): 3.0}
    cell = _analyse(runs, requests, tp)[0][0]
    assert cell["usd_per_correct_extraction"] == 0.0
    assert cell["flag"] == "zero_priced"


def test_hidden_runs_are_excluded_by_default():
    runs = [_run(), _run(run_id="T0002@2026-01-01", hidden=True)]
    requests = [_request("T0001@2026-01-01", "a", 1.0),
                _request("T0002@2026-01-01", "a", 1.0)]
    tp = {("T0001@2026-01-01", "a"): 1.0, ("T0002@2026-01-01", "a"): 1.0}
    cells, meta = _analyse(runs, requests, tp)
    assert len(cells) == 1 and meta["runs_excluded_as_hidden"] == 1

    cells, _ = _analyse(runs, requests, tp, include_hidden=True)
    assert len(cells) == 1 and cells[0]["n_saved_requests"] == 2


def test_an_unresolved_visibility_is_not_treated_as_visible():
    """`hidden` is null when the benchmark metadata would not load. Not a licence."""
    runs = [_run(run_id="T0003@2026-01-01", hidden=None)]
    requests = [_request("T0003@2026-01-01", "a", 1.0)]
    cells, meta = _analyse(runs, requests, {})
    assert cells == [] and meta["runs_excluded_as_hidden"] == 1


def test_grouping_splits_by_provider_and_date():
    runs = [_run(), _run(run_id="T0002@2026-02-01", provider="genai", model="gemini")]
    requests = [_request("T0001@2026-01-01", "a", 1.0),
                _request("T0002@2026-02-01", "a", 2.0)]
    tp = {("T0001@2026-01-01", "a"): 1.0, ("T0002@2026-02-01", "a"): 1.0}
    cells, _ = _analyse(runs, requests, tp)
    assert [(c["provider"], c["date"]) for c in cells] == [
        ("genai", "2026-02-01"), ("openai", "2026-01-01")]
