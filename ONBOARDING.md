# Onboarding: RISE Humanities Data Benchmark

A short orientation for new contributors. Read this once, then read one benchmark folder
end-to-end — that combination is enough to start working.

## 1. What this repository is

A benchmark suite that measures how well large language models do *digital humanities*
work: reading historical documents — often handwritten, in Fraktur, tabular, and
multilingual — and turning them into structured data. It is developed at the University
of Basel by RISE (Research and Infrastructure Support).

Published results live at <https://rise-services.rise.unibas.ch/benchmarks/>. The
framework, the datasets, and every result ever produced are all in this repository.

The question the project answers is not "which model is smartest". It is: *which model
should a humanities researcher use for this specific kind of source, and what will it
cost?* Everything below follows from that.

Background reading:

- Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to
  Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities
  Data*, 12(1), 38. <https://doi.org/10.5334/johd.470>
- Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data
  Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks.
  *Journal of Open Humanities Data*, 12(1), 24. <https://doi.org/10.5334/johd.481>

## 2. Four terms you need

| Term | Meaning |
|---|---|
| **Benchmark** | One task plus its dataset. A directory under `benchmarks/`, e.g. `personnel_cards/`. Twelve real ones plus two smoke-test ones. |
| **Test** | One row in `benchmarks/benchmarks_tests.csv`: benchmark × provider × model × prompt × temperature. Roughly 1740 rows, IDs `T0001`…`T1764`. |
| **Ground truth** | The human-verified correct answer. One JSON file per input file. |
| **Score** | The output of the scoring function of that benchmark (`fuzzy`, `f1_micro`, `cer`, …). Each benchmark defines its own metric. |

Two more that come up: an **adhoc test** is a throwaway run configured on the fly
(results go to `test_runs/`, which is gitignored), and a **dataclass** is the Pydantic
model that defines the structured output the model is asked to produce.

## 3. The twelve benchmarks

`bibliographic_data`, `blacklist_cards`, `book_advert_xml`, `business_letters`,
`company_lists`, `duty_rosters`, `fraktur_adverts`, `general_meeting_minutes`,
`library_cards`, `magazine_pages`, `medieval_manuscripts`, `personnel_cards`
(plus `test_benchmark` and `test_benchmark2` for system validation).

Each is named after its **source**, not its task — `personnel_cards`, not
`entity_extraction`. The name cannot be changed later.

## 4. Anatomy of a benchmark folder

```
benchmarks/personnel_cards/
  images/          # inputs sent to the model (or texts/ for text-only benchmarks)
  ground_truths/   # one JSON per input, matched by basename
  prompts/         # prompt.txt and any variants
  dataclass.py     # Pydantic schema for structured output
  benchmark.py     # score_request_answer() + score_benchmark()
  meta.json        # title, description, tags, contributors, ranking metric
  README.md        # documentation of the source and the task
```

Filename pairing is the central convention: `page_2.jpg` → `page_2.json`. The basename is
the "object"; all files sharing a basename are sent to the model together.

`benchmark.py` implements exactly two mandatory methods:

```python
def score_request_answer(self, object_name, response, ground_truth):
    return {"fuzzy": calculated_score}   # score one object

def score_benchmark(self, all_scores):
    return {"fuzzy": total / len(all_scores)}   # aggregate the run
```

Further behaviour (image resizing, `None`-stripping, prompt interpolation, skipping
objects) is configured by overriding methods inherited from `Benchmark` in
`scripts/benchmark_base.py`.

## 5. How a run works

1. `scripts/run_single_test.py --test_id T0001` looks the ID up in
   `benchmarks/benchmarks_tests.csv`.
2. For each object, it builds a request — role description, prompt, image or text — and
   calls the provider API, requesting output that conforms to the Pydantic dataclass.
3. The response is scored against the ground truth by `score_request_answer()`.
4. Everything is written to `results/<YYYY-MM-DD>/<test_id>/`:
   - `request_<test_id>_<object>.json` — model text, parsed output, `usage`, `duration`,
     `timestamp`, `score`, raw response
   - `scoring.json` — aggregate score plus a cost summary in tokens and USD
5. `collected_results/*.csv` and `*.json` are the aggregated exports that feed the web
   frontend.

A test that already has results for the current day is skipped; pass `--regenerate` to
overwrite.

## 6. Getting set up

```bash
pip install -r requirements.txt        # Python 3.12 or newer
```

Create a `.env` in the repository root. Key names are derived from the provider name in
the CSV, uppercased: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GENAI_API_KEY`,
`MISTRAL_API_KEY`, `COHERE_API_KEY`, `OPENROUTER_API_KEY`, `SCICORE_API_KEY`,
`DEEPSEEK_API_KEY`, `ALIBABA_API_KEY`, `HUGGINGFACE_API_KEY`, `X-AI_API_KEY` (note the
hyphen, which follows from the provider name `x-ai`). Local providers need no key.

Then verify the installation on the one-image smoke test:

```bash
python scripts/run_single_test.py --test_id T0001        # needs OPENAI_API_KEY
python scripts/run_single_test.py --test_id T0193        # needs GENAI_API_KEY
python scripts/run_single_test.py                        # interactive test picker
```

Render what you just produced:

```bash
python scripts/generate_test_report.py results/<date>/T0001 --open
python scripts/generate_date_report.py --date <YYYY-MM-DD> --format html
```

## 7. Providers

`anthropic`, `openai`, `genai` (Google), `mistral`, `cohere`, `openrouter`, `scicore`
(University of Basel HPC), `deepseek`, `x-ai`, `alibaba`, `huggingface`.

Two notes worth internalising:

- **Hugging Face models are pinned** as `<repo_id>:<provider>`, e.g.
  `MiniMaxAI/MiniMax-M3:deepinfra`. Without the pin the router picks an inference provider
  per request and nothing in the response says who served it, so both the price and the
  model id in the result file become unreproducible.
- There are also four **local** vision backends registered in `local/__init__.py`
  (`contour_local`, `doclayout_yolo_local`, `grounding_dino_local`, `sam3_local`). They are
  selected through the `provider` column like any other provider and need no API key.

## 8. Things newcomers underestimate

**Cost and time are first-class metrics.** Every run computes USD from token counts
against `scripts/data/pricing.json`, which is date-versioned. The `source_url` of each
entry must be a Wayback Machine snapshot, so a run from 2025 is priced at 2025 prices and
the price can be verified years later. Never put a bare provider URL there.

**Model churn is the main maintenance burden.** New models arrive constantly, and adding
one is a fixed six-step procedure documented in `CLAUDE.md`: the test CSV, `README.md`, the
scraper in `scripts/update_pricing.py`, `scripts/data/pricing.json` (plus a metadata
version bump), `CHANGELOG.md`, and a `scripts/run_benchmarks_<model>.py` runner. It is easy
to half-complete; follow it in order.

**Superseded models are marked `legacy_test=true`, never deleted.** They are skipped by the
runners, but their historical results must stay reproducible and explicable.

**Scoring functions encode humanities judgment calls** about what counts as a correct
transcription or a correct extraction. Changing one silently invalidates every earlier
comparison for that benchmark. Treat such a change as a discussion, not a refactor.

**Ground truth is expensive.** It is created and checked by domain experts. Do not "fix" a
ground truth file because a model disagreed with it.

## 9. Guard rails

`tests/integrity/` checks configuration consistency — provider allowlists, the test CSV,
client capability claims. Run it before committing changes to
`benchmarks/benchmarks_tests.csv` or to provider handling:

```bash
python -m pytest tests/integrity
```

Adding a provider means updating three allowlists: `is_runnable` in
`scripts/benchmark_base.py`, `API_PROVIDERS` in
`tests/integrity/test_config_integrity.py`, and the `provider_map` in the
`generic-llm-api-client` dependency.

`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and is kept
current for every change.

## 10. Adding a new benchmark

```bash
python scripts/create_benchmark.py
```

The CLI scaffolds the directory, `meta.json`, the README, a default prompt, and stubs for
`benchmark.py` and `dataclass.py`. Afterwards you add the inputs and ground truths,
implement the two scoring methods, and fill in the Pydantic schema.

Before proposing a benchmark for inclusion: the data must be openly licensed and free of
copyrighted or sensitive material, ideally under 50 MB; ground truths must be manually
checked; the prompt must not over-specify its way to the right answers; and the benchmark
should fill a real gap in task, domain, or corpus. See `CONTRIBUTING.md` and section 3 of
`README.md` for the full checklist and the pull request process.

## 11. A first week that works

1. Run `T0001`, then render its report.
2. Read `benchmarks/personnel_cards/` completely — `meta.json`, the prompt, the dataclass,
   `benchmark.py` — and trace one image from `images/` through to a line in `scoring.json`.
3. Open the same test in the public dashboard and find your local numbers in it.
4. Read `scripts/benchmark_base.py` to see what the base class does for you.

Once that clicks, the remaining ~1740 tests are the same thing repeated.
