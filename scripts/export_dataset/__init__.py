"""Export stored benchmark results as typed tables and supporting metadata.

The full export retains each stored run directory and request file, including
unresolved configurations, unreadable requests, and unscored runs. Status columns
record these conditions. Numeric scores, recorded costs, derived cost estimates,
and supplementary re-scoring results remain distinguishable.

Source records are read through scripts.results_index. Derived costs use recorded
token counts and the latest matching pricing entry on or before the run date.
Input hashes, schemas, coverage statistics, diagnostics, and documentation
accompany the tables and JSON payload sidecars.

Run ``python -m scripts.export_dataset`` to build the dataset in a staging
directory and publish it after table validation.
"""
from scripts.results_index import PROJECT_ROOT

DATASET_PATH = PROJECT_ROOT / "dataset"
"""Default output directory for the generated, Git-ignored dataset."""

STAGING_SUFFIX = ".staging"

SCHEMA_VERSION = "1.1.0"
"""Semantic version of the table and column contract.

Additive columns require a minor version increment; incompatible changes to
existing column meanings require a major version increment.
"""


def default_dataset_version(data_cutoff, serial=1):
    """Return the dataset release identifier as ``<data_cutoff>.<serial>``.

    Use ``unknown`` when no cutoff is available. The caller supplies the serial to
    distinguish releases with the same cutoff, including corrections that do not
    change the schema version or the date range.
    """
    return "%s.%d" % (data_cutoff or "unknown", serial)
