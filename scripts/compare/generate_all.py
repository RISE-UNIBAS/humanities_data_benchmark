"""Build the comparison data: detail first, since the index records which runs have it.

Usage (from project root):
    python -m scripts.compare.generate_all
"""

from scripts.compare.generate_compare_detail import generate_compare_detail
from scripts.compare.generate_compare_index import generate_compare_index


def generate_all():
    print("=== Step 1/2: Compare detail (re-scores runs lacking field detail) ===")
    generate_compare_detail()

    print("\n=== Step 2/2: Compare index ===")
    generate_compare_index()


if __name__ == "__main__":
    generate_all()
