from scripts.ndr_export import TESTS_CSV
from scripts.results_index import TestCatalog


def get_all_tests():
    """Load and parse the benchmarks_tests.csv file.

    The reading and the type coercion live in `results_index.TestCatalog`, shared with
    the dataset export. The warning stays here: the shared reader is silent by design,
    and this pipeline's callers rely on seeing it on stdout.
    """
    if not TESTS_CSV.exists():
        print(f"⚠️ Tests CSV not found: {TESTS_CSV}")
        return []

    return TestCatalog.load().typed_rows()
