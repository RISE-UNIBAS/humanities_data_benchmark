"""Run all NDR export generators in the correct order.

Usage (from project root):
    python -m scripts.ndr_export.generate_all
"""

from scripts.ndr_export.generate_benchmark_export import generate_benchmark_export
from scripts.ndr_export.generate_test_runs_export import generate_test_runs_export
from scripts.ndr_export.generate_multi_select_data import generate_multi_select_data
from scripts.ndr_export.generate_visualizations import generate_visualizations
from scripts.ndr_export.generate_vars import generate_vars
from scripts.ndr_export.copy_static_data import copy_static_data


def generate_all():
    print("=== Step 1/6: Benchmark export ===")
    generate_benchmark_export()

    print("\n=== Step 2/6: Test runs export ===")
    generate_test_runs_export()

    print("\n=== Step 3/6: Multi-select data ===")
    generate_multi_select_data()

    print("\n=== Step 4/6: Visualizations ===")
    generate_visualizations()

    print("\n=== Step 5/6: Vars ===")
    generate_vars()

    print("\n=== Step 6/6: Static data (pricing, model aliases) ===")
    copy_static_data()

    print("\nAll exports complete.")


if __name__ == "__main__":
    generate_all()
