"""Run all NDR export generators in the correct order.

Usage (from project root):
    python -m scripts.ndr_export.generate_all
"""

from scripts.ndr_export.generate_benchmark_export import generate_benchmark_export
from scripts.ndr_export.generate_test_runs_export import generate_test_runs_export
from scripts.ndr_export.generate_compare_index import generate_compare_index
from scripts.ndr_export.generate_multi_select_data import generate_multi_select_data
from scripts.ndr_export.generate_visualizations import generate_visualizations
from scripts.ndr_export.generate_vars import generate_vars
from scripts.ndr_export.copy_static_data import copy_static_data


def generate_all():
    print("=== Step 1/7: Benchmark export ===")
    generate_benchmark_export()

    print("\n=== Step 2/7: Test runs export ===")
    generate_test_runs_export()

    print("\n=== Step 3/7: Compare index ===")
    generate_compare_index()

    print("\n=== Step 4/7: Multi-select data ===")
    generate_multi_select_data()

    print("\n=== Step 5/7: Visualizations ===")
    generate_visualizations()

    print("\n=== Step 6/7: Vars ===")
    generate_vars()

    print("\n=== Step 7/7: Static data (pricing, model aliases) ===")
    copy_static_data()

    print("\nAll exports complete.")


if __name__ == "__main__":
    generate_all()
