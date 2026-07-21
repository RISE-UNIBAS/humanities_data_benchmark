"""Integrity guards that a newly added model is registered everywhere the
"Adding a New Model" workflow requires: the pricing scraper and the README.

Run logic-only with: pytest -m "not integrity".

Rules enforced here:
  1. Every non-legacy model resolves to a non-empty source URL in
     scripts/update_pricing.py (PricingUpdater.get_source_url). For most providers
     this means an explicit *_MODEL_URLS entry; anthropic/genai/openrouter have a
     provider-level fallback, so those resolve without a per-model entry. scicore
     and local providers have no scraper and are exempt.
  2. Every non-legacy model name appears in the README.md models table. Local
     providers are exempt — the README table documents API models only.
"""
import csv
import os

import pytest

from local import is_local_provider
from update_pricing import PricingUpdater

pytestmark = pytest.mark.integrity

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(REPO_ROOT, "benchmarks", "benchmarks_tests.csv")
README_PATH = os.path.join(REPO_ROOT, "README.md")

# Providers without a pricing scraper in update_pricing.py (no public page to scrape).
SCRAPER_EXEMPT_PROVIDERS = {"scicore"}


@pytest.fixture(scope="module")
def non_legacy_models():
    pairs = set()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["legacy_test"].strip().lower() != "true":
                pairs.add((r["provider"], r["model"]))
    return sorted(pairs)


def test_models_registered_in_update_pricing(non_legacy_models):
    # get_source_url only reads class-level *_MODEL_URLS dicts, so bypass __init__.
    updater = PricingUpdater.__new__(PricingUpdater)
    missing = [
        (provider, model)
        for provider, model in non_legacy_models
        if provider not in SCRAPER_EXEMPT_PROVIDERS and not is_local_provider(provider)
        and not PricingUpdater.get_source_url(updater, provider, model)
    ]
    assert not missing, f"Non-legacy models not registered in update_pricing.py: {missing}"


def test_models_listed_in_readme(non_legacy_models):
    readme = open(README_PATH, encoding="utf-8").read()
    missing = [
        (provider, model)
        for provider, model in non_legacy_models
        if not is_local_provider(provider) and model not in readme
    ]
    assert not missing, f"Non-legacy models missing from the README models table: {missing}"