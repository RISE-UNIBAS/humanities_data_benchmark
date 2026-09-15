"""Column types and status vocabularies for the three tables.

The pyarrow schema is the single source of truth. CSV is generated from the same typed
rows rather than written independently, so the two cannot drift; `writers.py` asserts they
read back equal.

Every column is nullable and integer columns stay `int64`. That matters more than it
looks: a token count that is absent must not arrive as `0`, and a float column holding
integers silently rounds large ones. Null means "not recorded", always, and is never an
inferred zero.

The status vocabularies exist because the alternative is a boolean that cannot say why.
`has_scoring` is true for a `scoring.json` that exists and is a `{"score": "niy"}`
placeholder; only `scoring_status` separates that from a run that was really scored.
"""
import pyarrow as pa

# --- status vocabularies ----------------------------------------------------------

CONFIG_STATUSES = ("matched", "unknown_test_id")
"""Whether the run directory's test id resolves in `benchmarks_tests.csv`. An unknown id
keeps its exact spelling and its benchmark-derived columns stay null; it is never mapped
onto a base test, because a variant id is evidence about what was run."""

PARSE_STATUSES = ("ok", "missing", "unreadable", "invalid")
"""Reading the stored JSON -- not whether the model's own output parsed. A response that
the model returned as prose sits in a perfectly valid request file."""

SCORING_STATUSES = ("missing", "invalid", "not_implemented", "no_numeric_metrics",
                    "numeric_metrics_present")
"""`not_implemented` is the literal `{"score": "niy"}` a scorer writes when it has none.
`no_numeric_metrics` is a scoring file that parsed and carried nothing this export can
express as a number -- a message, say. Neither certifies that every expected document in
the run was scored: that is coverage, and it is not knowable from the file."""

COST_PROVENANCES = ("derived", "partial_tokens", "no_price_in_table", "no_tokens",
                    "no_model_identity")
"""How `derived_total_cost_usd` came about, or why it did not. `partial_tokens` is one
count recorded and the other not: the known component is exported, the total is null, and
the missing side is never assumed to be zero."""

PRICING_IDENTITY_SOURCES = ("response", "config")
"""Whether the provider/model priced came from the stored response or from the test
configuration. They disagree for aliased and routed models, and the difference is the
reason both are exported."""

LEVELS = ("run", "request", "field")

METRIC_ROLES = ("performance", "count", "parameter")
"""A count is not a score and a parameter is not a measurement. `iou_threshold` is a knob
the scorer was given; `mean_iou` is what it measured. Averaging the two together is the
mistake this column exists to prevent."""


# --- tables -----------------------------------------------------------------------

RUNS = pa.schema([
    ("run_id", pa.string()),
    ("test_id", pa.string()),
    ("date", pa.string()),
    ("benchmark", pa.string()),
    ("source_path", pa.string()),

    ("config_status", pa.string()),
    ("configured_provider", pa.string()),
    ("configured_model", pa.string()),
    ("dataclass", pa.string()),
    ("temperature", pa.float64()),
    ("role_description", pa.string()),
    ("prompt_file", pa.string()),
    ("rules_json", pa.string()),
    ("legacy_test", pa.bool_()),
    ("benchmark_display", pa.bool_()),
    ("hidden", pa.bool_()),

    ("n_requests", pa.int64()),
    ("n_valid_requests", pa.int64()),
    ("n_explicit_errors", pa.int64()),
    ("n_scored", pa.int64()),
    ("has_scoring", pa.bool_()),
    ("scoring_status", pa.string()),

    # Copied from scoring.json's cost_summary without recomputation.
    ("recorded_total_input_tokens", pa.int64()),
    ("recorded_total_output_tokens", pa.int64()),
    ("recorded_total_tokens", pa.int64()),
    ("recorded_input_cost_usd", pa.float64()),
    ("recorded_output_cost_usd", pa.float64()),
    ("recorded_total_cost_usd", pa.float64()),
    # Only the longer cost_summary shape carries these.
    ("recorded_pricing_date", pa.string()),
    ("recorded_input_price_per_million", pa.float64()),
    ("recorded_output_price_per_million", pa.float64()),

    # Summed over this run's request rows. An observed subtotal, never an estimate of
    # what the missing requests would have cost.
    ("n_requests_with_stored_cost", pa.int64()),
    ("observed_stored_cost_usd", pa.float64()),
    ("stored_cost_coverage_fraction", pa.float64()),
    ("stored_cost_complete_for_saved_requests", pa.bool_()),
    ("n_requests_with_derived_cost", pa.int64()),
    ("observed_derived_cost_usd", pa.float64()),
    ("derived_cost_coverage_fraction", pa.float64()),

    ("tags_json", pa.string()),
    ("contributors_json", pa.string()),
])

REQUESTS = pa.schema([
    ("run_id", pa.string()),
    ("object_id", pa.string()),
    ("test_id", pa.string()),
    ("date", pa.string()),
    ("benchmark", pa.string()),
    ("source_path", pa.string()),
    ("line", pa.int64()),

    ("configured_provider", pa.string()),
    ("configured_model", pa.string()),
    ("response_provider", pa.string()),
    ("response_model", pa.string()),

    ("parse_status", pa.string()),
    ("timestamp_raw", pa.string()),
    ("timestamp_utc", pa.string()),
    ("duration_s", pa.float64()),
    ("finish_reason", pa.string()),
    ("is_error", pa.bool_()),
    ("error_message", pa.string()),
    ("scoring_status", pa.string()),
    ("is_scored", pa.bool_()),

    ("input_tokens", pa.int64()),
    ("output_tokens", pa.int64()),
    ("total_tokens", pa.int64()),
    ("cached_tokens", pa.int64()),
    ("cache_creation_tokens", pa.int64()),
    ("cache_read_tokens", pa.int64()),

    # What the run recorded, verbatim. Never recomputed, never backfilled.
    ("stored_input_cost_usd", pa.float64()),
    ("stored_output_cost_usd", pa.float64()),
    ("stored_estimated_cost_usd", pa.float64()),

    # Recomputed here from the recorded tokens and the price in force on the run's date.
    # A different claim from the stored figure, so a different set of columns.
    ("derived_input_cost_usd", pa.float64()),
    ("derived_output_cost_usd", pa.float64()),
    ("derived_total_cost_usd", pa.float64()),
    ("cost_provenance", pa.string()),
    ("pricing_bucket_date", pa.string()),
    ("pricing_age_days", pa.int64()),
    ("pricing_input_price_per_million", pa.float64()),
    ("pricing_output_price_per_million", pa.float64()),
    ("pricing_model_key", pa.string()),
    ("pricing_identity_source", pa.string()),

    ("conversation_id", pa.string()),
    ("has_parsed", pa.bool_()),
    ("has_raw_response", pa.bool_()),
])

SCORES_LONG = pa.schema([
    ("run_id", pa.string()),
    ("object_id", pa.string()),
    ("level", pa.string()),
    ("field_path", pa.string()),
    ("metric_id", pa.string()),
    ("value", pa.float64()),
])

RESCORED_FIELDS = pa.schema([
    ("run_id", pa.string()),
    ("object_id", pa.string()),
    ("benchmark", pa.string()),
    ("field_path", pa.string()),
    ("score", pa.float64()),
    ("reproduces_stored_score", pa.bool_()),
    ("rescored_date", pa.string()),
    ("scorer_revision", pa.string()),
    ("ground_truth_revision", pa.string()),
    ("scorer_dirty", pa.bool_()),
])
"""Deliberately not part of `scores_long`. These are today's readings of stored responses,
not what the runs recorded, and they carry provenance the stored scores cannot have."""

METRICS = pa.schema([
    ("metric_id", pa.string()),
    ("benchmark", pa.string()),
    ("level", pa.string()),
    ("source_metric", pa.string()),
    ("metric_role", pa.string()),
    ("unit", pa.string()),
    ("direction", pa.string()),
    ("min_value", pa.float64()),
    ("max_value", pa.float64()),
    ("aggregation", pa.string()),
    ("description", pa.string()),
])

TABLES = {
    "runs": RUNS,
    "requests": REQUESTS,
    "scores_long": SCORES_LONG,
    "rescored_fields": RESCORED_FIELDS,
    "metrics": METRICS,
}

SCHEMAS_FOR_DOCS = dict(TABLES)
"""The tables `columns.py` must describe. `coverage` is described there too but has no
pyarrow schema, since it is generated rather than extracted."""

SORT_KEYS = {
    "runs": ("run_id",),
    "requests": ("run_id", "object_id"),
    "scores_long": ("run_id", "object_id", "level", "field_path", "metric_id"),
    "rescored_fields": ("run_id", "object_id", "field_path"),
    "metrics": ("metric_id",),
}

UNIQUE_KEYS = {
    "runs": ("run_id",),
    "requests": ("run_id", "object_id"),
    "scores_long": ("run_id", "object_id", "level", "field_path", "metric_id"),
    "rescored_fields": ("run_id", "object_id", "field_path"),
    "metrics": ("metric_id",),
}


def empty_string_is_null(table, column):
    """Whether an empty source string should be normalised to null in this column.

    Everywhere except `scores_long.field_path`, where `""` is a real key: four benchmarks
    store a `field_scores` entry under the empty string -- 6,080 request records do -- and
    collapsing it to null would merge it with the run- and request-level rows that
    legitimately have no field path, breaking the table's uniqueness key.
    """
    return column != "field_path" or table not in ("scores_long", "rescored_fields")
