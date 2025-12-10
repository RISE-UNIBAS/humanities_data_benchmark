# RISE Humanities Data Benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17866725.svg)](https://doi.org/10.5281/zenodo.17866725)

This repository contains benchmark datasets (images and text files), prompts, ground truths, and evaluation scripts for
assessing the performance of large language models (LLMs) on humanities-related tasks. The suite is
designed as a resource for researchers and practitioners interested in systematically evaluating
how well various LLMs perform on digital humanities (DH) tasks involving visual and text-like materials.

> **ℹ Looking for benchmark results?**     
> This README provides an overview of the benchmark suite and explains how to use it.  
> For detailed test results and model comparisons, visit our [results dashboard](https://rise-services.rise.unibas.ch/benchmarks/).

## What is Benchmarking and Why Should You Care?

Benchmarking is the process of systematically evaluating and ranking various models for specific tasks using well-defined ground truths and metrics. For humanities research, benchmarking provides:

- **Evidence-based decision-making** about which model(s) to use for which humanities-specific task(s)
- **Quantifiable comparisons** between different AI models on humanities data, including cost efficiency analysis
- **Standardized evaluation** of model performance on tasks like historical document analysis, transcription, and metadata extraction

This benchmark suite focuses on tasks essential to digital humanities work with visual materials, helping researchers make informed choices about which AI systems best suit their specific research needs.

> **ℹ Looking for more background?**  
> For a deeper introduction to AI benchmarking in humanities contexts, see:  
> Hindermann, M., & Marti, S. (2025, March 19). *RISE Crash Course: "AI Benchmarking"*. Zenodo. https://doi.org/10.5281/zenodo.15062831

## Table of Contents

| | |
|--------|-------------|
| **[1. Overview](#1-overview)** | |
| [1.1. Terminology](#11-terminology) | What terms are used for what?|
| [1.2. Available Benchmarks](#12-available-benchmarks) | List of currently available datasets |
| [1.3. How it Works](#13-how-it-works) | Breakdown of the framework's functionality |
| [1.4. Practical Considerations](#14-practical-considerations) |  |
| **[2. Use it!](#2-use-it)** |  |
| [2.1. Fork and prepare](#21-fork-and-prepare) | Start here with your own benchmark project. |
| [2.2. Run a configured test](#22-run-a-configured-test) | Test the framework and your setup. |
| [2.3. Create a new Benchmark](#23-create-a-new-benchmark) | Use our CLI tool for easy creation, add context data and implement scoring.|
| [2.4. Run an adhoc test](#24-run-an-adhoc-test) | Test your created benchmark and inspect the test results. |
| [2.5. Generate a result render](#25-generate-a-result-render) | Pretty-print your results for better inspection.  |
| **[3. Share it!](#3-share-it)** | |
| [3.1. Before Submitting](#31-before-submitting) | Did you complete the checklist? |
| [3.2. Create a pull request](#32-create-a-pull-request) | Submit your dataset. |
| [3.3. Review & Publication](#33-review--publication) | We check your submission. Now what? |
| **[4. Providers & Models](#4-providers-and-models)** | List of implemented providers and models.|
| **[5. Benchmarking Methodology](#5-benchmarking-methodology)** | |
| [5.1. Ground Truth](#51-ground-truth) | How to create, what to consider. |
| [5.2. Metrics](#52-metrics) | How to score, what to consider. |
| **[6. Project Status](#6-project-status)** | |
| [6.1. Current Limitations](#61-current-limitations) | |
| [6.2. Outlook](#62-outlook) |  |
| **[7. Contributors](#7-contributors)** | |


## 1. Overview

### 1.1. Terminology
- **Adhoc-Test**: A specific instance of a benchmark run which is only run once with the run-tests-tool CLI for testing reasons.
- **Benchmark**: A task for models to perform, consisting of images, ground truths, prompts, dataclasses, and scoring functions. Each benchmark is stored in a separate directory.
- **Configured Test**: A specific instance of a benchmark run with a particular configuration (ID, provider, model, temperature, role description, prompt file, dataclass).
- **Dataclass**: Pydantic models for structured output, supported across all providers.
- **Ground Truth**: The correct answer used to evaluate the model's response.
- **Image**: Visual input for the task. Images are paired with ground truth files.
- **Model**: Specific model used to perform the task.
- **Prompt**: Text given to the model to guide its response. 
- **Provider**: Company or service providing model access (`openai`, `genai`, `anthropic`, `cohere`, `mistral`, `openrouter`, or `scicore`).
- **Request**: API call(s) made during a test, consisting of images and prompts.
- **Response**: Model's answer containing metadata and output.
- **Score**: Evaluation result indicating model performance.
- **Scoring Function**: Function that evaluates the model's response, implemented via the `score_answer` method.
- **Test Configuration**: Parameters for running a test, stored in `benchmarks_tests.csv`.
- **Text file**: Textual input for the task. Text files are paired with ground truth files.

### 1.2. Available Benchmarks
This benchmark suite currently includes the following benchmarks for evaluating LLM performance on humanities tasks:

| Benchmark | Description |
|-----------|-------------|
| **[Bibliographic Data](benchmarks/bibliographic_data/)** | Extract bibliographic information (publication details, authors, dates, metadata) from historical documents |
| **[Blacklist Cards](benchmarks/blacklist/)** | Extract and structure information from historical blacklist cards |
| **[Book Advert XML](benchmarks/book_advert_xml/)** | Correct malformed XML from 18th century book advertisements |
| **[Company Lists](benchmarks/company_lists/)** | Extract structured company information from historical business listings and directories |
| **[Fraktur Adverts](benchmarks/fraktur/)** | Recognize and transcribe historical German Fraktur script (16th-20th centuries) |
| **[Medieval Manuscripts](benchmarks/medieval_manuscripts/)** | Page segmentation and handwritten text extraction from 15th century medieval German manuscripts |
| **[Business Letters](benchmarks/metadata_extraction/)** | Extract structured metadata (names, organizations, dates, locations) from 20th century Swiss historical correspondence |
| **[Library Cards](benchmarks/zettelkatalog/)** | Catalog card analysis and information extraction from historical library catalog systems |
| **Test Benchmarks** | System validation and basic functionality testing ([test_benchmark](benchmarks/test_benchmark/), [test_benchmark2](benchmarks/test_benchmark2/)) |

### 1.3. How it Works
The RISE Humanities Data Benchmark is designed to be modular and extensible. There is a number of datasets which are submitted to tests and their results are saved.
The whole framework, the datasets and the resukts are part of this repository.

<img width="2279" height="1206" alt="how-it-works" src="https://github.com/user-attachments/assets/ae3197f1-2ea8-4d5f-bb47-94f0cb0e3a69" />

Refer to the [next chapter](#use-it) in order to learn about usage in your own research.

### 1.4. Practical Considerations
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


## 2. Use it!

> **ℹ We welcome your contributions**     
> The benchmark suite is designed to be extensible and welcomes contributions from the digital humanities community. Whether you're adding new benchmarks, improving existing ones, or enhancing the evaluation framework, your contributions help advance AI evaluation for humanities research.
> For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md). To report bugs, suggest features, or discuss improvements, please open an issue on our [GitHub Issues page](https://github.com/rise-unibas/humanities_data_benchmark/issues).

### 2.1. Fork and prepare
In order to start, the following steps are in order:
- Fork this repository and clone your fork
- Obtain API keys to the providers you want to test
- Create a `.env` file in the root directory of the repository.

Add the following lines as needed with the obtained API key.
```bash
OPENAI_API_KEY=<your_openai_api_key>
GENAI_API_KEY=<your_genai_api_key>
ANTHROPIC_API_KEY=<your_anthropic_api_key>
COHERE_API_KEY=<your_cohere_api_key>
MISTRAL_API_KEY=<your_mistral_api_key>
OPENROUTER_API_KEY=<your_openrouter_api_key>
SCICORE_API_KEY=<your_scicore_api_key>
```

### 2.2. Run a configured test
To test if your installation works, it's easiest to run one of the configured tests. Define one of `OPENAI_API_KEY` (= `T0001`),  `GENAI_API_KEY` (= `T0002`) or `ANTHROPIC_API_KEY`  (= `T0003`) to get started.
Start the script from tha root of your project, like so:

```
python scripts/run_single_test.py --test_id T0001
```

This executes the `test_benchmark` (one image, one request) and saves the results to `results/YYYY-MM-DD/T0001`. Once these results are present, the test will **not** send requests for existing results on the same day. If you want to overwrite the existing results, you can:

```
python scripts/run_single_test.py --test_id T0001 --regenerate
```

You also can run the script without any parameters for the interactive interface. It lets you search for and select the test you might be looking for.

### 2.3. Create a new Benchmark
Start with the CLI tool to create the basic structure:

```
python scripts/create_benchmark.py
```
This creates a new dataset environment, like so:

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

#### Step-by-Step Process
When starting the `create_benchmark.py` script, you will be guided through the creation of the following data:

**1. Benchmark Name**
- Must be lowercase with underscores (e.g., `personal_letters`)
- **Important:** Should describe the SOURCE, not the task
  - Good: `personal_letters`, `company_registers`, `manuscript_pages`
  - Bad: `date_recognition`, `entity_extraction`
- **Cannot be changed later** - choose carefully!
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

#### Add Context Data
You need to add at least one image or text file. This is the context data. 
Context data are the inputs that will be sent to the LLM. Depending on the benchmark, this may include:

- .txt, .json and other text-only files (historical texts, metadata records, descriptions, OCR fragments)
- .jpg, .png or other image types (manuscript pages, document snippets, photos)

_Naming convention_:
- The whole filename without its ending is treated as context object name
- This means that all files with the same basename in the context directories (images, texts) are sent at the same time
- For each basename you must provide a ground truth file

#### Implement Scoring
Each benchmark has a corresponding benchmark class in benchmark.py. Two methods have to be implemented in order for the scoring to work:

_Implement the scoring of a single object/request:_
Implement the scoring for a single request. Most of the times it is not as easy as to ask if the llm-response and the ground truth are equal. 

```python
def score_request_answer(self, object_name, response, ground_truth):
   # object_name: basename of the processed files
   # response: large language model response
   # ground_truth: corresponding_ground_truth
   
   calculated_score = 0
   # implement scoring for one object
   
   return {"fuzzy": calculated_score}
```

_Implement the scoring of the whole test run:_
Take the average or the mean or use any other functionality to score accross all requests for the test run.

```python
def score_benchmark(self, all_scores):
       total_score = 0
       for score in all_scores:
           total_score += score['fuzzy']
       return {"fuzzy": total_score / len(all_scores)}
```

Return at least one metric. Commonly used metrics are fuzzy, f1_score, cer

#### Define Schema
If you want to implement a custom dataclass.

```python
dataclass exnmple
```

The `score_answer` method is used to score the answer from the model. The method receives the image name, the response
from the model, and the ground truth. The method should return a dictionary with the scores. The keys of the dictionary
should be the names of the evaluation criteria, and the values should be the scores.

The rest of the methods are properties that can be used to configure the behavior of the benchmark. 
The `convert_result_to_json` property indicates whether the results should be converted to JSON format.
The `resize_images` property indicates whether the images should be resized before being sent to the model.
The `get_page_part_regex` property is a regular expression that is used to extract the page part from the image name.
The `get_output_format` property indicates the output format of the model response.
The `title` property is used to generate the title of the benchmark.


### 2.4. Run an adhoc test
When you have created a benchmark you should test it first and ensure that verything works. That's what adhoc-tests are for.
Run the following command and select from the options to create an on-the-fly configuration to test.

```
python scripts/run_single_test.py --adhoc
```

The results are saved to `test_runs/` directory instead of `results/` which you can easily delete and is ignored by the repository.
Perfect for experimentation and quick testing, ID format: `ADHOC_YYYYMMDD_HHMMSS`.


### 2.5. Generate a result render

```
python scripts/create_report.py path/to/result
```


## 3. Share it!
We welcome contributions to the RISE Humanities Data Benchmark. 

### 3.1. Before submitting
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

### 3.2. Create a pull request
- Go to your fork on GitHub.
- Click “Compare & pull request”.
- Target: `RISE-UNIBAS/humanities_data_benchmark → main`

Add a short description:
- What your benchmark tests
- Example ground truth formats
- Scoring logic summary
- How you validated the dataset
- Any remaining issues or questions

### 3.3. Review & Publication
The maintainers will:

- run the benchmark locally
- check the metric
- confirm licensing
- validate folder structure
 -potentially request revisions

Once everything is green, your benchmark will be merged into the main repository.

## 4. Providers and Models

This benchmark suite currently tests models from the following providers:

| Provider | Model | Notes |
|----------|-------|-------|
| **Anthropic** | claude-3-5-sonnet-20241022 | Mid-tier Claude model with strong reasoning |
| | claude-3-7-sonnet-20250219 | Advanced Claude with improved capabilities |
| | claude-3-opus-20240229 | Highest capability Claude 3 model |
| | ~~claude-3-5-haiku-20241022~~ | ~~Fastest/smallest Claude 3.5~~ (legacy) |
| | claude-opus-4-1-20250805 | Updated Claude 4.1 Opus |
| | claude-opus-4-20250514 | Next-generation Claude 4 Opus |
| | claude-sonnet-4-20250514 | Claude 4 Sonnet |
| | claude-sonnet-4-5-20250929 | Latest Claude 4.5 Sonnet |
| **Cohere** | command-a-03-2025 | Advanced multimodal model |
| | command-a-vision-07-2025 | Vision-enabled Command A model |
| | command-r-08-2024 | Balanced performance model |
| | command-r-plus-08-2024 | Enhanced Command R with extended capabilities |
| | command-r7b-12-2024 | Compact 7B parameter model |
| **Google/Gemini** | ~~gemini-1.5-flash~~ | ~~Earlier generation flash~~ (legacy) |
| | ~~gemini-1.5-pro~~ | ~~Gemini 1.5 series~~ (legacy) |
| | gemini-2.0-flash | Fast response multimodal model |
| | gemini-2.0-flash-lite | Lighter version of 2.0-flash |
| | ~~gemini-2.0-pro-exp-02-05~~ | ~~Experimental 2.0 pro~~ (legacy) |
| | gemini-2.5-flash | Latest generation flash |
| | gemini-2.5-flash-lite | Efficient 2.5 flash |
| | gemini-2.5-flash-lite-preview-09-2025 | Preview lite flash |
| | ~~gemini-2.5-flash-preview-04-17~~ | ~~Preview flash~~ (legacy) |
| | gemini-2.5-flash-preview-09-2025 | Preview 2.5 flash |
| | gemini-2.5-pro | Production 2.5 pro |
| | ~~gemini-2.5-pro-exp-03-25~~ | ~~Experimental 2.5 pro~~ (legacy) |
| | ~~gemini-2.5-pro-preview-05-06~~ | ~~Preview 2.5 pro~~ (legacy) |
| | ~~gemini-exp-1206~~ | ~~Experimental~~ (legacy) |
| **Mistral AI** | mistral-large-latest | Most capable language model |
| | mistral-medium-2505 | Mid-tier balanced performance |
| | mistral-medium-2508 | Updated Mistral Medium |
| | pixtral-12b | 12B parameter multimodal |
| | pixtral-large-latest | Multimodal for vision tasks |
| **OpenAI** | gpt-4.1 | Latest GPT-4 iteration |
| | gpt-4.1-mini | Optimized for efficiency |
| | gpt-4.1-nano | Ultra-compact for lightweight tasks |
| | ~~gpt-4.5-preview~~ | ~~Updated GPT-4~~ (legacy) |
| | gpt-4o | Multimodal text and images |
| | gpt-4o-mini | Smaller, faster GPT-4o |
| | gpt-5 | Next-generation with advanced reasoning |
| | gpt-5-mini | Efficient GPT-5 |
| | gpt-5-nano | Compact GPT-5 |
| | o3 | Reasoning-focused model |
| **OpenRouter** | meta-llama/llama-4-maverick | Meta's Llama 4 via OpenRouter |
| | qwen/qwen3-vl-30b-a3b-instruct | Qwen3 VL 30B instruction |
| | qwen/qwen3-vl-8b-instruct | Qwen3 VL 8B instruction |
| | qwen/qwen3-vl-8b-thinking | Qwen3 VL 8B reasoning |
| | x-ai/grok-4 | xAI's Grok 4 multimodal |
| **sciCORE** | GLM-4.5V-FP8 | GLM-4.5V with FP8 quantization (University of Basel HPC) |

**Note:** OpenRouter provides access to models from multiple providers through a unified API. sciCORE provides access to models hosted on the University of Basel's high-performance computing infrastructure.


## 5. Benchmarking Methodology

### 5.1. Ground Truth
In this benchmark suite, a model's output for a task is compared to the ground truth (gold standard) for that task given the same input. Ground truth is the correct or verified output created by domain experts.

When selecting ground truth samples, we ensure:
- They are representative of the overall dataset
- They cover various edge cases and scenarios relevant to humanities tasks
- The sample size is large enough to achieve statistical significance

### 5.2. Metrics
We use two categories of metrics to evaluate model performance:

#### 5.2.1. Internal Metrics (Task Performance)
These metrics evaluate how well the model performs the specific task. Examples include:

- **F1 Score**: The harmonic mean of precision and recall, balancing both metrics
- **Precision**: The ratio of correctly predicted positive observations to all predicted positives
- **Recall**: The ratio of correctly predicted positive observations to all actual positives
- **Character/Word Error Rate**: Used for evaluating text generation and transcription accuracy

#### 5.2.2. External Metrics (Practical Considerations)
These metrics evaluate factors beyond task performance that impact usability:

- **Compute Cost**: Automatically tracked based on token usage and date-based pricing data (`scripts/data/pricing.json`). Each run includes cost breakdown and historical pricing via Wayback Machine snapshots.
  - **Cost per Performance Point**: Efficiency metric ($/performance point) calculated per test, averaged per benchmark, then globally. Uses multi-level normalization for fair comparison across different test configurations and benchmark scales.
- **Test Time**: Automatically tracked for each API call.
  - **Time per Performance Point**: Efficiency metric (seconds/point per item) using the same multi-level normalization as cost calculation for fair comparison across different item counts and benchmark complexities.
- **Deployment Options**: Whether the model can be run locally or requires API calls
- **Legal and Ethical Considerations**: Including data privacy, IP compliance, and model bias


## 6. Project Status

## 6.1. Current Limitations

The benchmark suite currently has several limitations that could be addressed in future iterations:

| Category | Limitation | Description |
|----------|------------|-------------|
| **Models** | Local/self-hosted models | Limited support for models that can be run locally |
| **Capabilities** | Domain-specific fine-tuned models | Models specifically optimized for historical research not included |
| | OCR-specialized models | Models with particular strength in document processing/OCR not included |
| | Multilingual capabilities | Systematic testing across different languages not covered |
| **Benchmark Coverage** | Limited benchmark diversity | Currently focused on document analysis; missing art history, archaeology, musicology domains |
| | Language coverage | Primarily German and English; limited coverage of other European languages and non-Western scripts |
| | Historical period coverage | Concentrated on 19th-20th century; limited medieval, early modern, or contemporary sources |
| **Evaluation** | Context window testing | Evaluation across different context window sizes and document lengths not implemented |
| | Standardized error analysis | More granular error categorization and failure mode analysis needed |

## 6.2. Outlook
TODO

## 7. Contributors

This project is developed by a multidisciplinary team at the University of Basel's RISE (Research and Infrastructure Support). 

| Name | GitHub | ORCID |
|------|-------|-------|
| Anthea Alberto | [@antheajeanne](https://github.com/antheajeanne) | [0009-0007-0430-0050](https://orcid.org/0009-0007-0430-0050) |
| Sven Burkhardt | [@Sveburk](https://github.com/Sveburk) | [0009-0001-4954-4426](https://orcid.org/0009-0001-4954-4426) |
| Eric Decker | [@edecker](https://github.com/edecker) | [0000-0003-3035-2413](https://orcid.org/0000-0003-3035-2413) |
| Pema Frick | [@pwmff](https://github.com/pwmff) | [0000-0002-8733-7161](https://orcid.org/0000-0002-8733-7161) |
| Maximilian Hindermann | [@MHindermann](https://github.com/MHindermann) | [0000-0002-9337-4655](https://orcid.org/0000-0002-9337-4655) |
| Lea Kasper | [@lekasp](https://github.com/lekasp) | [0000-0002-4671-1700](https://orcid.org/0000-0002-4671-1700) |
| José Luis Losada Palenzuela | [@editio](https://github.com/editio) | [0000-0002-6530-1328](https://orcid.org/0000-0002-6530-1328) |
| Sorin Marti | [@sorinmarti](https://github.com/sorinmarti) | [0000-0002-9541-1202](https://orcid.org/0000-0002-9541-1202) |
| Gabriel Müller | [@gbmllr1](https://github.com/gbmllr1) | [0000-0001-8320-5148](https://orcid.org/0000-0001-8320-5148) |
| Ina Serif | [@wissen-ist-acht](https://github.com/wissen-ist-acht) | [0000-0003-2419-4252](https://orcid.org/0000-0003-2419-4252) |
| Elena Spadini | [@elespdn](https://github.com/elespdn) | [0000-0002-4522-2833](https://orcid.org/0000-0002-4522-2833) |

For detailed attribution by benchmark and contribution type, see our [CONTRIBUTORS.md](CONTRIBUTORS.md) file.

From RISE with <3 








