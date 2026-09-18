"""Date-aware pricing lookup, for the NDR export and cost analyses over stored results.

This lives in the export, not in the benchmark core, because what it produces is
*derived* information -- the price in force on a given date -- recomputable at any time
from `scripts/data/pricing.json` plus a run's date. Nothing here is written back into
`results/*/*/scoring.json`; that file stays a record of what a run observed, and the
provenance is attached to the exported record instead.

`ai_client.PricingManager.get_model_pricing()` cannot answer this question: it takes no
date, sorting every bucket descending and returning the newest one that lists the model.
That coincides with the run's own bucket while a run is executing, but re-reading an old
run today would price it at today's rate.

So this implements the rule the table is actually maintained for: a run is priced with
the bucket at its own date, or the next most recent, up to `MAX_AGE_DAYS` back.
`update_pricing.py::get_models_needing_pricing` keeps that window open going forward --
when it builds the table for a date it skips any model already priced within the
preceding 30 days.

The window is not a guarantee across the historical corpus, though: the table was not
maintained continuously in the past, so some runs need an older bucket than 30 days
(mistral is priced 2026-03-02 and then not again until 2026-07-22). Callers that widen
the window must surface `age_days` rather than present a stale price as current.

Usage:
    from ndr_export.pricing_resolver import resolve_pricing

    pricing = resolve_pricing("openai", "gpt-4o-mini", "2026-03-16")
    if pricing:
        print(pricing.input_price, pricing.output_price, pricing.bucket_date)
"""
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, NamedTuple, Optional

logger = logging.getLogger(__name__)

SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
PRICING_FILE = SCRIPTS_DIR / "data" / "pricing.json"
ALIAS_FILE = SCRIPTS_DIR / "data" / "model_aliases.json"

MAX_AGE_DAYS = 30
"""How far back a run may reach for a price. Mirrors the window
`update_pricing.py::get_models_needing_pricing` uses when deciding what to scrape."""

DATE_FORMAT = "%Y-%m-%d"


class ResolvedPricing(NamedTuple):
    """A price as it stood for a given run."""

    input_price: float
    output_price: float
    bucket_date: str
    """The pricing.json bucket the prices came from -- NOT the run date."""

    age_days: int
    """How stale the bucket was at the time of the run."""


_pricing_cache: Optional[Dict] = None
_alias_cache: Optional[Dict] = None


def _load_pricing() -> Dict:
    global _pricing_cache
    if _pricing_cache is None:
        try:
            with open(PRICING_FILE, "r", encoding="utf-8") as handle:
                _pricing_cache = json.load(handle)
        except (OSError, json.JSONDecodeError) as error:
            logger.error("Could not load pricing table %s: %s", PRICING_FILE, error)
            _pricing_cache = {"pricing": {}}
    return _pricing_cache


def _load_aliases() -> Dict:
    """Maps a result-file model name back to its pricing.json key.

    Mirrors the reverse map built in inject_costs.py, kept here so the resolver has no
    import dependency on that script.
    """
    global _alias_cache
    if _alias_cache is None:
        _alias_cache = {}
        if ALIAS_FILE.exists():
            try:
                with open(ALIAS_FILE, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                for provider, mapping in data.get("aliases", {}).items():
                    for csv_name, result_name in mapping.items():
                        _alias_cache[(provider, result_name)] = csv_name
            except (OSError, json.JSONDecodeError) as error:
                logger.warning("Could not load model aliases %s: %s", ALIAS_FILE, error)
    return _alias_cache


def pricing_table_version() -> str:
    """Version string of the loaded table, for start-up logging."""
    return _load_pricing().get("metadata", {}).get("version", "unknown")


def _candidate_model_names(provider: str, model: str):
    """The names to try in the table, most specific first.

    Covers the alias map and the dated-suffix stripping ai_client does, so a result file
    naming a model `gpt-5.1-2025-11-13` still finds a `gpt-5.1` entry.
    """
    seen = []
    for name in (model, _load_aliases().get((provider, model))):
        if name and name not in seen:
            seen.append(name)

    for name in list(seen):
        base = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", name)
        base = re.sub(r"-\d{8}$", "", base)
        if base != name and base not in seen:
            seen.append(base)
    return seen


def _entry_is_priced(entry) -> bool:
    """A bucket entry counts only when both prices are actually set.

    A null price is a real state in this table (contour_local is unpriced by design), and
    it must not be read as zero.
    """
    if not isinstance(entry, dict):
        return False
    return entry.get("input_price") is not None and entry.get("output_price") is not None


def resolve_pricing(provider: str, model: str, run_date: str,
                    max_age_days: Optional[int] = MAX_AGE_DAYS) -> Optional[ResolvedPricing]:
    """Returns the price a run should be costed at, or None if nothing is in range.

    The default window is the documented rule and is what a live run should use. Pass
    `max_age_days=None` to take the nearest earlier bucket at any age: the table was not
    maintained continuously in the past (mistral, for one, is priced at 2026-03-02 and
    then not again until 2026-07-22), so a strict window leaves historical runs with no
    provenance at all. Callers that widen the window must surface `age_days` rather than
    present a stale price as though it were in force.

    :param provider: provider id as written in the result file, e.g. 'openai'
    :param model: model id as written in the result file
    :param run_date: the run's date folder, 'YYYY-MM-DD'
    :param max_age_days: how far back to look; 0 is the run's own bucket only, None is
        unbounded
    """
    try:
        run_dt = datetime.strptime(run_date, DATE_FORMAT)
    except (TypeError, ValueError):
        logger.warning("Un-parseable run date %r for %s/%s", run_date, provider, model)
        return None

    buckets = _load_pricing().get("pricing", {})
    names = _candidate_model_names(provider, model)

    best: Optional[ResolvedPricing] = None
    for bucket_date, providers in buckets.items():
        try:
            age = (run_dt - datetime.strptime(bucket_date, DATE_FORMAT)).days
        except ValueError:
            continue
        # Only buckets at or before the run, and not older than the window.
        if age < 0 or (max_age_days is not None and age > max_age_days):
            continue
        # A nearer bucket always wins, so stop early once one cannot improve.
        if best is not None and age >= best.age_days:
            continue

        entries = providers.get(provider, {})
        for name in names:
            entry = entries.get(name)
            if _entry_is_priced(entry):
                best = ResolvedPricing(
                    input_price=entry["input_price"],
                    output_price=entry["output_price"],
                    bucket_date=bucket_date,
                    age_days=age,
                )
                break

    if best is None:
        logger.warning("No price within %s days of %s for %s/%s",
                       "any" if max_age_days is None else max_age_days,
                       run_date, provider, model)
    return best
