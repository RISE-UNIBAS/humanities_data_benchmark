import json
import os
from datetime import date

from scripts.ndr_export import RESULTS_PATH, EXPORT_PATH, BENCHMARKS_PATH
from scripts.ndr_export.meta_utils import get_benchmarks, get_meta
from scripts.ndr_export.test_utils import get_all_tests


# ---------------------------------------------------------------------------
# Carbon / energy footprint estimation constants
#
# Model:  energy_Wh = alpha_Wh * n_requests
#                   + beta_in_Wh_per_token  * input_tokens
#                   + beta_out_Wh_per_token * output_tokens
#
# These are ROUGH ESTIMATES based on published literature, not measurements.
# Inference energy scales approximately linearly with token counts; alpha
# captures fixed per-call overhead (network I/O, scheduling, etc.).
#
# Sources
# -------
# [1] Luccioni et al. (2023) "Power Hungry Processing: Watts Driving the
#     Cost of AI Deployment?" https://arxiv.org/abs/2311.16863
#     → Measured 0.001–0.05 kWh per 1000 tokens for large-model inference,
#       with output (decode) tokens costing ~5–10× more than input (prefill).
# [2] Tomlinson et al. (2024) "The Carbon Footprint of Using LLMs"
#     https://arxiv.org/abs/2404.14329
#     → Estimates ~0.001–0.003 kWh per 1000 tokens for GPT-4-class APIs.
# [3] IEA (2023) "Electricity 2024" – global average grid carbon intensity
#     ≈ 0.4 kg CO₂e/kWh; renewable-heavy datacenters can be ≈ 0.1 kg CO₂e/kWh.
#     https://www.iea.org/reports/electricity-2024
# [4] EPA (2023) "Greenhouse Gas Emissions from a Typical Passenger Vehicle"
#     ≈ 248.55 g CO₂e per km for an average passenger car.
#     https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle
# ---------------------------------------------------------------------------
_CARBON = {
    # Fixed energy overhead per inference API call (Wh)
    "alpha_Wh": {"low": 0.001, "central": 0.01, "high": 0.05},
    # Energy per input (prefill) token (Wh)  [1][2]
    "beta_in_Wh_per_token": {"low": 0.0001, "central": 0.0005, "high": 0.002},
    # Energy per output (decode) token (Wh) – decode is ~5–10× costlier  [1]
    "beta_out_Wh_per_token": {"low": 0.0005, "central": 0.002, "high": 0.01},
    # Grid carbon intensity (kg CO₂e per kWh)  [3]
    "grid_kg_co2e_per_kwh": {"low": 0.1, "central": 0.4, "high": 0.8},
    # Passenger vehicle emission factor (g CO₂e per km)  [4]
    "car_g_co2e_per_km": 248.55,
}


def _estimate_footprint(n_requests, input_tokens, output_tokens):
    """Return low/central/high energy, CO₂e, and car-km estimates."""
    p = _CARBON
    result = {}
    for level in ("low", "central", "high"):
        energy_wh = (
            p["alpha_Wh"][level] * n_requests
            + p["beta_in_Wh_per_token"][level] * input_tokens
            + p["beta_out_Wh_per_token"][level] * output_tokens
        )
        co2e_kg = (energy_wh / 1000) * p["grid_kg_co2e_per_kwh"][level]
        car_km = (co2e_kg * 1000) / p["car_g_co2e_per_km"]
        result[level] = {
            "energy_wh": round(energy_wh, 1),
            "co2e_kg": round(co2e_kg, 3),
            "car_km": round(car_km, 2),
        }
    return result


def generate_vars():
    """Generate vars.json with summary statistics for the NDR website."""

    benchmarks = get_benchmarks()
    test_datasets = [b for b in benchmarks if "test" in get_meta(b).get("tags", {}).get("internal", [])]
    real_datasets = [b for b in benchmarks if b not in test_datasets]
    all_tests = get_all_tests()
    tests_by_id = {t["id"]: t for t in all_tests}

    number_of_runs = 0
    number_of_llm_requests = 0
    first_test_run_date = None
    last_test_run_date = None
    total_cost_usd = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    total_duration_seconds = 0.0
    used_providers = set()
    used_models = set()

    if RESULTS_PATH.exists():
        for date_folder in sorted(RESULTS_PATH.iterdir()):
            if not date_folder.is_dir():
                continue
            date_str = date_folder.name
            has_runs = False

            for test_folder in date_folder.iterdir():
                if not test_folder.is_dir():
                    continue
                has_runs = True
                number_of_runs += 1

                # Count individual LLM request files and sum duration
                for req_file in test_folder.glob("request_*.json"):
                    number_of_llm_requests += 1
                    try:
                        with req_file.open("r", encoding="utf-8") as f:
                            req = json.load(f)
                        total_duration_seconds += req.get("duration", 0) or 0
                    except (json.JSONDecodeError, IOError):
                        pass

                # Sum cost and token counts from scoring.json cost_summary
                scoring_path = test_folder / "scoring.json"
                if scoring_path.exists():
                    try:
                        with scoring_path.open("r", encoding="utf-8") as f:
                            scoring = json.load(f)
                        cost = scoring.get("cost_summary") or {}
                        total_cost_usd += cost.get("total_cost_usd", 0) or 0
                        total_input_tokens += cost.get("total_input_tokens", 0) or 0
                        total_output_tokens += cost.get("total_output_tokens", 0) or 0
                    except (json.JSONDecodeError, IOError):
                        pass

                # Collect providers/models from test configurations
                test_config = tests_by_id.get(test_folder.name)
                if test_config:
                    if test_config.get("provider"):
                        used_providers.add(test_config["provider"])
                    if test_config.get("model"):
                        used_models.add(test_config["model"])

            if has_runs:
                if first_test_run_date is None or date_str < first_test_run_date:
                    first_test_run_date = date_str
                if last_test_run_date is None or date_str > last_test_run_date:
                    last_test_run_date = date_str

    # Count input files (images and texts) across all benchmark datasets
    number_of_input_files = 0
    for benchmark in real_datasets:
        for subdir in ("images", "texts"):
            subdir_path = BENCHMARKS_PATH / benchmark / subdir
            if subdir_path.exists():
                number_of_input_files += sum(1 for f in subdir_path.iterdir() if f.is_file())

    # Estimated carbon / energy footprint (low / central / high ranges)
    footprint = _estimate_footprint(number_of_llm_requests, total_input_tokens, total_output_tokens)

    vars_data = {
        "number_of_datasets": str(len(real_datasets)),
        "number_of_test_datasets": str(len(test_datasets)),
        "number_of_tests": str(len(all_tests)),
        "number_of_runs": str(number_of_runs),
        "number_of_llm_requests": str(number_of_llm_requests),
        "number_of_input_files": str(number_of_input_files),
        "number_of_providers": str(len(used_providers)),
        "number_of_models": str(len(used_models)),
        "total_input_tokens": str(total_input_tokens),
        "total_output_tokens": str(total_output_tokens),
        "total_cost_usd": f"{total_cost_usd:.2f}",
        "total_duration_seconds": str(round(total_duration_seconds)),
        "framework_start_date": first_test_run_date or "",
        "last_test_run": last_test_run_date or "",
        "last_page_update": date.today().isoformat(),
        # Energy / carbon estimates — ROUGH ESTIMATES, not measurements
        "estimated_energy_wh_low": str(footprint["low"]["energy_wh"]),
        "estimated_energy_wh_central": str(footprint["central"]["energy_wh"]),
        "estimated_energy_wh_high": str(footprint["high"]["energy_wh"]),
        "estimated_co2e_kg_low": str(footprint["low"]["co2e_kg"]),
        "estimated_co2e_kg_central": str(footprint["central"]["co2e_kg"]),
        "estimated_co2e_kg_high": str(footprint["high"]["co2e_kg"]),
        "estimated_car_km_low": str(footprint["low"]["car_km"]),
        "estimated_car_km_central": str(footprint["central"]["car_km"]),
        "estimated_car_km_high": str(footprint["high"]["car_km"]),
    }

    os.makedirs(EXPORT_PATH, exist_ok=True)
    export_path = EXPORT_PATH / "vars.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(vars_data, f, indent=2, ensure_ascii=False)

    print(f"Exported vars to {export_path}")


if __name__ == "__main__":
    generate_vars()