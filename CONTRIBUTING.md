# Contributing to the RISE Humanities Data Benchmark

We welcome contributions from the research community! This guide outlines how to participate in this project and contribute to the development of benchmarks for evaluating LLM performance on digital humanities tasks.

## Ways to Contribute

We use a structured approach to contributions based on five key roles in digital humanities benchmarking:

### 1. Domain Expert
**What it involves:** Provide subject knowledge and shape research questions
- Help define relevant task categories for humanities research
- Contribute to annotation design and interpretation of model outputs
- Point out cultural and linguistic complexities that may affect performance
- Review benchmark designs for domain relevance

### 2. Data Curator
**What it involves:** Collect, clean, and prepare high-quality datasets
- Source historical documents, images, or other humanities materials
- Clean and format data following FAIR principles (Findable, Accessible, Interoperable, Reusable)
- Handle licensing and permissions for data use
- Address potential biases in digitization, selection, and representation

### 3. Annotator
**What it involves:** Create ground truth data and reference annotations
- Develop accurate transcriptions, tags, labels, or other annotations
- Follow clear guidelines to ensure consistency across annotators
- Recognize that interpretive variation is often part of humanities tasks
- Validate existing ground truth data

### 4. Analyst
**What it involves:** Develop meaningful scoring and evaluation criteria
- Propose evaluation criteria early in the benchmark development process
- Use standard measures where appropriate (e.g., precision, recall, edit distance)
- Adapt metrics to reflect what is meaningful in specific scholarly contexts
- Analyze benchmark results and identify patterns

### 5. Engineer
**What it involves:** Implement benchmarks and build reproducible workflows
- Build and document baseline systems and reproducible workflows
- Implement scoring functions and evaluation metrics
- Support comparisons through tools like dashboards or summary reports
- Aim for accessibility across different levels of technical experience

## How to Get Started

### For New Contributors

1. **Explore existing benchmarks** - Review our [benchmark documentation](benchmarks/) to understand the current scope
2. **Identify your expertise** - Consider which of the five contribution areas align with your skills
3. **Join the conversation** - Contact us (see [Contact](#contact) section) to discuss potential contributions
4. **Start small** - Consider validating existing ground truth or reviewing benchmark designs before proposing new benchmarks

### For New Benchmark Development

If you want to create a new benchmark:

1. **Propose your idea** - Contact the team to discuss scope, feasibility, and fit with project goals
2. **Assemble a team** - Ideally include contributors covering multiple roles (domain expert, data curator, annotator, analyst, engineer)
3. **Follow our structure** - Use our [benchmark template](benchmarks/README_TEMPLATE.md) and directory structure
4. **Iterate and refine** - Work with the team to refine your benchmark based on feedback

## Create and Submit a Benchmark

This walkthrough takes a new benchmark from an empty fork to a pull request.

### 1. Fork and clone

Fork [RISE-UNIBAS/humanities_data_benchmark](https://github.com/RISE-UNIBAS/humanities_data_benchmark)
on GitHub (top-right "Fork"), then clone your fork and set up the environment as described in
[Setting Up Your Development Environment](#setting-up-your-development-environment):

```bash
git clone https://github.com/<your-username>/humanities_data_benchmark.git
cd humanities_data_benchmark
```

### 2. Scaffold the benchmark

The CLI helper creates the directory structure, `meta.json`, a working default scorer, its
tests in `tests/test_<benchmark_name>_scoring.py` and the README (a BenchmarkCard template):

```bash
python scripts/create_benchmark.py
```

It asks for a name, title, description, tags, contributors, the scoring metric, whether the
benchmark uses images, texts and a dataclass, and the default prompt, and lets you edit every
answer before it writes anything. Name the benchmark after its **source**, not the task
(`personal_letters`, not `date_recognition`), in lowercase with underscores; choose it once, as
test configurations and result paths refer to it. Tags are chosen per facet from the controlled
vocabularies in `vocabularies/` (century, document type, language, layout, script, task and
others) and can be edited later in `meta.json`.

### 3. Add the inputs

Inputs are what is sent to the model: text files (`.txt`, `.json`, …) in `texts/`, images
(`.jpg`, `.png`, …) in `images/`. The filename without its extension names the object, and all
files with the same basename are sent together in one request. Every object needs a ground
truth:

```
benchmarks/<benchmark_name>/images/       page_1.jpg  page_2.jpg  page_3.jpg
benchmarks/<benchmark_name>/texts/        page_1.txt              page_3.json
benchmarks/<benchmark_name>/ground_truths/ page_1.json page_2.json page_3.json
```

This makes three requests: `page_1` sends an image and a text file, `page_2` only an image,
`page_3` an image and a JSON file.

### 4. Write the ground truths

One file per object in `ground_truths/`, encoding the expected output exactly. A ground truth
must be manually checked, unambiguous, as complete as possible, and consistent with your
scoring logic. See also [Ground Truth Standards](#ground-truth-standards).

### 5. Implement the scoring

`benchmark.py` holds the benchmark class. Implement two methods: one scores a single
request, the other aggregates a whole run. Return at least one metric; common ones are
`fuzzy`, `f1_score` and `cer`.

```python
def score_request_answer(self, object_name, response, ground_truth):
    # object_name: basename of the processed files
    # response: the model's response; ground_truth: the matching ground truth
    calculated_score = 0
    field_scores = {}
    # compare response and ground truth for this object, recording each comparison
    field_scores["title"] = {"response": "Der Process", "ground_truth": "Der Proceß", "score": 0.8}
    return {"fuzzy": calculated_score, "field_scores": field_scores}

def score_benchmark(self, all_scores):
    return {"fuzzy": sum(s["fuzzy"] for s in all_scores) / len(all_scores)}
```

The existing benchmarks show many variants: field-level F1, fuzzy matching, character error
rate, bounding-box overlap.

Besides your metrics, record **`field_scores`**: the values you compared, keyed by your scorer's
unit (a field name, a folio reference, a matched box). The result views show your scorer's own
judgement and cannot derive it. Use `score: None` where the scorer counts rather than assigns a
similarity, and keep it JSON-serializable: it is written verbatim into the stored answer.
`score_benchmark` receives the same dicts, so read metrics by key and do not log a whole score.

Set `score_unparseable_as_miss = True` on the class, so that an answer that cannot be parsed
scores as a miss instead of dropping out of the average; `score_request_answer` must then accept
a response that is not a dict.

For structured output, define a Pydantic model in `dataclass.py` and name its class in the
`dataclass` column of `benchmarks/benchmarks_tests.csv`. Nested models are supported, and field
descriptions are passed to the provider, so use them to disambiguate fields.

The class inherits further hooks from `Benchmark` (`scripts/benchmark_base.py`):

| Method | Purpose |
|--------|---------|
| `remove_none_values()` | Whether `None` values are stripped from the response before scoring (default `True`) |
| `convert_truth_to_json()` | Whether a ground truth stored as a JSON string is parsed into an object (default `True`) |
| `resize_images()` | Whether oversized images are resized before being sent to the model (default `False`) |
| `get_title()` | Title of the benchmark as shown in the result table |
| `get_prompt_kwargs(basename, filenames)` | Values interpolated into the prompt file, e.g. file information |
| `skip_object(object_basename)` | Whether a given object is excluded from the run |

### 6. Fill in the BenchmarkCard

The benchmark's `README.md` is a [BenchmarkCard](benchmarks/README_TEMPLATE.md): every field
stays, in order, with `Not specified` where unknown. Fields marked `(generated)` come from
`meta.json` and the files. Fill in `meta.json` (including `data_type`, `source` and `license`, the licence of the source
material),
then run:

```bash
python scripts/benchmark_cards.py <benchmark_name>
```

It fills the generated fields, validates the card and writes `benchmark_card.json`.
`benchmarks/personnel_cards/README.md` is a complete example.

### 7. Test it

Add scorer tests in `tests/test_<benchmark_name>_scoring.py`, including one in which every
ground-truth file scores perfectly against itself; the integrity suite fails without them. Then
run the benchmark end to end against a model, and the test suite:

```bash
python scripts/run_single_test.py --adhoc   # prompt → responses → scoring → summary
pytest
```

### 8. Check before submitting

- **Data:** the dataset is small (recommended under 50 MB); ground truths are manually checked;
  the source material is legally usable (openly available, a clear licence, preferably open; no
  copyrighted or sensitive data); the ground truth you create is released under CC BY 4.0; every
  input has its ground truth.
- **Technical:** the benchmark runs locally without errors; the metric is defined and documented
  in the card; the scorer has tests; the directory structure follows the template; the BenchmarkCard is complete and
  `python scripts/benchmark_cards.py --check` passes.
- **Quality:** outputs are deterministic enough for a fair comparison; the benchmark fills a
  clear gap (a new task, domain or corpus); the prompt does not steer the model toward the right
  answers by over-specifying them.

### 9. Open a pull request

Push your branch to your fork and open a pull request against `RISE-UNIBAS/humanities_data_benchmark`,
branch `main`. Describe what the benchmark tests, the ground-truth format, the scoring, how you
validated the data, and any open questions. The maintainers run the benchmark, check the metric,
confirm the licence and the structure, and may ask for changes before merging.

## Technical Requirements

### Setting Up Your Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/RISE-UNIBAS/humanities_data_benchmark.git
   cd humanities_data_benchmark
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys** (if testing models)
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

### Running the Tests

The test suite lives in `tests/` and runs with pytest:

```bash
pip install pytest
pytest                      # everything
pytest -m "not integrity"   # logic & scoring tests only (fast, offline, no API keys)
pytest -m integrity         # data-integrity guards only
```

There are two kinds of tests:

- **Logic & scoring tests** exercise the scoring helpers and each benchmark's scoring logic offline — no API keys or network needed.
- **Integrity guards** (the `integrity` marker) validate the repository's data so an incomplete model or benchmark addition fails fast: every non-legacy model in `benchmarks_tests.csv` has a `pricing.json` entry with an archived source URL, an entry in `update_pricing.py`, and a README listing; every test row's prompt file exists; every benchmark object has a matching ground truth; and every BenchmarkCard README is complete and in sync with `meta.json`.

These run automatically on every push and pull request via GitHub Actions (`.github/workflows/tests.yml`), so a model or benchmark added without its pricing, prompt, or ground-truth pieces will fail CI.

### Benchmark Structure

Each benchmark must include:
- `README.md` - A BenchmarkCard, from our [template](benchmarks/README_TEMPLATE.md); run `python scripts/benchmark_cards.py <name>` to fill the generated fields and write `benchmark_card.json`
- `images/` - Source images or documents
- `prompts/` - Text prompts for the models
- `ground_truths/` - Reference answers in JSON or text format
- `benchmark.py` (optional) - Custom scoring logic
- `dataclass.py` (optional) - Structured output schemas

## Code and Data Standards

### Code Standards
- Follow existing code style and conventions
- Include clear documentation for any new functions or classes
- Test your benchmark with at least one model before submitting
- Run the test suite (`pytest`) and keep it green before submitting (see [Running the Tests](#running-the-tests))
- Use meaningful variable and function names

### Data Standards
- Follow FAIR principles for data management
- Include proper attribution and licensing information
- Ensure data quality through validation and review
- Document any preprocessing steps clearly
- Consider privacy and ethical implications of your data

### Ground Truth Standards
- Provide clear annotation guidelines
- Include multiple examples of edge cases
- Document any subjective decisions or interpretations
- Ensure consistency across annotators
- Validate ground truth through peer review when possible

## Submission Process

### For Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-benchmark`)
3. Make your changes following our standards
4. Test your benchmark thoroughly
5. Submit a pull request with clear description of changes

### For Data Contributions
1. Contact the team before collecting or preparing large datasets
2. Ensure you have proper permissions and licenses
3. Follow our data structure and documentation standards
4. Provide metadata about your dataset
5. Submit through the agreed process with the team

### For Ground Truth Contributions
1. Follow existing annotation guidelines or propose new ones
2. Include documentation of your annotation process
3. Have your work reviewed by domain experts
4. Provide inter-annotator agreement statistics if applicable
5. Submit alongside documentation of annotation decisions

## Attribution and Recognition

Contributors are recognized in our [CONTRIBUTORS.md](CONTRIBUTORS.md) file based on their specific contributions across the five roles. When contributing, please:

- Provide your ORCID identifier if available
- Specify which roles you contributed to
- Include any institutional affiliations
- Provide GitHub username for technical contributions

## Code of Conduct

We are committed to fostering an inclusive and respectful research environment:

- Be respectful and constructive in all interactions
- Acknowledge and cite others' work appropriately
- Be open to feedback and different perspectives
- Focus on what is best for the research community
- Report any unacceptable behavior to the project maintainers

## Questions and Support

### Issues, Bugs, and Feature Requests
- Check existing [GitHub issues](https://github.com/RISE-UNIBAS/humanities_data_benchmark/issues) to see if your topic has been discussed
- Create a new issue to report bugs, suggest features, or discuss improvements
- Provide detailed descriptions and steps to reproduce for bug reports
- Clearly explain the motivation and use case for feature requests

### Research Questions
- Contact the research team for discussions about scope, methodology, or domain-specific questions
- Join our research meetings (contact us for information)

### General Questions
- Use GitHub Discussions for general questions about the project
- Email the project maintainers for sensitive or private matters

## Contact

For questions about contributions, please contact:
- **Maximilian Hindermann**: [maximilian.hindermann@unibas.ch](mailto:maximilian.hindermann@unibas.ch)
- **Sorin Marti**: [sorin.marti@unibas.ch](mailto:sorin.marti@unibas.ch)

## Resources

- [Project README](README.md) - Overview of the benchmark suite
- [CONTRIBUTORS.md](CONTRIBUTORS.md) - Detailed attribution information
- [Benchmark Template](benchmarks/README_TEMPLATE.md) - Template for new benchmarks
- [DataCite Contributor Types](https://doi.org/10.14454/mzv1-5b55) - Standard contributor classification
