"""Copy hand-maintained data files into the NDR export directory.

Most of collected_results/ is derived from results/ and benchmarks/. These two
files are not — they are maintained under scripts/data/ and consumed verbatim by
the NDR viz widget:

  pricing.json        per-date model prices (maintained via scripts/update_pricing.py)
  model_aliases.json  csv-name -> result-file-name map

The widget joins benchmark_export.json to test_runs_export.json on
provider + '/' + model. Those two exports do not always spell a model the same
way: benchmark_export uses the name from benchmarks_tests.csv, while
test_runs_export uses the name the provider's result file reports (e.g.
'meta-models/Muse-Glimmer-30B:together' vs 'meta-models/Muse-Glimmer-30B').
model_aliases.json is what reconciles them, so without it the widget silently
loses cost and speed figures for every aliased model.

Copying them here keeps collected_results/ a complete, self-contained export —
one directory to hand to the viz repo instead of two.
"""

import shutil

from scripts.ndr_export import EXPORT_PATH, MODEL_ALIASES_PATH, PRICING_PATH

STATIC_FILES = [PRICING_PATH, MODEL_ALIASES_PATH]


def copy_static_data():
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)

    copied = 0
    for src in STATIC_FILES:
        if not src.exists():
            print(f"Warning: static data file not found, skipping: {src}")
            continue
        dest = EXPORT_PATH / src.name
        shutil.copy2(src, dest)
        print(f"Copied {src.name} to {dest}")
        copied += 1

    print(f"Copied {copied}/{len(STATIC_FILES)} static data files.")


if __name__ == "__main__":
    copy_static_data()
