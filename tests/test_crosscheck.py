"""Logic of `scripts.export_dataset.crosscheck.compare`, without a built corpus."""
import pytest

from scripts.export_dataset.crosscheck import compare

RUN_ID = "T0001@2026-01-01"


def _run(**cost):
    row = {"run_id": RUN_ID, "benchmark": "company_lists", "hidden": False,
           "configured_provider": "genai", "configured_model": "gemini-3.8-flash",
           "recorded_total_cost_usd": 1.0, "recorded_total_input_tokens": 10,
           "recorded_total_output_tokens": 20, "recorded_total_reasoning_tokens": None,
           "recorded_reasoning_cost_usd": None}
    row.update(cost)
    return row


def _frontend(**cost):
    summary = {"total_cost_usd": 1.0, "total_input_tokens": 10, "total_output_tokens": 20}
    summary.update(cost)
    return {RUN_ID: {"benchmark": "company_lists", "hidden": False,
                     "config": {"provider": "genai", "model": "gemini-3.8-flash"},
                     "scoring": {"cost_summary": summary}}}


def _checks(run, frontend):
    findings, shared = compare([run], [], [], frontend)
    assert shared == 1
    return [f["check"] for f in findings]


def test_matching_reasoning_summaries_agree():
    run = _run(recorded_total_reasoning_tokens=500, recorded_reasoning_cost_usd=0.25)
    assert _checks(run, _frontend(total_reasoning_tokens=500,
                                  reasoning_cost_usd=0.25)) == []


def test_runs_with_no_reasoning_on_either_side_agree():
    assert _checks(_run(), _frontend()) == []


@pytest.mark.parametrize("run,frontend", [
    (_run(recorded_total_reasoning_tokens=500), _frontend(total_reasoning_tokens=400)),
    (_run(), _frontend(total_reasoning_tokens=400)),
    (_run(recorded_reasoning_cost_usd=0.25), _frontend(reasoning_cost_usd=None)),
])
def test_a_reasoning_disagreement_is_reported(run, frontend):
    assert _checks(run, frontend) == ["recorded_cost"]
