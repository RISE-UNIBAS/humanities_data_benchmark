"""What each exported number means.

A long table makes every metric look alike: six columns, one row per observation, and
nothing in the shape to stop someone averaging a true-positive count with an F1. This
dictionary is what stops it. Each entry fixes a metric's role, unit, direction and whether
aggregating it means anything.

Metric ids are scoped `<benchmark>.<level>.<source_metric>` because the same spelling is
not the same measure across benchmarks. `fuzzy` is the clearest case: `book_advert_xml`
records `rapidfuzz.fuzz.ratio` on 0-100 while every other benchmark records a 0-1
similarity, and an unscoped `fuzzy` would put both in one column.

The dictionary is closed and the build enforces it: `extract.py` raises on any numeric
value whose metric id is not listed here. That is deliberate. A new scorer key should stop
a release and get a definition, not flow into the tables as an unexplained float.

Entries below were derived from a full scan of the corpus -- all 2,362 scoring files and
all 104,395 request records -- cross-checked against the scorers in
`benchmarks/*/benchmark.py`, not from a sample.
"""
from scripts.export_dataset.schema import METRIC_ROLES

FUZZY_BENCHMARKS = ("bibliographic_data", "blacklist_cards", "general_meeting_minutes",
                    "fraktur_adverts", "medieval_manuscripts", "test_benchmark")
"""Emit `calculate_fuzzy_score`, which is 0-1. `book_advert_xml` is deliberately absent."""

CER_BENCHMARKS = ("fraktur_adverts", "medieval_manuscripts")

F1_COUNT_BENCHMARKS = ("company_lists", "duty_rosters", "library_cards", "personnel_cards")
"""Share a scorer shape: micro/macro F1 at run level, per-request F1 with TP/FP/FN."""

FIELD_SCORE_BENCHMARKS = F1_COUNT_BENCHMARKS
"""The only four with `field_scores` in *stored* records. Eight more benchmarks gained the
key in v0.5.5, but no run has been re-executed since, so the corpus has none of theirs."""

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
"""Keys that carry no numeric observation. `message` is the text beside
`book_advert_xml`'s failure score; `field_scores` is nested detail exported at field
level; `__error` is a scorer's own marker."""

NOT_IMPLEMENTED = "niy"
"""What a scorer writes instead of a score when it has none. A string, and never to be
coerced to zero -- a benchmark with no scorer is not a benchmark that scored zero."""
