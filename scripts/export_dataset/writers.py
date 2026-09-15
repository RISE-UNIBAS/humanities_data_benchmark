"""Serialize dataset tables and payloads with reproducible ordering and formats.

Sort rows by declared keys, write Parquet with explicit format and compression
settings, and omit variable filenames and timestamps from gzip headers. Byte
reproducibility also depends on the library versions used for serialization.

Generate CSV and Parquet from the same typed Arrow table. Validate CSV read-back
against that table, including exact floating-point representations and nulls.

CSV uses QUOTE_NOTNULL: nulls are unquoted empty fields, while empty strings are
quoted. The reader restores empty field identifiers using table semantics:
scores_long rows with level='field', and all rescored_fields rows. Parquet
preserves the distinction directly.
"""
import csv
import gzip
import json
import math
import os
import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PARQUET_VERSION = "2.6"
PARQUET_COMPRESSION = "zstd"

CSV_DIALECT = {
    "lineterminator": "\n",
    "quoting": csv.QUOTE_NOTNULL,
}

_SENTINEL_SORT = ""
"""Placeholder for null key components, ordered before non-null values by sort_rows."""


def sort_rows(rows, keys):
    def key(row):
        return tuple((row.get(k) is not None, row.get(k) if row.get(k) is not None
                      else _SENTINEL_SORT) for k in keys)
    return sorted(rows, key=key)


def _column(rows, name, field):
    values = [row.get(name) for row in rows]
    if pa.types.is_integer(field.type):
        values = [None if v is None else int(v) for v in values]
    elif pa.types.is_floating(field.type):
        values = [None if v is None else float(v) for v in values]
    elif pa.types.is_boolean(field.type):
        values = [None if v is None else bool(v) for v in values]
    else:
        values = [None if v is None else str(v) for v in values]
    return pa.array(values, type=field.type)


def to_table(rows, schema):
    return pa.Table.from_arrays(
        [_column(rows, f.name, f) for f in schema], schema=schema)


def _csv_value(value):
    """Convert a value to its CSV representation, preserving None.

    Use repr for finite floats, explicit spellings for non-finite floats, and
    lowercase true/false for booleans.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return repr(value)
    return str(value)


def write_csv(path, table):
    names = table.schema.names
    columns = [col.to_pylist() for col in table.columns]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, **CSV_DIALECT)
        writer.writerow(names)
        for i in range(table.num_rows):
            writer.writerow([_csv_value(col[i]) for col in columns])


def read_csv(path, schema, table=None):
    """Return CSV records parsed according to the supplied Arrow schema.

    Preserve string identifiers through schema-based conversion. Set table to
    scores_long or rescored_fields to restore empty field identifiers according
    to that table's rules; other empty cells become null.
    """
    types = dict((f.name, f.type) for f in schema)
    rows = []
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, **CSV_DIALECT)
        names = next(reader)
        for raw in reader:
            row = {}
            for name, cell in zip(names, raw):
                row[name] = _parse_cell(cell, types[name])
            # An empty `field_path` on disk is the empty string, not a null, wherever a
            # row is known to be a field observation. In `scores_long` that is the rows
            # with `level == "field"`; in `rescored_fields` it is every row, since the
            # table holds nothing else.
            if row.get("field_path") is None and (
                    table == "rescored_fields"
                    or (table == "scores_long" and row.get("level") == "field")):
                row["field_path"] = ""
            rows.append(row)
    return rows


def _parse_cell(cell, arrow_type):
    if cell is None or cell == "":
        return None
    if pa.types.is_integer(arrow_type):
        return int(cell)
    if pa.types.is_floating(arrow_type):
        return float(cell)
    if pa.types.is_boolean(arrow_type):
        return cell == "true"
    return cell


def write_parquet(path, table):
    pq.write_table(table, path, version=PARQUET_VERSION,
                   compression=PARQUET_COMPRESSION,
                   write_statistics=True, store_schema=True)


def check_round_trip(csv_path, table, table_name=None):
    """Raise AssertionError if CSV records differ from the supplied Arrow table.

    Check row counts, nulls, and column values. Compare floating-point repr strings
    exactly, without a numerical tolerance.
    """
    got = read_csv(csv_path, table.schema, table_name)
    expected = table.to_pylist()
    if len(got) != len(expected):
        raise AssertionError("CSV has %d rows, table has %d" % (len(got), len(expected)))
    for index, (a, b) in enumerate(zip(expected, got)):
        for name in table.schema.names:
            if a[name] is None or b[name] is None:
                if a[name] is not b[name]:
                    raise AssertionError(
                        "row %d column %r: %r round-tripped as %r; null and empty string "
                        "must stay distinct" % (index, name, a[name], b[name]))
            elif isinstance(a[name], float):
                if repr(a[name]) != repr(b[name]):
                    raise AssertionError("row %d column %r: %r != %r"
                                         % (index, name, a[name], b[name]))
            elif a[name] != b[name]:
                raise AssertionError("row %d column %r: %r != %r"
                                     % (index, name, a[name], b[name]))


def check_unique(rows, keys, table_name):
    seen = {}
    for row in rows:
        key = tuple(row.get(k) for k in keys)
        if key in seen:
            raise AssertionError(
                "%s: %r appears twice. %s is the table's key, so a duplicate means the "
                "extractor emitted the same observation from two places."
                % (table_name, key, " + ".join(keys)))
        seen[key] = True


def write_table(out_dir, name, rows, schema, sort_keys, unique_keys):
    rows = sort_rows(rows, sort_keys)
    check_unique(rows, unique_keys, name)
    table = to_table(rows, schema)
    write_parquet(out_dir / ("%s.parquet" % name), table)
    csv_path = out_dir / ("%s.csv" % name)
    write_csv(csv_path, table)
    check_round_trip(csv_path, table, table_name=name)
    return table.num_rows


def write_coverage(path, rows):
    """Sort coverage records and write CSV using the declared coverage columns."""
    from scripts.export_dataset.coverage import COLUMNS
    rows = sorted(rows, key=lambda r: (r["table"], r["column"], r["group_dimension"],
                                       str(r["group_value"])))
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, **CSV_DIALECT)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow([_csv_value(row[c]) for c in COLUMNS])


class JsonlGz:
    """Write UTF-8 JSONL with sorted object keys and fixed gzip header metadata."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._raw = open(self.path, "wb")
        # filename="" as well as mtime=0: given only a fileobj, GzipFile copies its
        # .name into the header, so two sidecars with identical contents would differ
        # by their own names and the header would carry a path into the build machine.
        self._gz = gzip.GzipFile(filename="", fileobj=self._raw, mode="wb", mtime=0,
                                 compresslevel=6)
        self.count = 0

    def write(self, record):
        line = json.dumps(record, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"))
        self._gz.write(line.encode("utf-8"))
        self._gz.write(b"\n")
        self.count += 1

    def close(self):
        self._gz.close()
        self._raw.close()


def publish(staging, final):
    """Publish a staged dataset, retaining the previous build during replacement.

    Move the existing final directory to a backup before renaming staging to final.
    If that rename fails, attempt to restore the backup. If restoration also fails,
    raise RuntimeError identifying the intact backup and staging directories.
    Remove the backup after successful publication.
    """
    staging, final = Path(staging), Path(final)
    if not staging.is_dir():
        raise RuntimeError("nothing staged at %s" % staging)
    previous = final.with_name(final.name + ".previous")

    if previous.exists() and final.exists():
        # A leftover from an interrupted publish. The live build is present, so this copy
        # is genuinely stale -- but only that combination makes it safe to remove.
        shutil.rmtree(previous)

    stepped_aside = False
    if final.exists():
        if previous.exists():
            raise RuntimeError(
                "Both %s and %s exist and %s does not. A previous publish was interrupted "
                "and one of them is the build you want; inspect them and rename by hand "
                "rather than letting this overwrite either." % (final, previous, final))
        _rename_or_explain(final, previous, staging)
        stepped_aside = True

    try:
        _rename_or_explain(staging, final, staging)
    except RuntimeError:
        if stepped_aside:
            try:
                os.rename(previous, final)
            except OSError as rollback_error:
                raise RuntimeError(
                    "Publishing failed and the previous build could not be put back.\n"
                    "  previous build: %s\n"
                    "  new build:      %s\n"
                    "Both are intact; rename one into %s by hand. (%s)"
                    % (previous, staging, final, rollback_error))
        raise

    if previous.exists():
        shutil.rmtree(previous)


def _rename_or_explain(source, target, staging):
    """Rename a directory or raise RuntimeError with recovery instructions.

    On failure, report the operating-system error, the staging location, and a
    publication retry command. The message includes guidance for Windows directory
    locks; publish handles restoration of any previous build.
    """
    try:
        os.rename(source, target)
    except OSError as error:
        raise RuntimeError(
            "Could not move %s into place: %s\n\n"
            "On Windows this usually means a shell, editor or file manager is sitting "
            "inside that directory. Close it or change directory, then publish the "
            "finished build with:\n"
            "    python -c \"from scripts.export_dataset import writers; "
            "writers.publish(r'%s', r'%s')\"\n\n"
            "Nothing was lost: the complete build is at %s and the previous one is "
            "untouched." % (source, error, staging, staging.with_name(
                staging.name.replace(".staging", "")), staging))
