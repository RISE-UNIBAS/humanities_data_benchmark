# RISE Humanities Data Benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16941752.svg)](https://doi.org/10.5281/zenodo.16941752)

This repository contains benchmark datasets (images and text files), prompts, ground truths, and evaluation
scripts for assessing the performance of large language models (LLMs) on humanities-related tasks. The suite is
designed as a resource for researchers and practitioners interested in systematically evaluating how well various
LLMs perform on digital humanities (DH) tasks involving visual and text-like materials.

Tasks covered include transcription, structured information extraction, and document layout analysis, each scored
against ground truths and recorded together with its cost and runtime.

**[Explore the results dashboard](https://rise-services.rise.unibas.ch/benchmarks/)**

[Why benchmark?](#why-benchmark) · [Results](#results) ·
[Available benchmarks](#available-benchmarks) · [Quick start](#quick-start) ·
[Methodology](#methodology) · [Contributing](#contributing) ·
[Citation and licensing](#citation-and-licensing) · [Contributors](#contributors)

## Why benchmark?

Benchmarking is the process of systematically evaluating and ranking various models for specific tasks using
well-defined ground truths and metrics. For humanities research, benchmarking provides:

- **Evidence-based decision-making** about which model(s) to use for which humanities-specific task(s)
- **Quantifiable comparisons** between different AI models on humanities data, including cost efficiency analysis
- **Standardized evaluation** of model performance on tasks like document analysis, transcription, and metadata extraction

This benchmark suite focuses on tasks essential to digital humanities work with visual and text-like materials,
helping researchers make informed choices about which AI systems best suit their specific research needs.

## Results

All scored runs are published on the
**[results dashboard](https://rise-services.rise.unibas.ch/benchmarks/)**, which is the primary way
to read this benchmark:

- **[Leaderboard](https://rise-services.rise.unibas.ch/benchmarks/p/leaderboard/)** — aggregated
  results showing which providers and models perform best on which kinds of data.
- **[Datasets](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/)** — browse the
  benchmarks and the results recorded for each of them.
- **[Test runs](https://rise-services.rise.unibas.ch/benchmarks/p/testruns/)** — search individual
  test runs and compare model output with the ground truths.

Every score shown there traces back to a stored response in this repository, under
`results/<date>/<test_id>/`, alongside the aggregated `scoring.json` for the run.

## Available benchmarks

This benchmark suite currently includes the following benchmarks for evaluating LLM performance on humanities tasks:

| Benchmark | Description |
|-----------|-------------|
| **[Bibliographic Data](benchmarks/bibliographic_data/)** | Extract bibliographic information (publication details, authors, dates, metadata) from historical documents |
| **[Blacklist Cards](benchmarks/blacklist_cards/)** | Extract and structure information from historical blacklist cards |
| **[Book Advert XML](benchmarks/book_advert_xml/)** | Correct malformed XML from 18th century book advertisements |
| **[Business Letters](benchmarks/business_letters/)** | Extract structured metadata (names, organizations, dates, locations) from 20th century Swiss historical correspondence |
| **[Company Lists](benchmarks/company_lists/)** | Extract structured company information from historical business listings and directories |
| **[Duty Rosters](benchmarks/duty_rosters/)** | Extract structured schedule data (shift types, half-day splits, unit assignments, staff metadata) from Swiss nursing staff duty rosters |
| **[Fraktur Adverts](benchmarks/fraktur_adverts/)** | Recognize and transcribe historical German Fraktur script (16th-20th centuries) |
| **[General Meeting Minutes](benchmarks/general_meeting_minutes/)** | Extract structured data from general meeting minutes of historical companies |
| **[Library Cards](benchmarks/library_cards/)** | Catalog card analysis and information extraction from historical library catalog systems |
| **[Magazine Pages](benchmarks/magazine_pages/)** | Detect and locate advertisements on historical magazine pages using bounding boxes |
| **[Medieval Manuscripts](benchmarks/medieval_manuscripts/)** | Page segmentation and handwritten text extraction from 15th century medieval German manuscripts |
| **[Personnel Cards](benchmarks/personnel_cards/)** | Extract structured employment data (position, location, salary, dates) from 20th century Swiss personnel card tables |

The [test_benchmark](benchmarks/test_benchmark/) and [test_benchmark2](benchmarks/test_benchmark2/) fixtures validate the framework itself.

## Quick start

To inspect existing comparisons, open the [results dashboard](https://rise-services.rise.unibas.ch/benchmarks/).
To run a new evaluation, follow the steps below. Python 3.12 or newer is recommended.

### Install

Clone the repository and create a virtual environment.
To contribute a benchmark, fork the repository first and clone your fork instead:

```console
git clone https://github.com/RISE-UNIBAS/humanities_data_benchmark.git
cd humanities_data_benchmark
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Or in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```console
python -m pip install -r requirements.txt
```

### Configure a provider and run a test

Create a `.env` file in the repository root with an OpenAI API key:

```dotenv
OPENAI_API_KEY=<your_openai_api_key>
```

Run the small validation fixture from the repository root. This sends one image to the provider and incurs API charges.

```console
python scripts/run_single_test.py --test_id T0001
```

Results are saved to `results/YYYY-MM-DD/T0001`, using the date of the run.
For Google instead, set `GENAI_API_KEY` and run the same command with `--test_id T0193`.
Configurations are stored in [benchmarks/benchmarks_tests.csv](benchmarks/benchmarks_tests.csv).

### Inspect the output

Generate a standalone HTML report, replacing `YYYY-MM-DD` with the date of your run:

```console
python scripts/generate_test_report.py results/YYYY-MM-DD/T0001
```

Open `reports/T0001_report.html` in a browser to inspect the results.

<details>
<summary>Additional provider keys</summary>

Add the keys for the providers you use to your root `.env` file.

```dotenv
OPENAI_API_KEY=<your_openai_api_key>
GENAI_API_KEY=<your_genai_api_key>
ANTHROPIC_API_KEY=<your_anthropic_api_key>
COHERE_API_KEY=<your_cohere_api_key>
MISTRAL_API_KEY=<your_mistral_api_key>
OPENROUTER_API_KEY=<your_openrouter_api_key>
SCICORE_API_KEY=<your_scicore_api_key>
DEEPSEEK_API_KEY=<your_deepseek_api_key>
ALIBABA_API_KEY=<your_alibaba_api_key>
X-AI_API_KEY=<your_xai_api_key>
HUGGINGFACE_API_KEY=<your_huggingface_api_key>
```

The key name is derived from the provider name in `benchmarks/benchmarks_tests.csv` as `<PROVIDER>_API_KEY` (uppercased). Note the hyphen in `X-AI_API_KEY`, which follows from the provider name `x-ai`. Local providers need no API key; see the local backend reference below.

</details>

<details>
<summary>Configured runs, ad hoc tests, and report options</summary>

**Configured runs**

The `T0001` example runs `test_benchmark` (one image, one request) and saves results to `results/YYYY-MM-DD/T0001`. Existing results are reused on the same day. To regenerate them, run:

```
python scripts/run_single_test.py --test_id T0001 --regenerate
```

Run the script without parameters to search for and select a configured test interactively.

Tests marked `legacy_test=true` in `benchmarks/benchmarks_tests.csv` are deprecated and are skipped by both `run_single_test.py` and `run_benchmarks.py`; they are kept only for historical results and cannot be run by ID.

**Ad hoc tests**

Use an ad hoc test to check a new benchmark or experiment with a temporary configuration.
Run the following command and select from the options to create an on-the-fly configuration to test.

```
python scripts/run_single_test.py --adhoc
```

The results are saved to `test_runs/` directory instead of `results/` which you can easily delete and is ignored by the repository.
Ad hoc tests use the ID format `ADHOC_YYYYMMDD_HHMMSS`.

**HTML reports**

To render a single test run as a standalone HTML report:

```
python scripts/generate_test_report.py results/YYYY-MM-DD/T0001
```

The report is written to `reports/<test_id>_report.html` by default; use `-o` to choose another path, `--include-raw`
to embed the raw API responses, `--no-images` to omit the input images, and `--open` to open the result in a browser.

To render all test runs of a given day into one overview report:

```
python scripts/generate_date_report.py --date YYYY-MM-DD
```

</details>

<details>
<summary>Local model backends</summary>

Local backends are registered in `local/__init__.py` and are used by putting their
provider name into the `provider` column of `benchmarks/benchmarks_tests.csv`; no API key is required.

| Provider | Backend | Requirements |
|----------|---------|--------------|
| `contour_local` | OpenCV contour detection | any OS, no GPU needed |
| `doclayout_yolo_local` | DocLayout-YOLO | Windows / Linux, NVIDIA GPU |
| `grounding_dino_local` | Grounding DINO | Windows / Linux, NVIDIA GPU |
| `sam3_local` | SAM 3 | macOS / Apple Silicon |

To add a new backend, create `local/backends/<name>.py` with a class extending `LocalBackend`, register it in
`LOCAL_PROVIDERS`, and add a test row with the new provider name.

</details>

<details>
<summary>Providers and model catalogue</summary>

This benchmark suite currently tests models from the following providers:

| Provider | Model                                 | Notes                                                     |
|----------|---------------------------------------|-----------------------------------------------------------|
| **Alibaba** | qwen3.5-plus-2026-02-15                   | Qwen 3.5 Plus (Feb 2026); multimodal                       |
| | qwen3.5-35b-a3b                           | Qwen 3.5, 35B MoE (3B active)                              |
| | qwen3.5-27b                               | Qwen 3.5, 27B dense                                        |
| | qwen3.5-122b-a10b                         | Qwen 3.5, 122B MoE (10B active)                            |
| | qwen3.5-397b-a17b                         | Qwen 3.5, 397B MoE (17B active)                            |
| | qwen3.5-flash-2026-02-23                  | Qwen 3.5 Flash (Feb 2026)                                  |
| **Anthropic** | ~~claude-3-5-sonnet-20241022~~            | ~~Claude 3.5 Sonnet~~ (legacy)                             |
| | ~~claude-3-7-sonnet-20250219~~            | ~~Claude 3.7 Sonnet~~ (legacy)                             |
| | ~~claude-3-opus-20240229~~                | ~~Claude 3 Opus~~ (legacy)                                 |
| | ~~claude-3-5-haiku-20241022~~             | ~~Claude 3.5 Haiku~~ (legacy)                              |
| | claude-haiku-4-5-20251001                 | Claude Haiku 4.5                                           |
| | claude-opus-4-1-20250805                  | Claude Opus 4.1                                            |
| | ~~claude-opus-4-20250514~~                | ~~Claude Opus 4~~ (legacy)                                 |
| | claude-opus-4-5-20251101                  | Claude Opus 4.5                                            |
| | ~~claude-sonnet-4-20250514~~              | ~~Claude Sonnet 4~~ (legacy)                               |
| | claude-sonnet-4-5-20250929                | Claude Sonnet 4.5                                          |
| | claude-opus-4-6                           | Claude Opus 4.6                                            |
| | claude-opus-4-7                           | Claude Opus 4.7                                            |
| | claude-opus-4-8                           | Claude Opus 4.8                                            |
| | claude-sonnet-4-6                         | Claude Sonnet 4.6                                          |
| | claude-sonnet-5                           | Claude Sonnet 5                                            |
| | claude-fable-5                            | Claude Fable 5                                             |
| | claude-fable-5-1                          | Claude Fable 5.1                                           |
| | claude-opus-5                             | Claude Opus 5                                              |
| **Cohere** | command-a-03-2025                         | Command A (Mar 2025)                                       |
| | command-a-vision-07-2025                  | Command A Vision (Jul 2025); multimodal                    |
| | command-r-08-2024                         | Command R (Aug 2024)                                       |
| | command-r-plus-08-2024                    | Command R+ (Aug 2024)                                      |
| | command-r7b-12-2024                       | Command R 7B (Dec 2024)                                    |
| **DeepSeek** | deepseek-chat                             | DeepSeek V3 (chat)                                         |
| | deepseek-reasoner                         | DeepSeek R1; reasoning                                     |
| | deepseek-v4-flash                         | DeepSeek V4 Flash                                          |
| | deepseek-v4-pro                           | DeepSeek V4 Pro                                            |
| | deepseek-v4-flash-vision-exp              | DeepSeek V4 Flash Vision (experimental); multimodal        |
| **Google/Gemini** | ~~gemini-1.5-flash~~                      | ~~Gemini 1.5 Flash~~ (legacy)                              |
| | ~~gemini-1.5-pro~~                        | ~~Gemini 1.5 Pro~~ (legacy)                                |
| | ~~gemini-2.0-flash~~                      | ~~Gemini 2.0 Flash~~ (legacy)                              |
| | ~~gemini-2.0-flash-lite~~                 | ~~Gemini 2.0 Flash-Lite~~ (legacy)                         |
| | ~~gemini-2.0-pro-exp-02-05~~              | ~~Gemini 2.0 Pro (experimental)~~ (legacy)                 |
| | gemini-2.5-flash                          | Gemini 2.5 Flash                                           |
| | gemini-2.5-flash-lite                     | Gemini 2.5 Flash-Lite                                      |
| | ~~gemini-2.5-flash-lite-preview-09-2025~~ | ~~Gemini 2.5 Flash-Lite (preview, Sep 2025)~~ (legacy)     |
| | ~~gemini-2.5-flash-preview-04-17~~        | ~~Gemini 2.5 Flash (preview, Apr 2025)~~ (legacy)          |
| | ~~gemini-2.5-flash-preview-09-2025~~      | ~~Gemini 2.5 Flash (preview, Sep 2025)~~ (legacy)          |
| | gemini-2.5-pro                            | Gemini 2.5 Pro                                             |
| | ~~gemini-2.5-pro-exp-03-25~~              | ~~Gemini 2.5 Pro (experimental)~~ (legacy)                 |
| | ~~gemini-2.5-pro-preview-05-06~~          | ~~Gemini 2.5 Pro (preview, May 2025)~~ (legacy)            |
| | ~~gemini-exp-1206~~                       | ~~Gemini experimental (Dec 2024)~~ (legacy)                |
| | gemini-3-flash-preview                    | Gemini 3 Flash (preview)                                   |
| | ~~gemini-3.1-flash-lite-preview~~         | ~~Gemini 3.1 Flash-Lite (preview)~~ (legacy)               |
| | gemini-3.1-flash-lite                     | Gemini 3.1 Flash-Lite                                      |
| | gemini-3.1-pro-preview                    | Gemini 3.1 Pro (preview)                                   |
| | ~~gemini-3-pro-preview~~                  | ~~Gemini 3 Pro (preview)~~ (legacy)                        |
| | gemini-3.5-flash                          | Gemini 3.5 Flash                                           |
| | gemini-3.6-flash                          | Gemini 3.6 Flash                                           |
| | gemini-3.5-flash-lite                     | Gemini 3.5 Flash-Lite                                      |
| | gemini-3.7-flash                          | Gemini 3.7 Flash                                           |
| | gemini-3.8-flash                          | Gemini 3.8 Flash                                           |
| **Hugging Face** | swiss-ai/Apertus-v1.5-70B:publicai        | Apertus v1.5, 70B (Swiss AI Initiative); multimodal         |
| | swiss-ai/Apertus-v1.5-8B:publicai         | Apertus v1.5, 8B (Swiss AI Initiative); multimodal          |
| | Qwen/Qwen3-VL-235B-A22B-Instruct:deepinfra | Qwen3-VL 235B-A22B Instruct (Alibaba); multimodal          |
| | MiniMaxAI/MiniMax-M3:deepinfra            | MiniMax M3 (MiniMax); multimodal                            |
| | thinkingmachines/Inkling-Small:deepinfra  | Inkling Small (Thinking Machines); multimodal               |
| | thinkingmachines/Inkling:together         | Inkling (Thinking Machines); multimodal                     |
| | meta-models/Muse-Glimmer-30B:together     | Muse Glimmer 30B (Meta Models); multimodal                  |
| **Mistral AI** | ~~magistral-medium-2509~~                 | ~~Magistral Medium (Sep 2025); reasoning~~ (legacy)        |
| | ~~magistral-small-2509~~                  | ~~Magistral Small (Sep 2025); reasoning~~ (legacy)         |
| | ministral-14b-2512                        | Ministral 3 14B (Dec 2025)                                 |
| | ministral-8b-2512                         | Ministral 3 8B (Dec 2025)                                  |
| | ~~mistral-large-2411~~                    | ~~Mistral Large (Nov 2024)~~ (legacy)                      |
| | mistral-large-2512                        | Mistral Large (Dec 2025)                                   |
| | ~~mistral-medium-2505~~                   | ~~Mistral Medium (May 2025)~~ (legacy)                     |
| | ~~mistral-medium-2508~~                   | ~~Mistral Medium (Aug 2025)~~ (legacy)                     |
| | mistral-medium-3.5                        | Mistral Medium 3.5 (Apr 2026)                              |
| | ~~mistral-small-2506~~                    | ~~Mistral Small (Jun 2025)~~ (legacy)                      |
| | ~~pixtral-12b~~                           | ~~Pixtral 12B; multimodal~~ (legacy)                       |
| | ~~pixtral-large-2411~~                    | ~~Pixtral Large (Nov 2024); multimodal~~ (legacy)          |
| **OpenAI** | gpt-4.1                                   | GPT-4.1                                                    |
| | gpt-4.1-mini                              | GPT-4.1 Mini                                               |
| | gpt-4.1-nano                              | GPT-4.1 Nano                                               |
| | ~~gpt-4.5-preview~~                       | ~~GPT-4.5 (preview)~~ (legacy)                             |
| | gpt-4o                                    | GPT-4o; multimodal                                         |
| | gpt-4o-mini                               | GPT-4o Mini; multimodal                                    |
| | gpt-5                                     | GPT-5                                                      |
| | gpt-5.1-2025-11-13                        | GPT-5.1 (Nov 2025)                                         |
| | gpt-5.2-2025-12-11                        | GPT-5.2 (Dec 2025)                                         |
| | gpt-5.3-codex                             | GPT-5.3 Codex; coding                                      |
| | gpt-5.4-2026-03-05                        | GPT-5.4 (Mar 2026)                                         |
| | gpt-5.5-2026-04-23                        | GPT-5.5 (Apr 2026)                                         |
| | gpt-5.6-sol                               | GPT-5.6 Sol                                                |
| | gpt-5.6-terra                             | GPT-5.6 Terra                                              |
| | gpt-5.6-luna                              | GPT-5.6 Luna                                               |
| | gpt-6-astra                               | GPT-6 Astra                                                |
| | gpt-5-mini                                | GPT-5 Mini                                                 |
| | gpt-5-nano                                | GPT-5 Nano                                                 |
| | o3                                        | OpenAI o3; reasoning                                       |
| **OpenRouter** | google/gemma-4-26b-a4b-it                 | Gemma 4, 26B MoE (4B active), instruction-tuned            |
| | google/gemma-4-31b-it                     | Gemma 4, 31B, instruction-tuned                            |
| | meta-llama/llama-4-maverick               | Llama 4 Maverick                                           |
| | qwen/qwen3-vl-30b-a3b-instruct            | Qwen3-VL, 30B MoE (3B active), instruction-tuned; multimodal |
| | qwen/qwen3-vl-8b-instruct                 | Qwen3-VL 8B, instruction-tuned; multimodal                 |
| | qwen/qwen3-vl-8b-thinking                 | Qwen3-VL 8B, reasoning; multimodal                         |
| | qwen/qwen3.8-max                          | Qwen 3.8 Max; multimodal                                   |
| | qwen/qwen3.8-flash                        | Qwen 3.8 Flash; multimodal                                 |
| | qwen/qwen3.8-27b                          | Qwen 3.8, 27B dense; multimodal                            |
| | qwen/qwen3.7-plus                         | Qwen 3.7 Plus                                              |
| | qwen/qwen3.6-plus                         | Qwen 3.6 Plus                                              |
| | qwen/qwen3.5-122b-a10b                    | Qwen 3.5, 122B MoE (10B active)                            |
| | qwen/qwen3.5-27b                          | Qwen 3.5, 27B dense                                        |
| | qwen/qwen3.5-35b-a3b                      | Qwen 3.5, 35B MoE (3B active)                              |
| | qwen/qwen3.5-397b-a17b                    | Qwen 3.5, 397B MoE (17B active)                            |
| | qwen/qwen3.5-plus-02-15                   | Qwen 3.5 Plus (Feb 2026)                                   |
| | qwen/qwen3.5-flash-02-23                  | Qwen 3.5 Flash (Feb 2026)                                  |
| | qwen/qwen3.5-9b                           | Qwen 3.5 9B                                                |
| | ~~x-ai/grok-4~~                           | ~~Grok 4; multimodal~~ (legacy)                            |
| | meta-llama/llama-4-scout                  | Llama 4 Scout                                              |
| | stepfun/step-3.7-flash                    | StepFun Step 3.7 Flash                                     |
| | moonshotai/kimi-k3                        | Kimi K3                                                    |
| | meta/muse-spark-1.2                       | Muse Spark 1.2 (Meta); multimodal                          |
| | z-ai/glm-5v-turbo                         | GLM-5V Turbo (Z.ai); multimodal                            |
| | meta/muse-spark-1.3                       | Muse Spark 1.3 (Meta); multimodal                          |
| | z-ai/glm-5.3-flash                        | GLM-5.3 Flash (Z.ai); multimodal                           |
| **sciCORE** | ~~GLM-4.5V-FP8~~                              | ~~GLM-4.5V, FP8 quantization; multimodal (Univ. of Basel HPC)~~ (legacy) |
| | ~~qwen3-235b-fp8~~                            | ~~Qwen3 235B, FP8 quantization (Univ. of Basel HPC)~~ (legacy)          |
| | qwen35-397b-a17b-fp8                      | Qwen3.5 397B-A17B, FP8 quantization (Univ. of Basel HPC)   |
| **xAI** | grok-4.20-0309-reasoning                  | Grok 4.20; reasoning                                       |
| | grok-4.3                                  | Grok 4.3                                                   |
| | grok-4.5                                  | Grok 4.5; multimodal                                       |
| | grok-4.6                                  | Grok 4.6; multimodal                                       |

**Note:** OpenRouter provides access to models from multiple providers through a unified API. Hugging Face routes to third-party inference providers through an OpenAI-compatible API; the suffix on each model name pins the provider that serves it (`:publicai`, `:deepinfra`, `:together`), so that the price and the routing of a benchmark run are reproducible. sciCORE provides access to models hosted on the University of Basel's high-performance computing infrastructure.

</details>

## Methodology

### How it works

The RISE Humanities Data Benchmark is designed to be modular and extensible. Each test applies a model configuration to a benchmark dataset, scores the responses against the ground truths, and stores the results.
The framework, datasets, and recorded results are included in this repository.

<img width="2279" height="1206" alt="how-it-works" src="https://github.com/user-attachments/assets/ae3197f1-2ea8-4d5f-bb47-94f0cb0e3a69" />

### Ground truths

Model outputs are compared with the ground truth for the same inputs. Consult each benchmark's documentation for its sources, annotation process, and scoring rules. Interpret results in light of the sample size, source selection, and task definition.

### Metrics

Each benchmark defines its own scoring function, so a metric name belongs to a benchmark rather than
to the suite as a whole.

#### Task performance

Before comparing or combining two scores, check three things about them.

- **What kind of number it is.** A measurement, a count and a setting are not interchangeable.
  `magazine_pages` records `mean_iou`, the overlap its matched boxes actually achieved, next to
  `iou_threshold`, the overlap they were required to reach; averaging the two together means nothing.
- **Which direction is better.** Character error rate is lower-is-better, while fuzzy similarity, F1,
  precision and recall are higher-is-better. They cannot be pooled without inverting one of them.
- **Whether it aggregates at all.** Counts sum; ratios do not. Where a benchmark records true and
  false positives beside its F1, those counts are the sufficient statistic — `library_cards` rebuilds
  micro precision, recall and F1 from summed counts, which averaging per-request F1 scores would not
  give.

The same name can also mean different things across benchmarks. `book_advert_xml` records `fuzzy` on
a 0–100 scale, while every other benchmark reporting `fuzzy` uses 0–1. Rescaling alone does not make
two tasks comparable.

#### Cost and runtime

- **Compute cost** is estimated per run from recorded token counts and the pricing entry in force on
  the run date (`scripts/data/pricing.json`), each entry archived as a Wayback Machine snapshot.
- **Test time** is recorded for each API call.
- **Cost and time per performance point** ($/point, seconds/point per item) are efficiency ratios,
  normalised per test, then per benchmark, then globally. What they mean depends on the metric being
  normalised and on the aggregation rules above.

A blank is not a zero. A missing cost, an unscored run or a failed request records the absence
of a measurement, and counting it as zero moves any average that includes it.

<details>
<summary>Practical considerations</summary>

When using this benchmark suite for your own research, consider the following:

| Category | Consideration | Description |
|----------|---------------|-------------|
| **Resource Requirements** | Skills | Operationalizing tasks requires both domain knowledge and technical expertise |
| | Ground Truth Creation | Requires domain expertise and careful curation |
| | Metric Selection | Requires understanding of both the humanities domain and evaluation methods |
| **Technical** | Local vs. API Models | Determine if you need to run models locally or can use API services |
| | Data Privacy | Ensure you're allowed to share your data via APIs if needed |
| | Infrastructure | Consider if you have access to appropriate computing resources |
| **Compliance** | Legal Requirements | Check for any legal restrictions on data sharing or model usage |
| | Ethical Guidelines | Consider any ethical implications of your benchmarking approach |
| | Funder Requirements | Verify if there are any funding agency requirements |
| | FAIR Data Principles | Consider how to make your benchmark data Findable, Accessible, Interoperable, and Reusable |

</details>

<details>
<summary>Terminology</summary>

- **Ad hoc test**: A temporary benchmark configuration run with `scripts/run_single_test.py --adhoc` for experimentation.
- **Benchmark**: A task for models to perform, consisting of images, ground truths, prompts, dataclasses, and scoring functions. Each benchmark is stored in a separate directory.
- **Configured Test**: A specific instance of a benchmark run with a particular configuration (ID, provider, model, temperature, role description, prompt file, dataclass).
- **Dataclass**: Pydantic models for structured output, supported across all providers.
- **Ground Truth**: The correct answer used to evaluate the model's response.
- **Image**: Visual input for the task. Images are paired with ground truth files.
- **Model**: Specific model used to perform the task.
- **Prompt**: Text given to the model to guide its response.
- **Local Provider**: Provider handled by a local backend instead of an API (`contour_local`, `sam3_local`, `grounding_dino_local`, `doclayout_yolo_local`). Registered in `local/__init__.py`; no API key required.
- **Provider**: Company or service providing model access (`openai`, `genai`, `anthropic`, `cohere`, `mistral`, `openrouter`, `scicore`, `deepseek`, `x-ai`, `alibaba`, or `huggingface`).
- **Request**: API call(s) made during a test, consisting of images and prompts.
- **Response**: Model's answer containing metadata and output.
- **Score**: Evaluation result indicating model performance.
- **Scoring Function**: Function that evaluates the model's response, implemented via the `score_request_answer` and `score_benchmark` methods.
- **Test Configuration**: Parameters for running a test, stored in `benchmarks/benchmarks_tests.csv`.
- **Text file**: Textual input for the task. Text files are paired with ground truth files.

</details>

## Contributing

Contributions can include new datasets, ground truths, scoring methods, model integrations, and documentation.
See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution roles and requirements, and the
[benchmark template](benchmarks/README_TEMPLATE.md) for dataset documentation.
Report bugs, propose benchmarks, or discuss improvements through
[GitHub Issues](https://github.com/rise-unibas/humanities_data_benchmark/issues).

<details>
<summary>Create a benchmark: technical guide</summary>

Start with the CLI tool to create the basic structure:

```
python scripts/create_benchmark.py
```
The command creates the following benchmark structure:

1. **Directory Structure:**
   - `benchmarks/[your_benchmark_name]/`
   - `images/` or `texts/` directories (based on your choice)
   - `ground_truths/` directory
   - `prompts/` directory

2. **Required Files:**
   - `benchmark.py` - Main benchmark class with scoring logic templates
   - `meta.json` - Benchmark metadata
   - `README.md` - Documentation
   - `prompts/prompt.txt` - Default prompt
   - `dataclass.py` - Pydantic schema (optional)

**Step-by-Step Process**
When starting the `create_benchmark.py` script, you will be guided through the creation of the following data:

**1. Benchmark Name**
- Must be lowercase with underscores (e.g., `personal_letters`)
- **Important:** Should describe the SOURCE, not the task
  - Good: `personal_letters`, `company_registers`, `manuscript_pages`
  - Bad: `date_recognition`, `entity_extraction`
- Choose a stable name, as test configurations and result paths refer to it.
- Will be converted to CamelCase for the class name (e.g., `PersonalLetters`)

**2. Basic Information**
- **Title:** Full descriptive title
- **Short Title:** Abbreviated version for displays
- **Description:** Multi-line description (press Enter twice to finish)
  - Should describe both SOURCES and TASK

**3. Tags**
- Structured tags from specific categories:
  - **Source Type:** index-cards, letter-pages, manuscript-pages, book-pages, article-pages, essay-pages, registers, lists
  - **Structure:** text-like, list-like, table-like, mixed
  - **Text Type:** handwritten-source, typed-source, printed-source
  - **Century:** century-15th, century-16th, century-17th, century-18th, century-19th, century-20th
  - **Languages:** language-german, language-english
  - **Entry Type:** company-entries, bibliographic-entries, ner-entries
  - **Task:** ner-extraction, metadata-extraction, transcription, classification
  - **Misc:** test-benchmark
- Enter as comma-separated values

**4. Contributors**
- Add contributors by role:
  - Domain Expert
  - Data Curator
  - Annotator
  - Analyst
  - Engineer
- **Format:** firstname_lastname (e.g., john_doe, jane_smith)
- Details of non-existing users can be added later

**5. Scoring Configuration**
- Defaults to `fuzzy` metric with `descending` order
- Can be customized later in `meta.json`

**6. Data Structure**
- **Dataclass:** Strongly recommended - defines expected output structure using Pydantic
  - Enables automatic validation
  - Ensures consistent output format
- **Dataclass Name:** Should reflect result content (e.g., Page, Letter, Document)
  - Use CamelCase
- **Images:** Whether the benchmark uses images
- **Text Files:** Whether the benchmark uses text files

**7. Prompt**
- Enter the default prompt text (multi-line)
- **This prompt is editable** and can be changed later in `prompts/prompt.txt`
- Role description for system prompt

**8. Review and Edit**
- Review all collected settings
- **Edit any field** by entering its number (1-12)
- Enter 'c' to continue and create benchmark
- Enter 'q' to quit without creating

**After Creation:**

1. **Add Context Data:**
   - Place images in `benchmarks/[name]/images/`
   - Place ground truth JSON files in `benchmarks/[name]/ground_truths/`
   - Each ground truth filename must match its corresponding image (e.g., `image.jpg` → `image.json`)

2. **Implement Scoring:**
   - Edit `benchmarks/[name]/benchmark.py`
   - Implement `score_request_answer()` method
   - Implement `score_benchmark()` method

3. **Define Schema (if using dataclass):**
   - Edit `benchmarks/[name]/dataclass.py`
   - Add fields to your Pydantic model

**Add Context Data**
You need to add at least one image or text file. This is the context data.
Context data are the inputs that will be sent to the LLM. Depending on the benchmark, this may include:

- .txt, .json and other text-only files (historical texts, metadata records, descriptions, OCR fragments)
- .jpg, .png or other image types (manuscript pages, document snippets, photos)

_Naming convention_:
- The whole filename without its ending is treated as context object name
- This means that all files with the same basename in the context directories (images, texts) are sent at the same time
- For each basename you must provide a ground truth file

**Implement Scoring**
Each benchmark has a corresponding benchmark class in benchmark.py. Two methods have to be implemented in order for the scoring to work:

_Implement the scoring of a single object/request:_
Implement the scoring for a single request. The comparison should reflect the task and its ground truths; exact equality is not always an appropriate metric.

```python
def score_request_answer(self, object_name, response, ground_truth):
   # object_name: basename of the processed files
   # response: large language model response
   # ground_truth: corresponding_ground_truth

   calculated_score = 0
   field_scores = {}
   # implement scoring for one object, recording each comparison as you make it
   field_scores["title"] = {"response": "Der Process",
                            "ground_truth": "Der Proceß",
                            "score": 0.8}

   return {"fuzzy": calculated_score, "field_scores": field_scores}
```

Besides your metrics, record **`field_scores`**: the values you compared, keyed by whatever unit
your scorer uses (a field name, a folio reference, a matched box). The result views display your
scorer's own judgement and cannot derive it: one benchmark matches boxes by overlap, another aligns
folios by position, so an independent comparison would contradict the score beside it. Use
`score: None` where your scorer gives counts rather than a similarity, and keep everything
JSON-serializable, because the dict is written verbatim into the stored answer.

_Implement the scoring of the whole test run:_
Define how request-level scores are aggregated for the test run, for example with an arithmetic mean.

```python
def score_benchmark(self, all_scores):
       total_score = 0
       for score in all_scores:
           total_score += score['fuzzy']
       return {"fuzzy": total_score / len(all_scores)}
```

`score_benchmark` receives those same dicts, `field_scores` included: read metrics by key, and do
not log a whole score, which carries every comparison made for that object.

Return at least one metric. Commonly used metrics are fuzzy, f1_score, cer

**Define Schema**
If you want the model to return structured output, define a Pydantic model in `benchmarks/[name]/dataclass.py` and
reference its class name in the `dataclass` column of `benchmarks/benchmarks_tests.csv`. Nested models are supported, and field
descriptions are passed on to the provider, so use them to disambiguate fields.

```python
from typing import List, Optional
from pydantic import BaseModel, Field


class Entry(BaseModel):
    """A single entry on the page."""

    name: str = Field(description="Name as written in the source")
    year: Optional[str] = Field(default=None, description="Year, if given")


class Page(BaseModel):
    """Main output structure; its name goes into the `dataclass` column."""

    entries: List[Entry] = Field(default_factory=list, description="All entries on the page")
```

Beyond the two mandatory scoring methods, the benchmark class inherits a number of methods from `Benchmark`
(`scripts/benchmark_base.py`) that you can override to configure its behaviour:

| Method | Purpose |
|--------|---------|
| `remove_none_values()` | Whether `None` values are stripped from the response before scoring (default `True`) |
| `convert_truth_to_json()` | Whether a ground truth stored as a JSON string is parsed into an object (default `True`) |
| `resize_images()` | Whether oversized images are resized before being sent to the model (default `False`) |
| `get_title()` | Title of the benchmark as shown in the result table |
| `get_prompt_kwargs(basename, filenames)` | Values interpolated into the prompt file, e.g. file information |
| `skip_object(object_basename)` | Whether a given object is excluded from the run |

</details>

<details>
<summary>Submission and review checklist</summary>

**Before submitting**

Before submitting a pull request, please make sure your benchmark meets all of the following criteria:

**Data Requirements**
- Dataset is not too large
  Recommended: < 50 MB total
- Ground truths are manually checked and reliable
- Data is legally usable
- Must be openly available
- No copyrighted or sensitive data
  - A clear license is indicated (preferably open license)
- Context files are properly named and paired with ground_truths

**Technical Requirements**
- Benchmark runs locally without errors
- Scoring metric is clearly defined and documented
- Directory structure follows the template
- README.md inside the benchmark folder is fully completed
  (template is created automatically by create_benchmark.py)

**Quality Requirements**
- Outputs are deterministic enough for fair evaluation
- The benchmark fills a clear research gap (new task, domain, or corpus)
- Instructions do not bias the LLM toward “right answers” via over-specification

**Create a pull request**
- Fork `RISE-UNIBAS/humanities_data_benchmark` and push your benchmark to a branch on your fork.
- Go to your fork on GitHub.
- Click “Compare & pull request”.
- Target: `RISE-UNIBAS/humanities_data_benchmark → main`

Add a short description:
- What your benchmark tests
- Example ground truth formats
- Scoring logic summary
- How you validated the dataset
- Any remaining issues or questions

**Review and publication**
The maintainers will:

- run the benchmark locally
- check the metric
- confirm licensing
- validate folder structure
- potentially request revisions

Once the review requirements are met, the maintainers can merge the benchmark into the main repository.

</details>

## Citation and licensing

### Cite this work

Use the metadata in [CITATION.cff](CITATION.cff) to cite the software and identify the release or commit used.
Archived releases are available through the [project DOI](https://doi.org/10.5281/zenodo.16941752).

### Publications and background

Hindermann, M., Kasper, L. K., Marti, S., &amp; Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481

Hindermann, M., & Marti, S. (2026). The RISE Humanities Data Benchmark: From Anecdote to Evidence. DH Benelux 2026, Maastricht, Netherlands. Zenodo. https://doi.org/10.5281/zenodo.20595263

Hindermann, M., & Marti, S. (2025, March 19). *RISE Crash Course: "AI Benchmarking"*. Zenodo. https://doi.org/10.5281/zenodo.15062831

### Licensing

The benchmark software is licensed under [GNU GPL version 3](LICENSE).
For benchmark input materials and ground truths, consult the relevant benchmark's documentation
and source attribution for applicable reuse terms.

## Contributors

This project is developed by a multidisciplinary team at the University of Basel's RISE (Research and Infrastructure Support).

| Name                        | GitHub                                                 | ORCID                                                        |
|-----------------------------|--------------------------------------------------------|--------------------------------------------------------------|
| Anthea Alberto              | [@antheajeanne](https://github.com/antheajeanne)       | [0009-0007-0430-0050](https://orcid.org/0009-0007-0430-0050) |
| Alexandra Binnenkade        | —                                                      | [0000-0002-9518-7212](https://orcid.org/0000-0002-9518-7212) |
| Arno Bosse                  | [@kintopp](https://github.com/kintopp)                 | [0000-0003-3681-1289](https://orcid.org/0000-0003-3681-1289) |
| Sven Burkhardt              | [@Sveburk](https://github.com/Sveburk)                 | [0009-0001-4954-4426](https://orcid.org/0009-0001-4954-4426) |
| Eric Decker                 | [@edecker](https://github.com/edecker)                 | [0000-0003-3035-2413](https://orcid.org/0000-0003-3035-2413) |
| Pema Frick                  | [@pwmff](https://github.com/pwmff)                     | [0000-0002-8733-7161](https://orcid.org/0000-0002-8733-7161) |
| Maximilian Hindermann       | [@MHindermann](https://github.com/MHindermann)         | [0000-0002-9337-4655](https://orcid.org/0000-0002-9337-4655) |
| Lea Kasper                  | [@lekasp](https://github.com/lekasp)                   | [0000-0002-4671-1700](https://orcid.org/0000-0002-4671-1700) |
| Ana-Maria Leonte            | —                                                      | [0009-0005-4678-2807](https://orcid.org/0009-0005-4678-2807) |
| José Luis Losada Palenzuela | [@editio](https://github.com/editio)                   | [0000-0002-6530-1328](https://orcid.org/0000-0002-6530-1328) |
| Sven Lienhard               | —                                                      | [0009-0005-9981-4286](https://orcid.org/0009-0005-9981-4286) |
| Sorin Marti                 | [@sorinmarti](https://github.com/sorinmarti)           | [0000-0002-9541-1202](https://orcid.org/0000-0002-9541-1202) |
| Gabriel Müller              | [@gbmllr1](https://github.com/gbmllr1)                 | [0000-0001-8320-5148](https://orcid.org/0000-0001-8320-5148) |
| Ina Serif                   | [@wissen-ist-acht](https://github.com/wissen-ist-acht) | [0000-0003-2419-4252](https://orcid.org/0000-0003-2419-4252) |
| Elena Spadini               | [@elespdn](https://github.com/elespdn)                 | [0000-0002-4522-2833](https://orcid.org/0000-0002-4522-2833) |
| Tabea Wullschleger          | [@tabea-w](https://github.com/tabea-w) | [0000-0001-9841-0005](https://orcid.org/0000-0001-9841-0005) |
| Franziska Zúñiga            | —                                                      | [0000-0002-8844-4903](https://orcid.org/0000-0002-8844-4903) |

For detailed attribution by benchmark and contribution type, see our [CONTRIBUTORS.md](CONTRIBUTORS.md) file.
