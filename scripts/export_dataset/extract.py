"""Step 3: turn the stored result tree into rows.

One pass over the corpus produces every table at once, because they share a key and a
second pass could disagree with the first. Reading is direct `json.load` through
`results_index`; no scorer runs, no cost is recalculated behind the caller's back, no
timestamp is invented.

The discipline throughout is that a fact and the absence of a fact are different values.
A token count that was never recorded is null, not zero. A run with no `scoring.json` is a
row with `scoring_status = "missing"`, not a missing row. A request file that will not
parse keeps its key, its source path and a diagnostic, and its payload-derived columns are
null. The dataset is meant to be able to say "this is not known", which a table built by
skipping cannot.

Costs are the one place where this export computes rather than copies, and it does both.
`stored_*` is what the run recorded, untouched. `derived_*` is recomputed from the
recorded tokens and the price in force on the run's date, via the same resolver the
frontend uses. They can disagree -- a run costed against a stale table will -- and the
export keeps both rather than picking a winner.
"""
import json
import math
import re
from datetime import datetime

from scripts.export_dataset import metrics as M
from scripts.export_dataset.inventory import relative_path
from scripts.export_dataset.schema import empty_string_is_null
from scripts.ndr_export.pricing_resolver import resolve_pricing
from scripts.results_index import (TestCatalog, benchmark_meta, iter_request_records,
                                   iter_run_dirs, read_run, read_scoring)

LINE_OBJECT_ID = re.compile(r"^line_(\d+)$")
"""`line` is optional presentation metadata and never a join key. It is populated only
when the whole object id is `line_<digits>`: `line_10a` and `0002_p002` are not lines."""

COST_SUMMARY_KEY = "cost_summary"


def _clean(value, table="", column=""):
    """Empty strings become null, except where the empty string is real data."""
    if isinstance(value, str) and value == "" and empty_string_is_null(table, column):
        return None
    return value


def _number(value):
    """A finite int or float, or None. Booleans are not numbers here.

    `isinstance(True, int)` is the trap: without this guard a boolean field would export
    as 1.0 and be averaged with real measurements.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(value) else None


def _int(value):
    n = _number(value)
    return None if n is None else int(n)


def _text(value):
    if value is None or isinstance(value, (dict, list)):
        return None
    return _clean(str(value))


def parse_timestamp(raw):
    """(timestamp_utc, diagnostic-or-None).

    Every timestamp in this corpus is naive -- no offset, no Z -- so this returns None for
    all of them. That is the point: converting a naive local time to UTC means inventing
    a timezone, and the run's own machine is not recorded anywhere. The column exists,
    stays null, and the README says so rather than the export guessing an offset.
    """
    if not raw:
        return None, None
    try:
        parsed = datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return None, "unparseable_timestamp"
    if parsed.tzinfo is None:
        return None, None
    return parsed.astimezone(tz=None).isoformat(), None


def scoring_status_of(read_status, value):
    if read_status == "missing":
        return "missing"
    if read_status != "ok" or not isinstance(value, dict):
        return "invalid"
    if value.get("score") == M.NOT_IMPLEMENTED:
        return "not_implemented"
    for key, item in value.items():
        if key == COST_SUMMARY_KEY or key in M.NON_METRIC_KEYS:
            continue
        if _number(item) is not None:
            return "numeric_metrics_present"
    return "no_numeric_metrics"


class Extractor:
    def __init__(self, results_path=None, catalog=None):
        self.catalog = catalog if catalog is not None else TestCatalog.load()
        self.results_path = results_path
        self.runs = []
        self.requests = []
        self.scores = []
        self.diagnostics = []
        self.payloads = {}          # benchmark -> list of records
        self.run_payloads = []
        self.invalid_sources = []   # (relative path, absolute path)
        self._meta_cache = {}
        self._unknown_metrics = []

    # -- helpers ---------------------------------------------------------------

    def _meta(self, benchmark):
        if benchmark not in self._meta_cache:
            read = benchmark_meta(benchmark) if benchmark else None
            self._meta_cache[benchmark] = (
                read.value if read is not None and read.status == "ok"
                and isinstance(read.value, dict) else None)
        return self._meta_cache[benchmark]

    def _diag(self, source_path, issue, severity, handling):
        self.diagnostics.append({
            "source_path": source_path,
            "issue": issue,
            "severity": severity,
            "handling": handling,
        })

    def _score_row(self, run_id, object_id, level, field_path, benchmark, key, value):
        number = _number(value)
        if number is None:
            return
        if not M.is_known(benchmark, level, key):
            self._unknown_metrics.append((benchmark, level, key))
            return
        self.scores.append({
            "run_id": run_id,
            "object_id": object_id,
            "level": level,
            "field_path": field_path,
            "metric_id": M.metric_id(benchmark, level, key),
            "value": float(number),
        })

    # -- the pass --------------------------------------------------------------

    def run(self):
        for run in (iter_run_dirs(self.results_path) if self.results_path
                    else iter_run_dirs()):
            self._one_run(run)
        if self._unknown_metrics:
            seen = sorted(set(self._unknown_metrics))
            raise ValueError(
                "%d numeric metric(s) have no entry in metrics.py, so the export cannot "
                "say what they measure. Add a definition before releasing:\n  %s"
                % (len(seen), "\n  ".join("%s.%s.%s" % s for s in seen)))
        return self

    def _one_run(self, run):
        config = self.catalog.raw_by_id().get(run.test_id)
        typed = self.catalog.typed_by_id().get(run.test_id) or {}
        benchmark = self.catalog.benchmark_of(run.test_id)
        meta = self._meta(benchmark) if benchmark else None
        source = relative_path(run.path)

        files = read_run(run)
        request_rows = []
        for request, read in iter_request_records(files):
            request_rows.append(
                self._one_request(run, request, read, benchmark, typed, meta))

        scoring = read_scoring(files)
        status = scoring_status_of(scoring.status, scoring.value)
        if scoring.status == "invalid":
            self._diag(relative_path(files.scoring_path), "unparseable_scoring_json",
                       "warning", "row kept with scoring_status=invalid; bytes preserved "
                       "under payloads/invalid/")
            self.invalid_sources.append(files.scoring_path)

        cost = {}
        if scoring.status == "ok" and isinstance(scoring.value, dict):
            self.run_payloads.append({
                "run_id": run.run_id,
                "source_path": source,
                "source_record": scoring.value,
            })
            raw_cost = scoring.value.get(COST_SUMMARY_KEY)
            cost = raw_cost if isinstance(raw_cost, dict) else {}
            if benchmark:
                for key, value in scoring.value.items():
                    if key == COST_SUMMARY_KEY or key in M.NON_METRIC_KEYS:
                        continue
                    self._score_row(run.run_id, None, "run", None, benchmark, key, value)

        self.runs.append(self._run_row(run, source, config, typed, benchmark, meta,
                                       request_rows, scoring, status, cost))

    def _one_request(self, run, request, read, benchmark, typed, meta):
        source = relative_path(request.path)

        if request.object_id is None:
            self._diag(source, "unresolvable_object_id", "blocking",
                       "row kept with a null object_id; the filename matches neither the "
                       "directory's test id nor a prefix observed beside it")
        if read.status == "invalid":
            self._diag(source, "unparseable_request_json", "warning",
                       "row kept with payload columns null; bytes preserved under "
                       "payloads/invalid/")
            self.invalid_sources.append(request.path)
        elif read.status == "unreadable":
            self._diag(source, "unreadable_request_file", "blocking",
                       "row kept with payload columns null")

        record = read.value if isinstance(read.value, dict) else None
        usage = record.get("usage") if record else None
        usage = usage if isinstance(usage, dict) else {}

        line = None
        if request.object_id:
            match = LINE_OBJECT_ID.match(request.object_id)
            if match:
                line = int(match.group(1))

        timestamp_raw = _text(record.get("timestamp")) if record else None
        timestamp_utc, ts_issue = parse_timestamp(timestamp_raw)
        if ts_issue:
            self._diag(source, ts_issue, "warning", "timestamp_utc left null")

        response_provider = _text(record.get("provider")) if record else None
        response_model = _text(record.get("model")) if record else None

        score = record.get("score") if record else None
        if isinstance(score, dict) and benchmark:
            for key, value in score.items():
                if key in M.NON_METRIC_KEYS:
                    continue
                self._score_row(run.run_id, request.object_id, "request", None,
                                benchmark, key, value)
            field_scores = score.get("field_scores")
            if isinstance(field_scores, dict):
                for path, entry in field_scores.items():
                    if isinstance(entry, dict):
                        self._score_row(run.run_id, request.object_id, "field",
                                        str(path), benchmark, "score",
                                        entry.get("score"))

        if record is not None:
            self.payloads.setdefault(benchmark or "_unresolved_benchmark", []).append({
                "run_id": run.run_id,
                "object_id": request.object_id,
                "source_path": source,
                "source_record": record,
            })

        error = record.get("error") if record else None
        error_message = record.get("error_message") if record else None
        is_error = None if record is None else bool(error or error_message)

        tokens = dict(
            input_tokens=_int(usage.get("input_tokens")),
            output_tokens=_int(usage.get("output_tokens")),
            total_tokens=_int(usage.get("total_tokens")),
            cached_tokens=_int(usage.get("cached_tokens")),
            cache_creation_tokens=_int(usage.get("cache_creation_tokens")),
            cache_read_tokens=_int(usage.get("cache_read_tokens")),
        )
        derived = self._derive_cost(run.date, response_provider, response_model,
                                    typed, tokens)

        row = {
            "run_id": run.run_id,
            "object_id": request.object_id,
            "test_id": run.test_id,
            "date": run.date,
            "benchmark": benchmark,
            "source_path": source,
            "line": line,
            "configured_provider": _clean(typed.get("provider")),
            "configured_model": _clean(typed.get("model")),
            "response_provider": response_provider,
            "response_model": response_model,
            "parse_status": read.status,
            "timestamp_raw": timestamp_raw,
            "timestamp_utc": timestamp_utc,
            "duration_s": _number(record.get("duration")) if record else None,
            "finish_reason": _text(record.get("finish_reason")) if record else None,
            "is_error": is_error,
            "error_message": _text(error_message) if record else None,
            "scoring_status": self._request_scoring_status(record, score),
            "stored_input_cost_usd": _number(usage.get("input_cost_usd")),
            "stored_output_cost_usd": _number(usage.get("output_cost_usd")),
            "stored_estimated_cost_usd": _number(usage.get("estimated_cost_usd")),
            "conversation_id": _text(record.get("conversation_id")) if record else None,
            "has_parsed": None if record is None else record.get("parsed") is not None,
            "has_raw_response": (None if record is None
                                 else record.get("raw_response") is not None),
        }
        row.update(tokens)
        row.update(derived)
        self.requests.append(row)
        return row

    @staticmethod
    def _request_scoring_status(record, score):
        if record is None:
            return "missing"
        if score is None:
            return "missing"
        if score == M.NOT_IMPLEMENTED:
            return "not_implemented"
        if not isinstance(score, dict):
            return "invalid"
        for key, value in score.items():
            if key in M.NON_METRIC_KEYS:
                continue
            if _number(value) is not None:
                return "numeric_metrics_present"
        return "no_numeric_metrics"

    @staticmethod
    def _derive_cost(date, response_provider, response_model, typed, tokens):
        """Recompute cost from recorded tokens and the price in force on the run's date.

        The response's own provider/model is preferred over the configured pair, because
        that is what the alias map is keyed on and what actually served the request. The
        window is unbounded: the pricing table has gaps longer than 30 days in the past,
        and a price with an explicit age attached is more useful than no price at all.
        """
        blank = {
            "derived_input_cost_usd": None,
            "derived_output_cost_usd": None,
            "derived_total_cost_usd": None,
            "pricing_bucket_date": None,
            "pricing_age_days": None,
            "pricing_input_price_per_million": None,
            "pricing_output_price_per_million": None,
            "pricing_model_key": None,
            "pricing_identity_source": None,
        }
        provider, model, origin = response_provider, response_model, "response"
        if not (provider and model):
            provider, model, origin = typed.get("provider"), typed.get("model"), "config"
        if not (provider and model):
            return dict(blank, cost_provenance="no_model_identity")

        if tokens["input_tokens"] is None and tokens["output_tokens"] is None:
            return dict(blank, cost_provenance="no_tokens",
                        pricing_identity_source=origin)

        price = resolve_pricing(provider, model, date, max_age_days=None)
        if price is None:
            return dict(blank, cost_provenance="no_price_in_table",
                        pricing_identity_source=origin)

        input_cost = (tokens["input_tokens"] or 0) / 1e6 * price.input_price
        output_cost = (tokens["output_tokens"] or 0) / 1e6 * price.output_price
        return {
            "derived_input_cost_usd": input_cost,
            "derived_output_cost_usd": output_cost,
            "derived_total_cost_usd": input_cost + output_cost,
            "cost_provenance": "derived",
            "pricing_bucket_date": price.bucket_date,
            "pricing_age_days": price.age_days,
            "pricing_input_price_per_million": price.input_price,
            "pricing_output_price_per_million": price.output_price,
            "pricing_model_key": getattr(price, "model_key", None) or model,
            "pricing_identity_source": origin,
        }

    def _run_row(self, run, source, config, typed, benchmark, meta, request_rows,
                 scoring, status, cost):
        n_requests = len(request_rows)
        n_valid = sum(1 for r in request_rows if r["parse_status"] == "ok")
        n_errors = sum(1 for r in request_rows if r["is_error"])
        n_scored = sum(1 for r in request_rows
                       if r["scoring_status"] == "numeric_metrics_present")

        stored = [r["stored_estimated_cost_usd"] for r in request_rows
                  if r["stored_estimated_cost_usd"] is not None]
        derived = [r["derived_total_cost_usd"] for r in request_rows
                   if r["derived_total_cost_usd"] is not None]

        legacy = typed.get("legacy_test")
        display = None
        if meta is not None:
            display = bool(meta.get("display", True))
        hidden = None
        if legacy is not None or display is not None:
            hidden = bool(legacy) or (display is False)

        rules = config.get("rules") if config else None

        return {
            "run_id": run.run_id,
            "test_id": run.test_id,
            "date": run.date,
            "benchmark": benchmark,
            "source_path": source,
            "config_status": "matched" if config else "unknown_test_id",
            "configured_provider": _clean(typed.get("provider")),
            "configured_model": _clean(typed.get("model")),
            "dataclass": _clean(typed.get("dataclass")),
            "temperature": _number(typed.get("temperature")),
            "role_description": _clean(typed.get("role_description")),
            "prompt_file": _clean(typed.get("prompt_file")),
            "rules_json": _clean(rules),
            "legacy_test": legacy,
            "benchmark_display": display,
            "hidden": hidden,
            "n_requests": n_requests,
            "n_valid_requests": n_valid,
            "n_explicit_errors": n_errors,
            "n_scored": n_scored,
            "has_scoring": scoring.status != "missing",
            "scoring_status": status,
            "recorded_total_input_tokens": _int(cost.get("total_input_tokens")),
            "recorded_total_output_tokens": _int(cost.get("total_output_tokens")),
            "recorded_total_tokens": _int(cost.get("total_tokens")),
            "recorded_input_cost_usd": _number(cost.get("input_cost_usd")),
            "recorded_output_cost_usd": _number(cost.get("output_cost_usd")),
            "recorded_total_cost_usd": _number(cost.get("total_cost_usd")),
            "recorded_pricing_date": _text(cost.get("pricing_date")),
            "recorded_input_price_per_million": _number(cost.get("input_price_per_million")),
            "recorded_output_price_per_million": _number(cost.get("output_price_per_million")),
            "n_requests_with_stored_cost": len(stored),
            "observed_stored_cost_usd": sum(stored) if stored else None,
            "stored_cost_coverage_fraction": (len(stored) / n_requests
                                              if n_requests else None),
            "stored_cost_complete_for_saved_requests": (
                bool(n_requests) and len(stored) == n_requests),
            "n_requests_with_derived_cost": len(derived),
            "observed_derived_cost_usd": sum(derived) if derived else None,
            "derived_cost_coverage_fraction": (len(derived) / n_requests
                                               if n_requests else None),
            "tags_json": (json.dumps(meta.get("tags"), sort_keys=True)
                          if meta and meta.get("tags") is not None else None),
            "contributors_json": (json.dumps(meta.get("contributors"), sort_keys=True)
                                  if meta and meta.get("contributors") is not None
                                  else None),
        }
