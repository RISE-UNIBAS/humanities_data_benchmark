 # Project: Humanities Data Benchmark

## Overview
A benchmark suite for evaluating LLM performance on humanities digitisation tasks (OCR, transcription, structured data extraction). Models are tested across multiple benchmarks, results are scored and stored in `results/`, and pricing data is tracked in `pricing.json`.

## Key Files
- `benchmarks/benchmarks_tests.csv` — all test definitions (id, benchmark, provider, model, dataclass, temperature, role, prompt_file, rules, legacy_test)
- `collected_results/` — CSV exports used for the web frontend (models.csv, benchmarks.csv, etc.)
- `results/` — actual run results, organised by date and test ID
- `scripts/update_pricing.py` — semi-automated pricing scraper
- `CHANGELOG.md` — keep up to date with all changes

## Conventions

### benchmarks_tests.csv
- Non-legacy models have `legacy_test=false`; deprecated models are marked `legacy_test=true`
- When adding a new model, mirror the full set of benchmarks from the most recent equivalent model of the same provider
- Test IDs are sequential (T0001, T0002, …); always append after the last existing ID
- When asked for test IDs, return them as a Python list: `["Txxx", ...]`

### Providers
- `anthropic`, `openai`, `genai`, `mistral`, `cohere`, `openrouter`, `scicore`, `deepseek`, `x-ai`, `alibaba`, `huggingface`
- Each provider has a scraper and per-model URL dict in `scripts/update_pricing.py`
- Adding a provider means updating three allowlists: the provider list in `scripts/benchmark_base.py` (`is_runnable`), `API_PROVIDERS` in `tests/integrity/test_config_integrity.py`, and the `provider_map` in the `generic-llm-api-client` dependency
- API keys are read from `<PROVIDER>_API_KEY` in `.env` (provider name uppercased)
- Alibaba models use `base_url` in the rules column to point to the Alibaba API endpoint
- Hugging Face models are recorded as `<repo_id>:<provider>` (e.g. `MiniMaxAI/MiniMax-M3:deepinfra`), pinning the downstream inference provider. Pick the cheapest route whose `supports_structured_output` is true in `GET https://router.huggingface.co/v1/models`. The pinned name is the key everywhere: CSV, README, `pricing.json`, `HUGGINGFACE_MODEL_URLS`, `model_aliases.json`. Without a pin the router chooses per request and nothing in the response identifies who served it, so price and result-file model id both become unreproducible — see `dev/HUGGINGFACE_FINDINGS.md` §8

### CHANGELOG.md
- Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- Integrate new entries into existing `## Unreleased` bullet points rather than adding separate bullets

### README.md
- Models table is at the bottom; add new models in provider order, remove "Latest" qualifiers when superseded

## Adding a New Model
When asked to add a new model, always do all of the following in order:
1. **`benchmarks/benchmarks_tests.csv`** — add tests mirroring the full benchmark set of the most recent equivalent model for that provider (`legacy_test=false`). Each model gets 15 tests (one per benchmark across the 12 benchmarks, with business_letters×3 and company_lists×2 variants). The rules column must be wrapped in outer `"` quotes for CSV escaping: `"{""key"": ""value""}"`.
2. **`README.md`** — add the model to the models table in the correct provider section
3. **`scripts/update_pricing.py`** — add the model to the provider's `*_MODEL_URLS` dict; if the provider has no scraper yet, add one
4. **`scripts/data/pricing.json`** — add pricing entry with `input_price` ($/M tokens), `output_price` ($/M tokens), `source_url`, and `added` (date string). The `source_url` must be a Wayback Machine archive URL (`https://web.archive.org/web/<timestamp>/<original-url>`); archive the provider page on archive.org before adding the entry, and never use the bare provider URL. Whenever `pricing.json` is updated, also bump the top-level `metadata` block: increment `version` and set `last_updated` to today's date.
5. **`CHANGELOG.md`** — integrate into the existing `## Unreleased` Added bullet (update model count and test ID range)
6. **`scripts/run_benchmarks_<model>.py`** — create a copy of `run_benchmarks.py` with the new model's test IDs in the `__main__` block (one file per model, used to run benchmarks in parallel)

## Reports
When asked for a report on today's (or a given date's) results, run:
```
python scripts/generate_date_report.py --date <YYYY-MM-DD> --format html
```
Then reply with the path to the generated file (`reports/<date>_report.html`) as a clickable link — nothing else is needed.

## Preferences
- Keep responses concise
- Don't add docstrings, comments, or type annotations to code that wasn't changed
- When checking which models are missing, compare against `benchmarks_tests.csv` (not `models.csv`)
