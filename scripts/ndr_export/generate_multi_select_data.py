"""This module generates csv and json data files to be used in NDR Core for the creation
 of multi-select search fields."""

import csv
import json
import os

from scripts.ndr_export import CONTRIBUTORS_PATH, EXPORT_PATH
from scripts.ndr_export.meta_utils import get_benchmarks, get_meta, load_json
from scripts.ndr_export.test_utils import get_all_tests

def get_mentioned_contributors():
    """Returns a unique list of contributors mentioned in the meta.json files."""
    benchmarks = get_benchmarks()
    contributors = set()

    for benchmark in benchmarks:
        meta = get_meta(benchmark)
        contributor_data = meta.get("contributors", [])

        for role_group in contributor_data:
            for contributor in role_group.get("contributors", []):
                contributors.add(contributor)

    return sorted(list(contributors))

def get_mentioned_tags():
    """Returns a unique list of tags mentioned in the meta.json files."""
    benchmarks = get_benchmarks()
    tags = set()

    for benchmark in benchmarks:
        meta = get_meta(benchmark)
        benchmark_tags = meta.get("tags", [])
        tags.update(benchmark_tags)

    return sorted(list(tags))

def get_mentioned_providers():
    """Returns a unique list of providers mentioned in test configurations."""
    all_tests = get_all_tests()
    providers = set()

    for test in all_tests:
        provider = test.get("provider")
        if provider:
            providers.add(provider)

    return sorted(list(providers))

def get_mentioned_models():
    """Returns a unique list of models mentioned in test configurations."""
    all_tests = get_all_tests()
    models = set()

    for test in all_tests:
        model = test.get("model")
        if model:
            models.add(model)

    return sorted(list(models))

def load_contributors_database():
    """Load the contributors database from contributors.json."""
    if not CONTRIBUTORS_PATH.exists():
        print(f"Warning: Contributors database not found at {CONTRIBUTORS_PATH}")
        return {}

    return load_json(CONTRIBUTORS_PATH) or {}

def get_contributor_ndr_csv():
    """Generate NDR CSV file for contributors.

    Returns a list of dicts with: key, value, is_printable, is_searchable, info
    """
    mentioned_contributors = get_mentioned_contributors()
    contributors_db = load_contributors_database()

    csv_data = []

    for contributor_key in mentioned_contributors:
        contributor_info = contributors_db.get(contributor_key, {})
        display_name = contributor_info.get("display_name", contributor_key)
        orcid = contributor_info.get("orcid", "")
        github = contributor_info.get("github", "")

        info_parts = []
        if orcid:
            info_parts.append(f"ORCID: {orcid}")
        if github:
            info_parts.append(f"GitHub: {github}")

        csv_data.append({
            "key": contributor_key,
            "value": display_name,
            "is_printable": True,
            "is_searchable": True,
            "info": ", ".join(info_parts)
        })

    return csv_data

def get_tag_ndr_csv():
    """Generate NDR CSV file for tags.

    Returns a list of dicts with: key, value, is_printable, is_searchable, info
    """
    tags = get_mentioned_tags()

    csv_data = []

    for tag in tags:
        # Convert tag key to display name (replace hyphens with spaces, capitalize)
        display_name = tag.replace("-", " ").title()

        csv_data.append({
            "key": tag,
            "value": display_name,
            "is_printable": True,
            "is_searchable": True,
            "info": ""
        })

    return csv_data

def get_provider_ndr_csv():
    """Generate NDR CSV file for providers.

    Returns a list of dicts with: key, value, is_printable, is_searchable, info
    """
    providers = get_mentioned_providers()

    # Map provider keys to display names
    provider_names = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "cohere": "Cohere",
        "mistral": "Mistral AI",
        "meta": "Meta",
        "huggingface": "Hugging Face"
    }

    csv_data = []

    for provider in providers:
        display_name = provider_names.get(provider, provider.capitalize())

        csv_data.append({
            "key": provider,
            "value": display_name,
            "is_printable": True,
            "is_searchable": True,
            "info": ""
        })

    return csv_data

def get_model_ndr_csv():
    """Generate NDR CSV file for models.

    Returns a list of dicts with: key, value, is_printable, is_searchable, info
    """
    models = get_mentioned_models()

    csv_data = []

    for model in models:
        # Use model name as-is for both key and value
        csv_data.append({
            "key": model,
            "value": model,
            "is_printable": True,
            "is_searchable": True,
            "info": ""
        })

    return csv_data

def get_benchmark_ndr_csv():
    """Generate NDR CSV file for benchmarks.

    Returns a list of dicts with: key, value, is_printable, is_searchable, info
    Benchmarks with display: false are marked as is_searchable: false
    """
    benchmarks = get_benchmarks()

    csv_data = []

    for benchmark in benchmarks:
        meta = get_meta(benchmark)

        # Get display name from meta or generate from key
        display_name = meta.get("title_short") or meta.get("title") or benchmark.replace("_", " ").title()

        # Check if benchmark should be hidden
        is_searchable = meta.get("display", True)

        csv_data.append({
            "key": benchmark,
            "value": display_name,
            "is_printable": True,
            "is_searchable": is_searchable,
            "info": ""
        })

    return csv_data

def write_csv(data, filename):
    """Write data to a CSV file."""
    os.makedirs(EXPORT_PATH, exist_ok=True)
    filepath = EXPORT_PATH / filename

    if not data:
        print(f"No data to write to {filename}")
        return

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["key", "value", "is_printable", "is_searchable", "info"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Wrote {len(data)} rows to {filepath}")

def write_json(data, filename):
    """Write data to a JSON file."""
    filepath = EXPORT_PATH / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(data)} items to {filepath}")

def generate_multi_select_data():
    """Generate all multi-select data files (CSV and JSON)."""

    # Ensure export directory exists
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)

    # Generate contributors data
    contributors_data = get_contributor_ndr_csv()
    write_csv(contributors_data, "contributors.csv")
    write_json(contributors_data, "contributors.json")

    # Generate tags data
    tags_data = get_tag_ndr_csv()
    write_csv(tags_data, "tags.csv")
    write_json(tags_data, "tags.json")

    # Generate providers data
    providers_data = get_provider_ndr_csv()
    write_csv(providers_data, "providers.csv")
    write_json(providers_data, "providers.json")

    # Generate models data
    models_data = get_model_ndr_csv()
    write_csv(models_data, "models.csv")
    write_json(models_data, "models.json")

    # Generate benchmarks data
    benchmarks_data = get_benchmark_ndr_csv()
    write_csv(benchmarks_data, "benchmarks.csv")
    write_json(benchmarks_data, "benchmarks.json")

    print("\nMulti-select data generation complete!")

if __name__ == "__main__":
    generate_multi_select_data()
