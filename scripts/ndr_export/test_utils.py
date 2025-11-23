import csv

from scripts.ndr_export import TESTS_CSV


def get_all_tests():
    """Load and parse the benchmarks_tests.csv file."""

    tests = []
    if not TESTS_CSV.exists():
        print(f"⚠️ Tests CSV not found: {TESTS_CSV}")
        return tests

    with TESTS_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up empty string values
            cleaned_row = {}
            for key, value in row.items():
                if value == "":
                    cleaned_row[key] = None
                elif key == "temperature" and value:
                    cleaned_row[key] = float(value)
                elif key == "legacy_test":
                    cleaned_row[key] = value.lower() == "true"
                else:
                    cleaned_row[key] = value
            tests.append(cleaned_row)

    return tests