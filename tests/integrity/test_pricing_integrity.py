"""Integrity guards over scripts/data/pricing.json.

Enforces the project's pricing rules against the real data, so an incomplete
model addition fails. Run logic-only with: pytest -m "not integrity".

Pricing rules enforced here:
  1. metadata block carries a `version` and a `last_updated` date.
  2. Every non-legacy model in benchmarks_tests.csv has an explicit pricing.json
     entry under its exact (provider, model) key — no base-model/date-suffix
     fallback, so the full "Adding a New Model" workflow is required per model.
  3. For API providers, that entry must carry a usable numeric, non-negative
     `input_price` and `output_price`. Local providers (is_local_provider) run on
     local hardware with no per-token price, so null prices are accepted — but an
     entry is still required.
  4. Every pricing entry has all required fields: input_price, output_price,
     source_url, added.
  5. Every `source_url` is a Wayback Machine archive (http or https), except for
     providers in WAYBACK_EXEMPT_PROVIDERS and local providers, which have no
     public, archivable pricing page.
"""
import csv
import json
import os
import re

import pytest

from local import is_local_provider

pytestmark = pytest.mark.integrity

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(REPO_ROOT, "benchmarks", "benchmarks_tests.csv")
PRICING_PATH = os.path.join(REPO_ROOT, "scripts", "data", "pricing.json")

WAYBACK_RE = re.compile(r"^https?://web\.archive\.org/web/")
REQUIRED_ENTRY_FIELDS = {"input_price", "output_price", "source_url", "added"}

# Providers with no public, archivable pricing page (self-hosted / local backends)
# are exempt from the Wayback-archive requirement.
WAYBACK_EXEMPT_PROVIDERS = {"scicore"}


def _wayback_exempt(provider: str) -> bool:
    return provider in WAYBACK_EXEMPT_PROVIDERS or is_local_provider(provider)


@pytest.fixture(scope="module")
def pricing():
    with open(PRICING_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def priced_entries(pricing):
    """Map (provider, model) -> list of its pricing entries across all date buckets."""
    entries = {}
    for providers in pricing["pricing"].values():
        for provider, models in providers.items():
            for model, entry in models.items():
                entries.setdefault((provider, model), []).append(entry)
    return entries


def _is_valid_price(value) -> bool:
    """A usable price: a non-negative real number (bool excluded)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


@pytest.fixture(scope="module")
def non_legacy_csv_models():
    pairs = set()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["legacy_test"].strip().lower() != "true":
                pairs.add((r["provider"], r["model"]))
    return pairs


def test_metadata_present(pricing):
    meta = pricing.get("metadata", {})
    assert meta.get("version"), "metadata.version missing"
    assert meta.get("last_updated"), "metadata.last_updated missing"


def test_every_non_legacy_model_priced(non_legacy_csv_models, priced_entries):
    """Every non-legacy model in benchmarks_tests.csv must have an explicit
    pricing.json entry (exact provider+model key) with a usable numeric price."""
    missing = []        # no entry at all
    unpriced = []       # entry exists but no usable input/output price (non-local only)
    for pair in sorted(non_legacy_csv_models):
        provider, _model = pair
        entries = priced_entries.get(pair)
        if not entries:
            missing.append(pair)
            continue
        # Local models run on local hardware and have no per-token price (null is valid);
        # only API providers must carry a usable numeric price.
        if is_local_provider(provider):
            continue
        if not any(
            _is_valid_price(e.get("input_price")) and _is_valid_price(e.get("output_price"))
            for e in entries
        ):
            unpriced.append(pair)
    assert not missing, f"Non-legacy models with no pricing entry: {missing}"
    assert not unpriced, f"Non-legacy models with an entry but no usable numeric price: {unpriced}"


def test_entry_fields_present(pricing):
    incomplete = []
    for date, providers in pricing["pricing"].items():
        for provider, models in providers.items():
            for model, entry in models.items():
                missing = REQUIRED_ENTRY_FIELDS - entry.keys()
                if missing:
                    incomplete.append((date, provider, model, sorted(missing)))
    assert not incomplete, f"Pricing entries missing required fields: {incomplete}"


def test_source_urls_are_wayback(pricing):
    bad = []
    for date, providers in pricing["pricing"].items():
        for provider, models in providers.items():
            if _wayback_exempt(provider):
                continue
            for model, entry in models.items():
                url = entry.get("source_url", "")
                if not WAYBACK_RE.match(url):
                    bad.append((date, provider, model, url))
    assert not bad, (
        f"{len(bad)} source_url(s) are not Wayback archives: "
        f"{bad[:20]}{' ...' if len(bad) > 20 else ''}"
    )
