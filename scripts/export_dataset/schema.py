"""Declare dataset table schemas, keys, and status vocabularies.

PyArrow schemas define column types for the exported tables. Writers generate
Parquet and CSV from the same typed records and validate CSV round trips.
Columns are nullable, with counts represented as int64 and missing quantities
kept distinct from zero.

Status values distinguish file presence, parsing, configuration resolution,
scoring, and cost derivation. For example, has_scoring records file presence,
while scoring_status distinguishes numeric metrics from placeholders.
"""
import pyarrow as pa

# --- status vocabularies ----------------------------------------------------------

CONFIG_STATUSES = ("matched", "unknown_test_id")
"""Resolution of a run's test identifier against benchmarks_tests.csv.

Unresolved identifiers are preserved without substituting a different test.
"""

PARSE_STATUSES = ("ok", "missing", "unreadable", "invalid")
"""Read and parse status of the stored JSON file, independent of model-output validity."""

SCORING_STATUSES = ("missing", "invalid", "not_implemented", "no_numeric_metrics",
                    "numeric_metrics_present")
"""Availability and content of a stored scoring record.

The ``niy`` marker denotes unimplemented scoring; no_numeric_metrics denotes a
parsed record without numeric metrics. These statuses do not measure coverage
of the expected benchmark inputs.
"""

COST_PROVENANCES = ("derived", "partial_tokens", "no_price_in_table", "no_tokens",
                    "no_model_identity")
"""Outcome of deriving request costs from recorded tokens and pricing.

With partial_tokens, retain the available cost component and leave the total null.
"""

PRICING_IDENTITY_SOURCES = ("response", "config")
"""Source of the provider/model identity used for pricing: response or configuration."""

LEVELS = ("run", "request", "field")

METRIC_ROLES = ("performance", "count", "parameter")
"""Distinguish performance measurements, counts, and scorer parameters.

For example, mean_iou is a measurement and iou_threshold is a parameter.
"""


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
"""Supplementary field evaluations with provenance from the subsequent scoring pass."""

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
"""Table schemas validated against the column dictionary.

Coverage has separate column definitions and is written directly as CSV.
"""

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
    """Return whether empty strings should become null for a table column.

    Preserve empty field identifiers in scores_long and rescored_fields. Empty
    strings in all other table columns are normalized to null.
    """
    return column != "field_path" or table not in ("scores_long", "rescored_fields")
