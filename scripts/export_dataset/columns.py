"""What every exported column means.

This is the data dictionary. `datapackage.json` and the README are both generated from it,
so a column cannot acquire a description in one and lack it in the other, and a column
added to `schema.py` without a description here fails the build.

The descriptions are written for someone holding the files and nothing else -- no
repository, no access to the people who ran the benchmarks. That rules out shorthand like
"see the scorer": if a column's meaning depends on a fact about how the corpus was
produced, the fact belongs here.
"""

RUNS = {
    "run_id": "Primary key: `<test_id>@<date>`. Identifies a stored run directory within "
              "this release. A test executed on another date is a different run.",
    "test_id": "The test configuration's id, as the run directory is named. Preserved "
               "exactly, including variant spellings that no longer appear in the "
               "configuration file.",
    "date": "The date folder the run was stored under, `YYYY-MM-DD`. Not a timestamp: it "
            "is the directory name, and the runner writes to it for the duration of a run.",
    "benchmark": "Which benchmark this run belongs to, from the test configuration. Null "
                 "when the test id could not be resolved.",
    "source_path": "Path of the run directory in the source archive, for tracing a row "
                   "back to the bytes it came from.",
    "config_status": "`matched` when the test id resolves in the configuration file, "
                     "`unknown_test_id` when it does not. An unknown id keeps its exact "
                     "spelling and its configuration-derived columns stay null.",
    "configured_provider": "Provider named in the test configuration. May differ from the "
                           "provider that actually served the requests -- see "
                           "`requests.response_provider`.",
    "configured_model": "Model named in the test configuration. May differ from the model "
                        "that actually served the requests.",
    "dataclass": "Structured-output class the run requested, if any.",
    "temperature": "Sampling temperature configured for the run. Null when not configured, "
                   "which is not the same as zero.",
    "role_description": "System-role text configured for the run.",
    "prompt_file": "Name of the prompt file used. The prompt's contents are not exported; "
                   "prompts changed over the corpus and this records only which was named.",
    "rules_json": "The run's `rules` column verbatim, as a JSON string. Some benchmarks "
                  "select which fields they score from it, so two runs of one benchmark "
                  "with different rules are not directly comparable.",
    "legacy_test": "True when the configuration marks this test as deprecated.",
    "benchmark_display": "The benchmark's `display` metadata flag. True when the metadata "
                         "loaded and did not set it to false; null when metadata could not "
                         "be read.",
    "hidden": "The default analytical view excludes these. True when the test is legacy or "
              "the benchmark sets `display: false`; false only when both inputs are known "
              "and neither hides the run; null when either is unresolved. Filter on "
              "`hidden = false` rather than `hidden != true`: null is not a licence to "
              "include.",
    "n_requests": "Request files discovered in the run directory. The denominator for the "
                  "coverage fractions below.",
    "n_valid_requests": "Request files that parsed as JSON. Lower than `n_requests` when a "
                        "stored file is malformed.",
    "n_explicit_errors": "Requests whose stored record carries a truthy `error` or "
                         "`error_message`. Not a general failure count: a request can fail "
                         "without recording either.",
    "n_scored": "Requests where `requests.is_scored` is true -- a performance metric, or "
                "the complete counts a counting scorer uses. Not the scorer's own `n`, "
                "and it does not certify that every expected document was scored: it "
                "counts observations that exist, not observations that should.",
    "has_scoring": "Whether a `scoring.json` file exists. True even when that file only "
                   "records that scoring is not implemented.",
    "scoring_status": "One of `missing`, `invalid`, `not_implemented` (the scorer wrote "
                      "`niy`), `no_numeric_metrics`, `numeric_metrics_present`.",
    "recorded_total_input_tokens": "Copied verbatim from the run's own cost summary.",
    "recorded_total_output_tokens": "Copied verbatim from the run's own cost summary.",
    "recorded_total_tokens": "Copied verbatim from the run's own cost summary.",
    "recorded_input_cost_usd": "Copied verbatim from the run's own cost summary. Not "
                               "recomputed, and its completeness is unknown.",
    "recorded_output_cost_usd": "Copied verbatim from the run's own cost summary.",
    "recorded_total_cost_usd": "Copied verbatim from the run's own cost summary. The "
                               "runner initialises this to zero and skips requests with no "
                               "cost, so it may already be an understatement.",
    "recorded_pricing_date": "Pricing bucket the run costed itself against, where its cost "
                             "summary records one. Only the longer summary shape carries it.",
    "recorded_input_price_per_million": "Input price the run costed itself against, where "
                                        "recorded.",
    "recorded_output_price_per_million": "Output price the run costed itself against, "
                                         "where recorded.",
    "n_requests_with_stored_cost": "Requests in this run carrying a finite stored total "
                                   "cost, zero included.",
    "observed_stored_cost_usd": "Sum of those stored costs. An observed subtotal, not an "
                                "estimate of what the requests without one would have cost.",
    "stored_cost_coverage_fraction": "`n_requests_with_stored_cost / n_requests`. Null for "
                                     "a run with no requests.",
    "stored_cost_complete_for_saved_requests": "True only when every saved request in this "
                                               "run has a stored cost. Says nothing about "
                                               "attempts that were never saved.",
    "n_requests_with_derived_cost": "Requests in this run for which a cost could be derived "
                                    "from recorded tokens and the price table.",
    "observed_derived_cost_usd": "Sum of those derived costs.",
    "derived_cost_coverage_fraction": "`n_requests_with_derived_cost / n_requests`.",
    "tags_json": "The benchmark's tags, as a JSON string. Describes the benchmark at export "
                 "time, not necessarily at run time.",
    "contributors_json": "The benchmark's contributors, as a JSON string.",
}

REQUESTS = {
    "run_id": "Foreign key to `runs.run_id`.",
    "object_id": "The input's identity within its benchmark, taken from the request "
                 "filename. A string: leading zeros and non-ASCII characters are "
                 "significant. Null when the filename resolved to no id, which is a "
                 "release-blocking diagnostic rather than a normal state.",
    "test_id": "Denormalised from `runs`, for filtering without a join.",
    "date": "Denormalised from `runs`.",
    "benchmark": "Denormalised from `runs`.",
    "source_path": "Path of the request file in the source archive.",
    "line": "Integer line number, populated only when the whole object id matches "
            "`line_<digits>`. Presentation metadata; never a join key.",
    "configured_provider": "Provider from the test configuration.",
    "configured_model": "Model from the test configuration.",
    "response_provider": "Provider as the stored response reports it. This and the "
                         "configured provider are both exported because they disagree for "
                         "aliased and routed models; neither is substituted for the other.",
    "response_model": "Model as the stored response reports it. For routed providers this "
                      "is what actually served the request.",
    "parse_status": "Whether the stored file could be read: `ok`, `missing`, `unreadable`, "
                    "`invalid`. Describes reading the file, not whether the model's own "
                    "output parsed.",
    "timestamp_raw": "The timestamp exactly as stored. Naive local time throughout this "
                     "corpus, with no offset recorded.",
    "timestamp_utc": "UTC conversion, populated only where the source carries an offset. "
                     "Null for every row in this release, because no stored timestamp does "
                     "and the writing machine's timezone is not recorded.",
    "duration_s": "Wall-clock seconds the request took, as recorded. Absent on some error "
                  "records.",
    "finish_reason": "Completion reason reported by the provider.",
    "is_error": "True when the record carries an explicit error field. Null when it cannot "
                "be assessed, for instance when the file did not parse. Not a general "
                "success verdict.",
    "error_message": "The recorded error text, where present.",
    "scoring_status": "Same vocabulary as `runs.scoring_status`, applied to this request's "
                      "own stored score.",
    "is_scored": "Whether this request carries a real scoring observation, by its "
                 "benchmark's own rule: a performance metric, or the complete set of "
                 "counts a counting scorer uses. `business_letters` needs all three "
                 "true-positive categories, since one is a partial observation. A "
                 "parameter such as `iou_threshold` does not qualify, nor do the fixed "
                 "placeholders the scaffold benchmarks emit. This is the column "
                 "`runs.n_scored` counts.",
    "input_tokens": "Prompt tokens as recorded. Null when no usage block was stored, which "
                    "is not the same as zero.",
    "output_tokens": "Completion tokens as recorded.",
    "total_tokens": "Total tokens as recorded. Not necessarily the sum of the two above.",
    "cached_tokens": "Cached prompt tokens, where the provider reported them.",
    "cache_creation_tokens": "Cache-write tokens, where reported.",
    "cache_read_tokens": "Cache-read tokens, where reported.",
    "stored_input_cost_usd": "Input cost exactly as the run recorded it. Never recomputed.",
    "stored_output_cost_usd": "Output cost exactly as the run recorded it.",
    "stored_estimated_cost_usd": "Total cost exactly as the run recorded it. Costed against "
                                 "whatever price table was live at run time, which varies "
                                 "across the corpus.",
    "derived_input_cost_usd": "Recomputed here: `input_tokens / 1e6 × the input price in "
                              "force on the run's date`.",
    "derived_output_cost_usd": "Recomputed here, from output tokens and the output price.",
    "derived_total_cost_usd": "Sum of the two derived costs, and null unless both were "
                              "derivable -- see `cost_provenance`. Uniform across the "
                              "corpus and reproducible from the price table, but it is "
                              "what the run would have cost at that date's prices, not "
                              "what was charged.",
    "cost_provenance": "`derived` when both token counts were recorded and priced. "
                       "`partial_tokens` when only one was: the known component is "
                       "exported, the total is null, and the missing side is never "
                       "assumed to be zero. Otherwise why no cost could be derived at "
                       "all: `no_price_in_table`, `no_tokens`, `no_model_identity`.",
    "pricing_bucket_date": "Which dated entry in the price table was used. Not the run's "
                           "date: the nearest entry at or before it.",
    "pricing_age_days": "How stale that entry was at the run's date. Large values mean the "
                        "table had a gap, not that the price was wrong.",
    "pricing_input_price_per_million": "Input price used for the derived cost.",
    "pricing_output_price_per_million": "Output price used for the derived cost.",
    "pricing_model_key": "The name matched in the price table, after alias resolution.",
    "pricing_identity_source": "`response` when the stored response's own provider/model "
                               "was priced, `config` when it fell back to the configured "
                               "pair.",
    "conversation_id": "Provider-side conversation identifier, where recorded.",
    "has_parsed": "Whether the record stored a parsed structured output. The parsed value "
                  "itself is in the payload sidecar.",
    "has_raw_response": "Whether the record stored the raw provider envelope.",
}

SCORES_LONG = {
    "run_id": "Foreign key to `runs.run_id`.",
    "object_id": "Foreign key component to `requests`. Null for run-level observations.",
    "level": "`run`, `request` or `field`.",
    "field_path": "Which field a field-level observation refers to, preserved exactly as "
                  "the scorer keyed it -- including the empty string, which is a real key "
                  "for several thousand observations. Non-null exactly when `level` is "
                  "`field`; that invariant is how the CSV distinguishes an empty path from "
                  "a null one.",
    "metric_id": "Foreign key to `metrics.metric_id`. Scoped by benchmark and level, "
                 "because the same metric name means different things in different "
                 "benchmarks.",
    "value": "The observation. Finite numbers only; a non-numeric score is not represented "
             "here at all, and its absence is recorded in `scoring_status` instead.",
}

METRICS = {
    "metric_id": "Primary key: `<benchmark>.<level>.<source_metric>`.",
    "benchmark": "Which benchmark defines this metric.",
    "level": "`run`, `request` or `field`.",
    "source_metric": "The key as the scorer writes it.",
    "metric_role": "`performance` for a measurement, `count` for a tally, `parameter` for "
                   "a setting the scorer was given. Averaging across roles is meaningless.",
    "unit": "`ratio_0_1`, `ratio_0_100`, `error_rate`, `iou`, or a count noun.",
    "direction": "`higher_better`, `lower_better`, or `not_applicable` for counts and "
                 "parameters.",
    "min_value": "Lower bound where the metric has one.",
    "max_value": "Upper bound where the metric has one.",
    "aggregation": "How this metric may be combined: `sum` for counts, "
                   "`mean_over_requests`, `not_summable` for a ratio already averaged by "
                   "the scorer, `not_aggregatable` for a parameter.",
    "description": "What the metric measures and how it was produced.",
}

COVERAGE = {
    "table": "Which exported table the column belongs to.",
    "column": "The column being measured.",
    "group_dimension": "How the rows were grouped: `global`, `benchmark`, "
                       "`configured_provider`, `date`, or `benchmark+provider+date`.",
    "group_value": "The group. `<null>` where the grouping column itself is null -- those "
                   "rows are retained rather than dropped.",
    "n_rows": "Rows in this group. The denominator.",
    "n_non_null": "Rows where the column has a value.",
    "n_null": "Rows where it does not. Null means not recorded, never an inferred zero.",
    "n_invalid": "Rows where a numeric column holds a non-finite value. Zero throughout "
                 "this release: the extractor rejects them, and the count is kept so that "
                 "a future regression is visible rather than silent.",
    "fraction_non_null": "`n_non_null / n_rows`.",
}

BY_TABLE = {
    "runs": RUNS,
    "requests": REQUESTS,
    "scores_long": SCORES_LONG,
    "metrics": METRICS,
    "coverage": COVERAGE,
}


def check_complete(schemas):
    """Fail the build when a column has no description, or a description no column."""
    problems = []
    for name, schema in schemas.items():
        described = set(BY_TABLE.get(name, {}))
        actual = set(schema.names)
        for column in sorted(actual - described):
            problems.append("%s.%s has no description in columns.py" % (name, column))
        for column in sorted(described - actual):
            problems.append("%s.%s is described but not in the schema" % (name, column))
    if problems:
        raise ValueError("the data dictionary is out of step with the schema:\n  "
                         + "\n  ".join(problems))
