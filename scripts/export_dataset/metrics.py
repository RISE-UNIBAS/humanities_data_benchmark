"""Define and validate numeric metrics exported in scores_long.

Each metric definition specifies its role, unit, direction, range, and aggregation
rule. Identifiers use ``<benchmark>.<level>.<source_metric>`` so similarly named
metrics remain distinguishable across tasks and evaluation levels.

For example, book_advert_xml reports fuzzy similarity on a 0-100 scale, while
other registered fuzzy metrics use 0-1. Definitions are based on stored scoring
records and benchmark scorers. Extraction rejects unregistered numeric metrics.
"""
import math

from scripts.export_dataset.schema import METRIC_ROLES

FUZZY_BENCHMARKS = ("bibliographic_data", "blacklist_cards", "general_meeting_minutes",
                    "fraktur_adverts", "medieval_manuscripts", "test_benchmark")
"""Benchmarks with registered fuzzy similarity metrics on a 0-1 scale."""

CER_BENCHMARKS = ("fraktur_adverts", "medieval_manuscripts")

F1_COUNT_BENCHMARKS = ("company_lists", "duty_rosters", "library_cards", "personnel_cards")
"""Benchmarks with run-level micro/macro F1 and request-level F1 and TP/FP/FN counts."""

FIELD_SCORE_BENCHMARKS = F1_COUNT_BENCHMARKS
"""Benchmarks with registered field-level metrics in the stored-score dictionary."""

BUSINESS_LETTER_CATEGORIES = ("send_date", "sender_persons", "receiver_persons")


def _entry(benchmark, level, metric, role, unit, direction, lo, hi, aggregation, description):
    assert role in METRIC_ROLES, role
    return {
        "metric_id": "%s.%s.%s" % (benchmark, level, metric),
        "benchmark": benchmark,
        "level": level,
        "source_metric": metric,
        "metric_role": role,
        "unit": unit,
        "direction": direction,
        "min_value": lo,
        "max_value": hi,
        "aggregation": aggregation,
        "description": description,
    }


def _build():
    rows = []
    add = rows.append

    # --- similarity -----------------------------------------------------------
    for b in FUZZY_BENCHMARKS:
        for level in ("run", "request"):
            add(_entry(b, level, "fuzzy", "performance", "ratio_0_1", "higher_better",
                       0.0, 1.0, "mean_over_requests",
                       "Fuzzy string similarity from scoring_helper.calculate_fuzzy_score. "
                       "The run value is the scorer's own mean, not a re-aggregation."))

    for level in ("run", "request"):
        add(_entry("book_advert_xml", level, "fuzzy", "performance", "ratio_0_100",
                   "higher_better", 0.0, 100.0, "mean_over_requests",
                   "rapidfuzz.fuzz.ratio, on 0-100. Not comparable with the 0-1 `fuzzy` "
                   "every other benchmark records without rescaling."))

    add(_entry("book_advert_xml", "request", "score", "performance", "ratio_0_100",
               "higher_better", 0.0, 100.0, "mean_over_requests",
               "Emitted as 0.0 on the failure path, alongside a `message`, where the "
               "success path emits `fuzzy`. A real observation of a failed request, and "
               "not to be confused with the run-level string \"niy\"."))

    # --- character error rate -------------------------------------------------
    for b in CER_BENCHMARKS:
        for level in ("run", "request"):
            add(_entry(b, level, "cer", "performance", "error_rate", "lower_better",
                       0.0, None, "mean_over_requests",
                       "Character error rate. Lower is better, so it must not be pooled "
                       "with the similarity metrics without inverting it."))

    # --- F1 family ------------------------------------------------------------
    for b in F1_COUNT_BENCHMARKS:
        for metric, desc in (
            ("f1_micro", "Micro-averaged F1 over all field instances in the run."),
            ("f1_macro", "Macro-averaged F1, weighting each field equally."),
            ("micro_precision", "Micro-averaged precision over the run."),
            ("micro_recall", "Micro-averaged recall over the run."),
        ):
            add(_entry(b, "run", metric, "performance", "ratio_0_1", "higher_better",
                       0.0, 1.0, "not_summable", desc))
        for metric in ("total_instances", "total_tp", "total_fp", "total_fn"):
            add(_entry(b, "run", metric, "count", "instances", "not_applicable",
                       0.0, None, "sum",
                       "Field instances counted by the scorer over the whole run. A "
                       "sufficient statistic: precision, recall and F1 can be rebuilt "
                       "from these, which a mean of F1 scores cannot."))

        for metric, desc in (
            ("f1_score", "F1 for this one request."),
            ("precision", "Precision for this one request."),
            ("recall", "Recall for this one request."),
        ):
            add(_entry(b, "request", metric, "performance", "ratio_0_1", "higher_better",
                       0.0, 1.0, "not_summable", desc))
        for metric in ("true_positives", "false_positives", "false_negatives"):
            add(_entry(b, "request", metric, "count", "instances", "not_applicable",
                       0.0, None, "sum",
                       "Field instances for this request. Summable across requests; the "
                       "F1 beside it is not."))
        add(_entry(b, "request", "total_fields", "count", "fields", "not_applicable",
                   0.0, None, "sum",
                   "How many fields the scorer compared for this request. A denominator, "
                   "not a result."))

    for b in FIELD_SCORE_BENCHMARKS:
        add(_entry(b, "field", "score", "performance", "ratio_0_1", "higher_better",
                   0.0, 1.0, "not_summable",
                   "Per-field similarity from the scorer's own `field_scores`. The field "
                   "path is preserved literally, including the empty-string key that "
                   "6,080 stored records use."))

    # --- business letters: counts only ----------------------------------------
    for metric in ("f1_macro", "f1_micro"):
        add(_entry("business_letters", "run", metric, "performance", "ratio_0_1",
                   "higher_better", 0.0, 1.0, "not_summable",
                   "Macro/micro F1 over the three scored categories. The per-category "
                   "counts behind it are never written to scoring.json, so a category "
                   "breakdown has to be rebuilt from the request rows."))
    for category in BUSINESS_LETTER_CATEGORIES:
        for suffix, name in (("tp", "True positives"), ("fp", "False positives"),
                             ("fn", "False negatives")):
            add(_entry("business_letters", "request", "%s_%s" % (category, suffix),
                       "count", "extractions", "not_applicable", 0.0, None, "sum",
                       "%s for the %s category of one letter. These nine counts are the "
                       "whole of what this scorer records per request: it assigns no "
                       "per-request similarity." % (name, category.replace("_", " "))))

    # --- layout ---------------------------------------------------------------
    for level in ("run", "request"):
        for metric, desc in (
            ("f1", "F1 over matched page regions."),
            ("precision", "Precision over matched page regions."),
            ("recall", "Recall over matched page regions."),
        ):
            add(_entry("magazine_pages", level, metric, "performance", "ratio_0_1",
                       "higher_better", 0.0, 1.0, "not_summable", desc))
        add(_entry("magazine_pages", level, "mean_iou", "performance", "iou",
                   "higher_better", 0.0, 1.0, "not_summable",
                   "Mean intersection-over-union of the matched boxes. A measurement."))
        for metric in ("true_positives", "false_positives", "false_negatives"):
            add(_entry("magazine_pages", level, metric, "count", "regions",
                       "not_applicable", 0.0, None, "sum",
                       "Page regions counted at the IoU threshold in force."))
    add(_entry("magazine_pages", "run", "num_pages", "count", "pages", "not_applicable",
               0.0, None, "sum", "Pages the scorer examined in this run."))
    add(_entry("magazine_pages", "request", "iou_threshold", "parameter", "iou",
               "not_applicable", 0.0, 1.0, "not_aggregatable",
               "The overlap a box had to reach to count as matched. Configuration, not a "
               "result: averaging it with mean_iou is meaningless."))

    add(_entry("book_advert_xml", "run", "n", "count", "items", "not_applicable",
               0.0, None, "sum", "Items the scorer averaged over, where it records one."))

    # --- scaffolds ------------------------------------------------------------
    add(_entry("test_benchmark2", "request", "score", "parameter", "none",
               "not_applicable", None, None, "not_aggregatable",
               "Fixed placeholder from a scaffold benchmark used to exercise the harness. "
               "Not a measurement of anything."))
    for metric in ("score_3", "scoresdfsdf_2"):
        add(_entry("test_benchmark2", "request", metric, "parameter", "none",
                   "not_applicable", None, None, "not_aggregatable",
                   "Fixed placeholder from a scaffold benchmark. Not a measurement."))

    return rows


DICTIONARY = _build()

BY_ID = dict((row["metric_id"], row) for row in DICTIONARY)

assert len(BY_ID) == len(DICTIONARY), "duplicate metric_id in the dictionary"


def metric_id(benchmark, level, source_metric):
    return "%s.%s.%s" % (benchmark, level, source_metric)


def is_known(benchmark, level, source_metric):
    return metric_id(benchmark, level, source_metric) in BY_ID


NON_METRIC_KEYS = frozenset(("field_scores", "message", "__error"))
"""Keys excluded from top-level numeric metric extraction.

Field detail is processed separately; messages and error markers are metadata.
"""

NOT_IMPLEMENTED = "niy"
"""Stored marker for unimplemented scoring; it is not a numeric zero."""


SUFFICIENT_STATISTICS = {
    "business_letters": frozenset("%s_tp" % c for c in BUSINESS_LETTER_CATEGORIES),
}
"""Required request-level counts for benchmarks without a performance metric.

Business Letters requires a finite true-positive count for each scored category
before a request is classified as scored.
"""


def numeric(value):
    """Return a finite int or float, or None for booleans and other invalid values."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(value) else None


def is_scored(benchmark, score):
    """Return whether a request contains the benchmark's required scoring data.

    For benchmarks in SUFFICIENT_STATISTICS, require every listed count to be finite.
    Otherwise require at least one finite, registered request-level performance
    metric. Parameters, placeholders, and field-detail containers do not qualify.
    """
    if not isinstance(score, dict) or not benchmark:
        return False

    required = SUFFICIENT_STATISTICS.get(benchmark)
    if required is not None:
        return all(numeric(score.get(key)) is not None for key in required)

    for key, value in score.items():
        if key in NON_METRIC_KEYS:
            continue
        entry = BY_ID.get(metric_id(benchmark, "request", key))
        if entry and entry["metric_role"] == "performance" and numeric(value) is not None:
            return True
    return False
