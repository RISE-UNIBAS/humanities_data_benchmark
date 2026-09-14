"""An analysis-ready export of every stored benchmark result.

`dev/DATASET_EXPORT_PLAN.md` specifies the product: three typed tables that can be joined
on stable keys, a metric dictionary that says what each number means, and lossless payload
sidecars for anything the tables cannot represent. This package implements steps 1-3 of
its §9 -- freeze and inventory the inputs, declare the schema, and extract the tables.

The rule that shapes everything here is that nothing is dropped. A run whose test id is
absent from the CSV, a request file that will not parse, a run with no `scoring.json` and
a score of `"niy"` are all rows, each with a status column saying which. The frontend
export in `scripts/ndr_export` is entitled to skip what it cannot chart; an archive is
not, because a silence in a dataset cannot be told apart from an absence of data.

Reading is done through `scripts/results_index.py` and never through `benchmark_base`,
whose `load_saved_answer` recalculates missing costs at today's prices. What a run
recorded and what it would cost today are different facts and the export keeps them in
different columns.

Build it with `python -m scripts.export_dataset`. Output goes to a staging directory and
is moved into place only on success, so a failed build never replaces a good one.
"""
from scripts.results_index import PROJECT_ROOT

DATASET_PATH = PROJECT_ROOT / "dataset"
"""Release artifact, not source. Git-ignored: it is derived from `results/` and rebuilt."""

STAGING_SUFFIX = ".staging"

SCHEMA_VERSION = "1.1.0"
"""Semver over the table and column contract. A new column is a minor bump; a changed
meaning for an existing one is a major bump, because it silently breaks an analysis that
already ran."""


def default_dataset_version(data_cutoff, serial=1):
    """`<data_cutoff>.<serial>` -- the identifier an analysis cites.

    Three versions travel with a release and they answer different questions.
    `SCHEMA_VERSION` says whether your code still reads it. `data_cutoff` says how much
    data it covers. `dataset_version` says *which build* -- and it is the one that must
    change when a correction is made to records the previous release already contained,
    even though neither the schema nor the cutoff moved. Without it two releases of
    corrected 2026-09-09 data would be indistinguishable in a citation.

    The serial is passed, not inferred: the builder cannot know whether this is a
    correction of the last release or the first build of new data, and guessing wrong
    produces a duplicate identifier for different bytes.
    """
    return "%s.%d" % (data_cutoff or "unknown", serial)
