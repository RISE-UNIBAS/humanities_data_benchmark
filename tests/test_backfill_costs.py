"""Tests for `scripts/backfill_costs.py`.

The script rewrites tracked data in bulk, so these pin the properties that make that
safe: nothing is written until validation passes, a touched file differs only in the
intended keys and keeps its byte style, a provider-reported cost is never replaced by a
derived one, a dry run previews exactly what an apply would do, and a run's totals are
rewritten only when every one of its requests could be accounted for.

Pricing is stubbed, so these test the script's decisions, not `scripts/data/pricing.json`.
"""
import json
import os
from types import SimpleNamespace

import pytest

from scripts import backfill_costs as bc


# --------------------------------------------------------------------------- fixtures

class FakePrice(SimpleNamespace):
    pass


def price(inp, out):
    return FakePrice(input_price=inp, output_price=out, bucket_date="2026-01-01", age_days=0)


@pytest.fixture
def prices(monkeypatch):
    """(provider, model) -> price, or absent to mean 'nothing in the window'."""
    table = {}

    def lookup(provider, model, run_date, max_age_days=None):
        return table.get((provider, model))

    monkeypatch.setattr(bc, "price_for", lookup)
    return table


def write_json(path, payload, ensure_ascii=True, newline="\r\n", trailing=""):
    """Write the way the runner does: indent=4, CRLF, no trailing newline."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(payload, indent=4, ensure_ascii=ensure_ascii)
    if newline != "\n":
        text = text.replace("\n", newline)
    with open(path, "wb") as fh:
        fh.write((text + trailing).encode("utf-8"))


def request_payload(provider="genai", model="m", usage=None, raw_response=None, text="hi"):
    doc = {"text": text, "model": model, "provider": provider,
           "finish_reason": "stop", "usage": usage or {}}
    if raw_response is not None:
        doc["raw_response"] = raw_response
    return doc


def make_run(root, date, test_id, requests, summary=None):
    for name, payload in requests.items():
        write_json(os.path.join(root, date, test_id, "request_%s.json" % name), payload)
    if summary is not None:
        write_json(os.path.join(root, date, test_id, "scoring.json"),
                   {"score": 1.0, "cost_summary": summary})
    return os.path.join(root, date, test_id)


def make_args(results, **kw):
    base = dict(results=str(results), provider=None, date=None, test_id=None,
                apply=False, all_files=False, summaries=False, max_price_age=30,
                verify=False)
    base.update(kw)
    return SimpleNamespace(**base)


def read(path):
    with open(path, "rb") as fh:
        return fh.read()


def usage_of(path):
    return json.loads(read(path).decode("utf-8"))["usage"]


def summary_of(run_dir):
    return json.loads(read(os.path.join(run_dir, "scoring.json")).decode("utf-8"))["cost_summary"]


REASONING_USAGE = {"input_tokens": 100, "output_tokens": 200, "total_tokens": 1300,
                   "input_cost_usd": 0.001, "output_cost_usd": 0.002,
                   "estimated_cost_usd": 0.003}
"""1,000 reasoning tokens outside output_tokens, already costed for input and output."""


# ------------------------------------------------------------------- the five findings

def test_nothing_is_written_when_a_mismatch_is_found(tmp_path, prices):
    """Validation must finish before any write, not report a stop afterwards."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    # a clean file that would otherwise be rewritten, and one whose provider figure
    # contradicts the arithmetic gap
    run = make_run(root, "2026-01-02", "T0001", {
        "clean": request_payload(usage=dict(REASONING_USAGE)),
        "bad": request_payload(usage=dict(REASONING_USAGE), raw_response=json.dumps(
            {"usage_metadata": {"thoughts_token_count": 999}})),
    })
    before = {n: read(os.path.join(run, n)) for n in os.listdir(run)}

    rc = bc.main_with_args(make_args(root, apply=True))

    assert rc == 2
    after = {n: read(os.path.join(run, n)) for n in os.listdir(run)}
    assert after == before, "files were modified despite the stop"


def test_provider_filter_leaves_other_runs_untouched(tmp_path, prices):
    """A scoped run must not rewrite the summary of an unscoped run with zeros."""
    prices[("genai", "m")] = price(10.0, 10.0)
    prices[("openai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    make_run(root, "2026-01-02", "T0001",
             {"a": request_payload(provider="genai", usage=dict(REASONING_USAGE))},
             summary={"total_input_tokens": 100, "total_output_tokens": 200,
                      "total_tokens": 300, "input_cost_usd": 0.001,
                      "output_cost_usd": 0.002, "total_cost_usd": 0.003})
    # A MIXED run is the dangerous case: summing only the matching requests would
    # rewrite the run as though the excluded ones cost nothing.
    other = make_run(root, "2026-01-02", "T0002",
                     {"a": request_payload(provider="openai", usage=dict(REASONING_USAGE)),
                      "b": request_payload(provider="genai", usage=dict(REASONING_USAGE))},
                     summary={"total_input_tokens": 200, "total_output_tokens": 400,
                              "total_tokens": 600, "input_cost_usd": 0.002,
                              "output_cost_usd": 0.004, "total_cost_usd": 0.006})
    before = read(os.path.join(other, "scoring.json"))

    bc.main_with_args(make_args(root, provider=["genai"], summaries=True, apply=True))

    assert read(os.path.join(other, "scoring.json")) == before
    assert summary_of(other)["total_cost_usd"] == 0.006


def test_provider_reported_cost_is_never_replaced(tmp_path, prices):
    """A billed estimated_cost_usd with no components must survive, in file and run."""
    prices[("openrouter", "m")] = price(1.0, 1.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001", {
        "a": request_payload(provider="openrouter", usage={
            "input_tokens": 500, "output_tokens": 500, "total_tokens": 1000,
            "estimated_cost_usd": 0.70}),
    }, summary={"total_cost_usd": 0.70})

    bc.main_with_args(make_args(root, summaries=True, apply=True))

    u = usage_of(os.path.join(run, "request_a.json"))
    assert u["estimated_cost_usd"] == 0.70
    assert "input_cost_usd" not in u, "list-price components replaced a billed figure"
    assert summary_of(run)["total_cost_usd"] == 0.70


def test_dry_run_matches_apply(tmp_path, prices):
    """The preview must count exactly what an apply would change."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    # a stored reasoning cost that the backfill will replace
    stale = dict(REASONING_USAGE, reasoning_tokens=1000, reasoning_cost_usd=0.5)
    make_run(root, "2026-01-02", "T0001", {"a": request_payload(usage=stale)},
             summary={"total_input_tokens": 100, "total_output_tokens": 200,
                      "total_tokens": 300, "input_cost_usd": 0.001,
                      "output_cost_usd": 0.002, "total_cost_usd": 0.503,
                      "total_reasoning_tokens": 1000, "reasoning_cost_usd": 0.5})

    dry = bc.roll_up_summaries(make_args(root, summaries=True), False)
    bc.backfill(make_args(root, apply=True), bc.Stats())
    wet = bc.roll_up_summaries(make_args(root, summaries=True), True)

    assert dry[1] == wet[1], "dry run previewed %d summary changes, apply made %d" % (
        dry[1], wet[1])


def test_verify_honours_filters(tmp_path, prices):
    """A scoped --verify must not fail on requests outside the scope."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    make_run(root, "2026-01-02", "T0001", {"a": request_payload(usage=dict(
        REASONING_USAGE, reasoning_tokens=1000, reasoning_cost_usd=0.01))})
    # deliberately inconsistent, and out of scope for the call below
    make_run(root, "2026-01-03", "T0002", {"a": request_payload(usage={
        "input_tokens": 1, "output_tokens": 1, "total_tokens": 99,
        "reasoning_tokens": 5, "reasoning_cost_usd": 0.0})})

    assert bc.verify(make_args(root, date=["2026-01-02"])) == 0
    assert bc.verify(make_args(root)) == 1


# ------------------------------------------------------------------ core properties

def test_writes_only_the_intended_keys_and_preserve_bytes(tmp_path, prices):
    """A touched file must differ from the original only in the cost keys."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(usage=dict(REASONING_USAGE), text="café — x")})
    path = os.path.join(run, "request_a.json")
    before = json.loads(read(path).decode("utf-8"))

    bc.backfill(make_args(root, apply=True), bc.Stats())

    after = json.loads(read(path).decode("utf-8"))
    assert {k: v for k, v in after.items() if k != "usage"} == \
           {k: v for k, v in before.items() if k != "usage"}
    changed = {k for k in set(after["usage"]) | set(before["usage"])
               if after["usage"].get(k) != before["usage"].get(k)}
    assert changed <= {"reasoning_tokens", "reasoning_cost_usd", "estimated_cost_usd"}
    assert after["text"] == "café — x"


@pytest.mark.parametrize("ensure_ascii", [True, False])
def test_round_trip_preserves_encoding_era(tmp_path, prices, ensure_ascii):
    """Both encoding eras must round-trip; an untouched file stays byte-identical."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    os.makedirs(root / "2026-01-02" / "T0001", exist_ok=True)
    touched = str(root / "2026-01-02" / "T0001" / "request_a.json")
    write_json(touched, request_payload(usage=dict(REASONING_USAGE), text="café"),
               ensure_ascii=ensure_ascii)
    untouched = str(root / "2026-01-02" / "T0001" / "request_b.json")
    write_json(untouched, request_payload(usage={"input_tokens": 1, "output_tokens": 1,
                                                 "total_tokens": 2,
                                                 "input_cost_usd": 0.0,
                                                 "output_cost_usd": 0.0,
                                                 "estimated_cost_usd": 0.0},
                                          text="café"),
               ensure_ascii=ensure_ascii)
    original = read(untouched)

    bc.backfill(make_args(root, apply=True), bc.Stats())

    assert read(untouched) == original
    raw = read(touched)
    assert b"\r\n" in raw and not raw.endswith(b"\n\n")
    has_non_ascii = any(b >= 0x80 for b in raw)
    assert has_non_ascii == (not ensure_ascii)
    assert usage_of(touched)["reasoning_tokens"] == 1000


def test_second_apply_writes_nothing(tmp_path, prices):
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    make_run(root, "2026-01-02", "T0001", {"a": request_payload(usage=dict(REASONING_USAGE))},
             summary={"total_input_tokens": 100, "total_output_tokens": 200,
                      "total_tokens": 300, "input_cost_usd": 0.001,
                      "output_cost_usd": 0.002, "total_cost_usd": 0.003})
    args = make_args(root, summaries=True, apply=True)
    bc.backfill(args, bc.Stats())
    bc.roll_up_summaries(args, True)

    stats = bc.Stats()
    bc.backfill(args, stats)
    _runs, changed, _unrep, _ret, _skip = bc.roll_up_summaries(args, True)

    assert stats.written == 0
    assert changed == 0


def test_unknown_price_records_tokens_but_withholds_cost(tmp_path, prices):
    """Out of window means unknown, not zero: keep the count, leave the money null."""
    root = tmp_path / "results"  # no entry in `prices` -> nothing in the window
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(usage=dict(REASONING_USAGE))})

    bc.backfill(make_args(root, apply=True), bc.Stats())

    u = usage_of(os.path.join(run, "request_a.json"))
    assert u["reasoning_tokens"] == 1000
    assert u["reasoning_cost_usd"] is None
    assert u["estimated_cost_usd"] == pytest.approx(0.003), "estimated must stay input+output"


def test_estimated_cost_is_input_plus_output_plus_reasoning(tmp_path, prices):
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(usage=dict(REASONING_USAGE))})

    bc.backfill(make_args(root, apply=True), bc.Stats())

    u = usage_of(os.path.join(run, "request_a.json"))
    assert u["reasoning_cost_usd"] == pytest.approx(1000 / 1e6 * 10.0)
    assert u["estimated_cost_usd"] == pytest.approx(0.001 + 0.002 + u["reasoning_cost_usd"])
    assert u["input_tokens"] + u["output_tokens"] + u["reasoning_tokens"] == u["total_tokens"]


def test_missing_input_output_cost_is_filled(tmp_path, prices):
    prices[("openai", "m")] = price(2.0, 4.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001", {"a": request_payload(
        provider="openai", usage={"input_tokens": 1_000_000, "output_tokens": 1_000_000,
                                  "total_tokens": 2_000_000})})

    bc.backfill(make_args(root, apply=True), bc.Stats())

    u = usage_of(os.path.join(run, "request_a.json"))
    assert u["input_cost_usd"] == pytest.approx(2.0)
    assert u["output_cost_usd"] == pytest.approx(4.0)
    assert u["estimated_cost_usd"] == pytest.approx(6.0)


def test_no_tokens_means_no_cost_is_invented(tmp_path, prices):
    prices[("openai", "m")] = price(2.0, 4.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001", {"a": request_payload(
        provider="openai", usage={"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})})
    before = read(os.path.join(run, "request_a.json"))

    bc.backfill(make_args(root, apply=True), bc.Stats())

    assert read(os.path.join(run, "request_a.json")) == before


def test_reasoning_reported_inside_output_tokens_is_not_double_counted(tmp_path, prices):
    """openai-family providers report reasoning inside output_tokens; the gap is 0."""
    prices[("openai", "m")] = price(1.0, 1.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001", {"a": request_payload(
        provider="openai",
        usage={"input_tokens": 100, "output_tokens": 900, "total_tokens": 1000,
               "input_cost_usd": 0.0001, "output_cost_usd": 0.0009,
               "estimated_cost_usd": 0.001},
        raw_response=json.dumps({"usage": {"completion_tokens_details":
                                           {"reasoning_tokens": 700}}}))})
    before = read(os.path.join(run, "request_a.json"))

    rc = bc.main_with_args(make_args(root, apply=True))

    assert rc == 0, "a provider reporting reasoning inside output_tokens is not a mismatch"
    assert read(os.path.join(run, "request_a.json")) == before


def test_summary_reasoning_cost_is_null_when_nothing_priced_it(tmp_path, prices):
    root = tmp_path / "results"  # nothing priced
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(usage=dict(REASONING_USAGE))},
                   summary={"total_input_tokens": 100, "total_output_tokens": 200,
                            "total_tokens": 300, "input_cost_usd": 0.001,
                            "output_cost_usd": 0.002, "total_cost_usd": 0.003})
    args = make_args(root, summaries=True, apply=True)
    bc.backfill(args, bc.Stats())
    bc.roll_up_summaries(args, True)

    s = summary_of(run)
    assert s["total_reasoning_tokens"] == 1000
    assert s["reasoning_cost_usd"] is None
    assert s["total_cost_usd"] == pytest.approx(0.003)


# ------------------------------------------------------------------- pricing window

def test_pricing_window_boundary(tmp_path, monkeypatch):
    """A bucket 30 days before the run counts; 31 does not, and neither does a later one."""
    from scripts.ndr_export import pricing_resolver

    table = {"pricing": {
        "2026-01-02": {"genai": {"m": {"input_price": 1.0, "output_price": 2.0}}},
        "2026-03-01": {"genai": {"m": {"input_price": 9.0, "output_price": 9.0}}},
    }}
    monkeypatch.setattr(pricing_resolver, "_pricing_cache", table)
    monkeypatch.setattr(pricing_resolver, "_alias_cache", {})
    bc.clear_price_cache()

    assert bc.price_for("genai", "m", "2026-02-01", 30).input_price == 1.0
    assert bc.price_for("genai", "m", "2026-02-02", 30) is None
    # a bucket after the run is never used, however close
    assert bc.price_for("genai", "m", "2026-02-28", 30) is None
    assert bc.price_for("genai", "m", "2026-02-02", None).input_price == 1.0
    bc.clear_price_cache()


def test_unreadable_request_leaves_the_summary_alone(tmp_path, prices):
    """A request that will not parse must not be dropped from the run's total."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(usage=dict(REASONING_USAGE)),
                    "b": request_payload(usage=dict(REASONING_USAGE))},
                   summary={"total_input_tokens": 200, "total_output_tokens": 400,
                            "total_tokens": 600, "input_cost_usd": 0.002,
                            "output_cost_usd": 0.004, "total_cost_usd": 0.006})
    with open(os.path.join(run, "request_b.json"), "wb") as fh:
        fh.write(b"{ this is not json")
    before = read(os.path.join(run, "scoring.json"))

    args = make_args(root, summaries=True, apply=True)
    bc.backfill(args, bc.Stats())
    _runs, changed, _unrep, _ret, skipped = bc.roll_up_summaries(args, True)

    assert read(os.path.join(run, "scoring.json")) == before
    assert changed == 0 and skipped == 1
    assert summary_of(run)["total_input_tokens"] == 200, "totalled from the readable half"


def test_unwritable_request_leaves_the_summary_alone(tmp_path, prices, monkeypatch):
    """If the writer skips a file, the run must not be totalled as if it had not."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(usage=dict(REASONING_USAGE))},
                   summary={"total_input_tokens": 100, "total_output_tokens": 200,
                            "total_tokens": 300, "input_cost_usd": 0.001,
                            "output_cost_usd": 0.002, "total_cost_usd": 0.003})
    before_req = read(os.path.join(run, "request_a.json"))
    before_sum = read(os.path.join(run, "scoring.json"))
    # the formatting safeguard rejects every file
    monkeypatch.setattr(bc, "detect_style", lambda raw, doc: None)

    args = make_args(root, summaries=True, apply=True)
    stats = bc.Stats()
    bc.backfill(args, stats)
    _runs, changed, _unrep, _ret, skipped = bc.roll_up_summaries(args, True)

    assert len(stats.unreproducible) == 1 and stats.written == 0
    assert read(os.path.join(run, "request_a.json")) == before_req
    assert read(os.path.join(run, "scoring.json")) == before_sum
    assert changed == 0 and skipped == 1


def test_a_stale_total_is_corrected_on_its_own(tmp_path, prices):
    """total_cost_usd is checked even when every other figure already matches."""
    prices[("openai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(provider="openai", usage={
                       "input_tokens": 100, "output_tokens": 200, "total_tokens": 300,
                       "input_cost_usd": 0.001, "output_cost_usd": 0.002,
                       "estimated_cost_usd": 0.003})},
                   summary={"total_input_tokens": 100, "total_output_tokens": 200,
                            "total_tokens": 300, "input_cost_usd": 0.001,
                            "output_cost_usd": 0.002, "total_cost_usd": 0.0})

    args = make_args(root, summaries=True, apply=True)
    bc.backfill(args, bc.Stats())
    _runs, changed, _unrep, _ret, _skip = bc.roll_up_summaries(args, True)

    assert changed == 1
    assert summary_of(run)["total_cost_usd"] == pytest.approx(0.003)


def test_request_without_a_usage_block_does_not_block_the_run(tmp_path, prices):
    """A request recording no usage contributes zero; it does not make the total unknown."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(usage=dict(REASONING_USAGE))},
                   summary={"total_input_tokens": 100, "total_output_tokens": 200,
                            "total_tokens": 300, "input_cost_usd": 0.001,
                            "output_cost_usd": 0.002, "total_cost_usd": 0.003})
    doc = request_payload()
    doc.pop("usage")
    write_json(os.path.join(run, "request_b.json"), doc)

    args = make_args(root, summaries=True, apply=True)
    bc.backfill(args, bc.Stats())
    _runs, changed, _unrep, _ret, skipped = bc.roll_up_summaries(args, True)

    assert skipped == 0, "a usage-less request blocked the run"
    assert changed == 1
    s = summary_of(run)
    assert s["total_reasoning_tokens"] == 1000
    assert s["total_input_tokens"] == 100, "the usage-less request added nothing"


def test_wholly_unpriced_run_keeps_its_recorded_total(tmp_path, prices):
    """No price in the window means the contribution is unknown, so the total stands."""
    root = tmp_path / "results"          # `prices` empty: nothing resolves
    run = make_run(root, "2026-01-02", "T0001",
                   {"a": request_payload(usage={"input_tokens": 100, "output_tokens": 200,
                                                "total_tokens": 300})},
                   summary={"total_input_tokens": 100, "total_output_tokens": 200,
                            "total_tokens": 300, "input_cost_usd": 0.001,
                            "output_cost_usd": 0.002, "total_cost_usd": 0.003})

    args = make_args(root, summaries=True, apply=True)
    bc.backfill(args, bc.Stats())
    bc.roll_up_summaries(args, True)

    assert summary_of(run)["total_cost_usd"] == pytest.approx(0.003), \
        "an unknown contribution was written as zero"


def test_one_unpriced_request_preserves_a_mixed_run_total(tmp_path, prices):
    """A priced request must not let an unpriceable sibling be counted as free."""
    prices[("genai", "m")] = price(10.0, 10.0)
    root = tmp_path / "results"
    run = make_run(root, "2026-01-02", "T0001", {
        "a": request_payload(usage=dict(REASONING_USAGE)),
        # different model, so `prices` has no entry for it
        "b": request_payload(model="unpriced", usage={"input_tokens": 100,
                                                      "output_tokens": 200,
                                                      "total_tokens": 300}),
    }, summary={"total_input_tokens": 200, "total_output_tokens": 400,
                "total_tokens": 600, "input_cost_usd": 0.002,
                "output_cost_usd": 0.004, "total_cost_usd": 0.006})

    args = make_args(root, summaries=True, apply=True)
    bc.backfill(args, bc.Stats())
    bc.roll_up_summaries(args, True)

    s = summary_of(run)
    assert s["total_cost_usd"] == pytest.approx(0.006), "partial sum overwrote the total"
    assert s["total_reasoning_tokens"] == 1000, "the known reasoning is still recorded"


# ------------------------------------------------- the components of a billed total

def billed(cost=0.00092005, prompt=0.0002725, completion=0.00064755, stored=None, **usage):
    """An OpenRouter request: a billed total, no components, the split in raw_response."""
    raw = {"usage": dict({"prompt_tokens": 2725, "completion_tokens": 4317,
                          "total_tokens": 7042, "cost": cost,
                          "cost_details": {"upstream_inference_cost": cost,
                                           "upstream_inference_prompt_cost": prompt,
                                           "upstream_inference_completions_cost": completion}},
                         **usage)}
    return request_payload(provider="openai", model="qwen/qwen3.5-9b", usage={
        "input_tokens": 2725, "output_tokens": 4317, "total_tokens": 7042,
        "estimated_cost_usd": cost if stored is None else stored}, raw_response=raw)


def test_a_billed_total_gets_the_providers_own_split(tmp_path, prices):
    run = make_run(tmp_path / "results", "2026-09-26", "T0983", {"a": billed()})
    path = os.path.join(run, "request_a.json")
    bc.main_with_args(make_args(tmp_path / "results", apply=True))
    usage = usage_of(path)
    assert usage["input_cost_usd"] == 0.0002725
    assert usage["output_cost_usd"] == 0.00064755
    assert usage["estimated_cost_usd"] == 0.00092005, "the billed total is never recomputed"


def test_the_split_needs_no_list_price(tmp_path, prices):
    """prices is empty: nothing in the pricing table is consulted for a billed total."""
    run = make_run(tmp_path / "results", "2026-09-26", "T0983", {"a": billed()})
    bc.main_with_args(make_args(tmp_path / "results", apply=True))
    assert usage_of(os.path.join(run, "request_a.json"))["input_cost_usd"] == 0.0002725


@pytest.mark.parametrize("case", [
    dict(prompt=0.0002725, completion=0.0005), # a per-request fee belongs to neither
    dict(stored=0.5),                          # the stored total is not what was billed
    dict(is_byok=True),                        # cost is OpenRouter's fee, not the bill
    dict(prompt=None),                         # no split to take
])
def test_a_split_that_does_not_account_for_the_bill_is_not_used(tmp_path, prices, case):
    run = make_run(tmp_path / "results", "2026-09-26", "T0983", {"a": billed(**case)})
    path = os.path.join(run, "request_a.json")
    before = read(path)
    bc.main_with_args(make_args(tmp_path / "results", apply=True))
    assert read(path) == before


def test_a_run_of_billed_totals_gets_component_totals(tmp_path, prices):
    summary = {"total_input_tokens": 5450, "total_output_tokens": 8634, "total_tokens": 14084,
               "input_cost_usd": 0.0, "output_cost_usd": 0.0, "total_cost_usd": 0.0018401}
    run = make_run(tmp_path / "results", "2026-09-26", "T0983",
                   {"a": billed(), "b": billed()}, summary=summary)
    bc.main_with_args(make_args(tmp_path / "results", apply=True, summaries=True))
    after = summary_of(run)
    assert after["input_cost_usd"] == pytest.approx(0.000545)
    assert after["output_cost_usd"] == pytest.approx(0.0012951)
    assert after["total_cost_usd"] == pytest.approx(0.0018401)


def test_one_unsplit_request_keeps_the_run_components_as_stored(tmp_path, prices):
    summary = {"total_input_tokens": 5450, "total_output_tokens": 8634, "total_tokens": 14084,
               "input_cost_usd": 0.0, "output_cost_usd": 0.0, "total_cost_usd": 0.0018401}
    run = make_run(tmp_path / "results", "2026-09-26", "T0983",
                   {"a": billed(), "b": billed(completion=0.0005)}, summary=summary)
    bc.main_with_args(make_args(tmp_path / "results", apply=True, summaries=True))
    after = summary_of(run)
    assert (after["input_cost_usd"], after["output_cost_usd"]) == (0.0, 0.0), (
        "a partial component sum would understate the run")
    assert after["total_cost_usd"] == pytest.approx(0.0018401)


def test_a_second_apply_leaves_split_files_alone(tmp_path, prices):
    run = make_run(tmp_path / "results", "2026-09-26", "T0983", {"a": billed()})
    path = os.path.join(run, "request_a.json")
    bc.main_with_args(make_args(tmp_path / "results", apply=True))
    once = read(path)
    bc.main_with_args(make_args(tmp_path / "results", apply=True))
    assert read(path) == once


def test_a_file_the_client_priced_unrounded_is_left_alone(tmp_path, prices):
    """ai_client 0.5.0 writes reasoning cost unrounded; the backfill rounds to 10 places."""
    prices[("genai", "m")] = price(0.5, 2.5)
    usage = {"input_tokens": 1000, "output_tokens": 1000, "total_tokens": 11378,
             "reasoning_tokens": 9378, "input_cost_usd": 0.0005, "output_cost_usd": 0.0025,
             "reasoning_cost_usd": 0.023444999999999997,
             "estimated_cost_usd": 0.0005 + 0.0025 + 0.023444999999999997}
    run = make_run(tmp_path / "results", "2026-09-26", "T0718",
                   {"a": request_payload(usage=usage)})
    path = os.path.join(run, "request_a.json")
    before = read(path)
    bc.main_with_args(make_args(tmp_path / "results", apply=True))
    assert read(path) == before
