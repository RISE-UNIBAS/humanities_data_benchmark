"""Build the comparison data: detail first, since the index records which runs have it; then the
run counts per benchmark version.

Usage (from project root):
    python -m scripts.compare.generate_all
"""

from scripts.compare.generate_compare_detail import generate_compare_detail
from scripts.compare.generate_compare_index import generate_compare_index
from scripts.compare.generate_version_runs import generate_version_runs


def generate_all():
    print("=== Step 1/3: Compare detail (re-scores runs lacking field detail) ===")
    generate_compare_detail()

    print("\n=== Step 2/3: Compare index ===")
    generate_compare_index()

    print("\n=== Step 3/3: Runs per benchmark version ===")
    generate_version_runs()


if __name__ == "__main__":
    generate_all()
