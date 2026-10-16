"""Run all NDR export generators in the correct order.

Usage (from project root):
    python -m scripts.ndr_export.generate_all
"""

from scripts.ndr_export.generate_benchmark_export import generate_benchmark_export
from scripts.ndr_export.generate_test_runs_export import generate_test_runs_export
from scripts.ndr_export.generate_compare_detail import generate_compare_detail
from scripts.ndr_export.generate_compare_index import generate_compare_index
from scripts.ndr_export.generate_multi_select_data import generate_multi_select_data
from scripts.ndr_export.generate_visualizations import generate_visualizations
from scripts.ndr_export.generate_vars import generate_vars
from scripts.ndr_export.copy_static_data import copy_static_data
from scripts.ndr_export.generate_site_data import generate_site_data


def generate_all():
    print("=== Step 1/9: Benchmark export ===")
    generate_benchmark_export()

    print("\n=== Step 2/9: Test runs export ===")
    generate_test_runs_export()

    # Detail before index: the index records which runs have re-scored field
    # detail, and learns that from the files this step writes.
    print("\n=== Step 3/9: Compare detail (re-scores runs lacking field detail) ===")
    generate_compare_detail()

    print("\n=== Step 4/9: Compare index ===")
    generate_compare_index()

    print("\n=== Step 5/9: Multi-select data ===")
    generate_multi_select_data()

    print("\n=== Step 6/9: Visualizations ===")
    generate_visualizations()

    print("\n=== Step 7/9: Vars ===")
    generate_vars()

    print("\n=== Step 8/9: Static data (pricing, model aliases) ===")
    copy_static_data()

    # Last: it copies the benchmark export written in step 1.
    print("\n=== Step 9/9: Site data (everything the website's widgets read) ===")
    generate_site_data()

    print("\nAll exports complete.")


if __name__ == "__main__":
    generate_all()
