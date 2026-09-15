"""Calculate column completeness and validity statistics.

Produce one record per table, column, and supported group, with row, non-null,
null, and invalid-value counts and the non-null fraction. Numeric non-finite
values count as present and invalid; this is not a general schema validator.

Groups include the whole table and, where the required columns exist, benchmark,
configured provider, date, and their combination. Null grouping values are
retained under the label ``<null>``.
"""
import math

GROUPINGS = ("global", "benchmark", "configured_provider", "date",
             "benchmark+provider+date")

NULL_LABEL = "<null>"

COLUMNS = ("table", "column", "group_dimension", "group_value", "n_rows", "n_non_null",
           "n_null", "n_invalid", "fraction_non_null")


def _group_values(row, dimension):
    if dimension == "global":
        return "all"
    if dimension == "benchmark+provider+date":
        parts = (row.get("benchmark"), row.get("configured_provider"), row.get("date"))
        return " | ".join(p if p is not None else NULL_LABEL for p in parts)
    value = row.get(dimension)
    return value if value is not None else NULL_LABEL


def _is_invalid(value):
    return isinstance(value, float) and not math.isfinite(value)


def build(tables):
    """Return coverage records for ``{table_name: (rows, schema)}``.

    Skip grouping dimensions whose columns are absent from a table. The coverage
    writer applies the final output ordering.
    """
    out = []
    for name in sorted(tables):
        rows, schema = tables[name]
        columns = list(schema.names)

        # scores_long carries no benchmark or provider column of its own; grouping it by
        # the dimensions it does not have would produce one <null> bucket and no insight.
        dimensions = [d for d in GROUPINGS
                      if d == "global"
                      or all(part in columns
                             for part in (("benchmark", "configured_provider", "date")
                                          if d == "benchmark+provider+date" else (d,)))]

        for dimension in dimensions:
            buckets = {}
            for row in rows:
                key = _group_values(row, dimension)
                bucket = buckets.get(key)
                if bucket is None:
                    bucket = buckets[key] = {"n": 0,
                                             "non_null": dict((c, 0) for c in columns),
                                             "invalid": dict((c, 0) for c in columns)}
                bucket["n"] += 1
                for column in columns:
                    value = row.get(column)
                    if value is not None:
                        bucket["non_null"][column] += 1
                        if _is_invalid(value):
                            bucket["invalid"][column] += 1

            for key in sorted(buckets, key=str):
                bucket = buckets[key]
                for column in columns:
                    non_null = bucket["non_null"][column]
                    out.append({
                        "table": name,
                        "column": column,
                        "group_dimension": dimension,
                        "group_value": str(key),
                        "n_rows": bucket["n"],
                        "n_non_null": non_null,
                        "n_null": bucket["n"] - non_null,
                        "n_invalid": bucket["invalid"][column],
                        "fraction_non_null": (non_null / bucket["n"]
                                              if bucket["n"] else None),
                    })
    return out
