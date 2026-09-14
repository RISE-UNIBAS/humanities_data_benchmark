"""Writing the tables so that the same inputs always produce the same bytes.

Three things break byte-identical rebuilds and all three are handled here: gzip stamps the
current time into its header, Parquet records the writer version, and any iteration over a
set or a directory can reorder rows. Rows are sorted on their declared key before writing,
gzip mtime is pinned to 0, and the Parquet writer version is pinned and recorded in the
manifest.

The CSV is generated from the same typed rows as the Parquet, not written independently,
and `check_round_trip` reads both back and compares them. That is the only way to know the
two agree: sharing a source frame does not prevent a serialisation difference.

CSV null encoding is `csv.QUOTE_NOTNULL` (Python 3.12+): on disk a null is a bare empty
field and an empty string is a quoted `""`, so the bytes are unambiguous. Python's own
`csv.reader` does not honour that distinction on the way back in -- it returns `''` for
both, whatever `quoting` is set to -- and a hand-rolled quote-aware parser is not worth
the risk, because `error_message`, `role_description` and `rules_json` can all contain
newlines inside a quoted field.

So the one column where an empty string is real data is disambiguated by a second column
instead. `scores_long.field_path` is non-null exactly when `level == "field"`; run- and
request-level rows have no field path at all. `read_csv` applies that rule, the extractor
maintains it, and an integrity test asserts it over the whole corpus. Parquet carries the
distinction natively and remains the lossless copy.
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
"""Nulls sort first, explicitly, rather than however the runtime happens to compare
None with a string. `scores_long` mixes null and non-null object ids in one key."""


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
    """Serialise one cell so it reads back as the same Python object.

    Floats go through `repr`, which in Python 3 is the shortest string that round-trips
    exactly; `%f` would quietly truncate. Booleans are spelled out rather than written as
    0/1, which a reader cannot tell from an integer column.
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
    """Read a table back under its declared schema.

    Ship this with the dataset. `pandas.read_csv` will not reproduce it: it turns a
    leading-zero object id like `00414956` into an integer, and it cannot rebuild the
    empty `field_path` described above.
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
            if (table == "scores_long" and row.get("level") == "field"
                    and row.get("field_path") is None):
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
    """Assert the CSV reads back equal to the Parquet source, column by column.

    Floats are compared by their repr so that a value which serialised differently is a
    failure rather than something an epsilon comparison hides.
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
    """coverage.csv, sorted and written under the same CSV contract as the tables.

    Not a pyarrow table: it is derived from the others rather than extracted, and giving
    it a schema would imply it is part of the data model.
    """
    from scripts.export_dataset.coverage import COLUMNS
    rows = sorted(rows, key=lambda r: (r["table"], r["column"], r["group_dimension"],
                                       str(r["group_value"])))
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, **CSV_DIALECT)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow([_csv_value(row[c]) for c in COLUMNS])


class JsonlGz:
    """A gzip JSONL sidecar with a pinned header, so two builds give the same bytes."""

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
    """Move a finished build into place, replacing any previous one only on success."""
    staging, final = Path(staging), Path(final)
    if not staging.is_dir():
        raise RuntimeError("nothing staged at %s" % staging)
    previous = final.with_name(final.name + ".previous")
    if previous.exists():
        shutil.rmtree(previous)
    if final.exists():
        _rename_or_explain(final, previous, staging)
    _rename_or_explain(staging, final, staging)
    if previous.exists():
        shutil.rmtree(previous)


def _rename_or_explain(source, target, staging):
    """Rename, or fail with the reason and the reassurance.

    Windows refuses to rename a directory while any process has it, or anything under it,
    as a working directory -- a shell left sitting in `dataset/examples` is enough, and it
    is a natural place to be sitting, since that is where the example script lives. The
    bare PermissionError says none of that, and worse, it arrives after a four-minute build
    and looks like the build was lost. It was not: the completed output is in staging.
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
