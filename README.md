
# LLM Benchmark Suite for Humanities Image Data

[![DOI](https://zenodo.org/badge/938016958.svg)](https://doi.org/10.5281/zenodo.16941752)

This repository contains benchmark datasets (images), prompts, ground truths, and evaluation scripts for
assessing the performance of large language models (LLMs) on humanities-related tasks. The suite is
designed as a resource for researchers and practitioners interested in systematically evaluating
how well various LLMs perform on digital humanities (DH) tasks involving visual materials.

> **ℹ Looking for benchmark results?**     
> This README provides an overview of the benchmark suite and explains how to use it.  
> For detailed test results and model comparisons, visit our [results dashboard](https://rise-unibas.github.io/humanities_data_benchmark/).

## What is Benchmarking and Why Should You Care?

Benchmarking is the process of systematically evaluating and ranking various models for specific tasks using well-defined ground truths and metrics. For humanities research, benchmarking provides:

- **Evidence-based decision making** about which model(s) to use for which humanities-specific task(s)
- **Quantifiable comparisons** between different AI models on humanities data
- **Standardized evaluation** of model performance on tasks like historical document analysis, transcription, and metadata extraction

This benchmark suite focuses on tasks essential to digital humanities work with visual materials, helping researchers make informed choices about which AI systems best suit their specific research needs.

> **ℹ Looking for more background?**  
> For a deeper introduction to AI benchmarking in humanities contexts, see:  
> Hindermann, M., & Marti, S. (2025, March 19). *RISE Crash Course: "AI Benchmarking"*. Zenodo. https://doi.org/10.5281/zenodo.15062831

## Table of Contents
- [Terminology](#terminology)
- [How it Works](#how-it-works)
- [Available Benchmarks](#available-benchmarks)
- [Expand on this Benchmark Suite](#expand-on-this-benchmark-suite)
  - [Create a new benchmark](#create-a-new-benchmark)
  - [API Keys](#api-keys)
  - [Run a Benchmark](#run-a-benchmark)
  - [Add Configuration to the Suite](#add-configuration-to-the-suite)
  - [Implement a Benchmark Class](#implement-a-benchmark-class)
- [Providers and Models](#providers-and-models)
- [Benchmarking Methodology](#benchmarking-methodology)
  - [Ground Truth](#ground-truth)
  - [Metrics](#metrics)
    - [Internal Metrics](#internal-metrics-task-performance)
    - [External Metrics](#external-metrics-practical-considerations)
- [Current Limitations](#current-limitations)
  - [Additional Models](#additional-models)
  - [Specialized Capabilities](#specialized-capabilities)
  - [Benchmark Dimensions](#benchmark-dimensions)
  - [Other Areas for Improvement](#other-areas-for-improvement)
- [Practical Considerations](#practical-considerations)
  - [Resource Requirements](#resource-requirements)
  - [Technical Considerations](#technical-considerations)
  - [Compliance Considerations](#compliance-considerations)
- [Contributors](#contributors)

## Terminology
- **Benchmark**: A benchmark is a task that the model should perform. Its resources consist of images and their ground truths, prompts, 
dataclasses and a scoring function. A benchmark can be used as the basis for a **test**. Each benchmark is stored in a separate directory.
- **Prompt**: A prompt is a text that is given to the model to guide its response. All prompts are stored in the `prompts` directory of the benchmark.
- **Ground Truth**: The ground truth is the correct answer to the task. It is used to evaluate the model's response. For each image, there is a ground 
truth file with the same base name.
- **Image**: An image is a visual representation of the task. The model should use the image to generate its response. Images are stored in the `images` 
directory of the benchmark.
- **Provider**: The provider is the company that provides the model. The provider can be `openai`, `genai`, `anthropic`, or `mistral`.
- **Model**: The model is the specific model that is used to perform the task. The model can be any model that is supported by the 
provider.
- **Scoring Function**: The scoring function is a function that is used to evaluate the model's response. 
It must be provided by overriding the `score_answer` method in the benchmark class.
- **Dataclass**: The use of Pydantic models (structured data schemas) for expected output is now supported across multiple providers.
OpenAI, Google GenAI, and Anthropic (via instructor) all support structured output using Pydantic BaseModel classes.
- **Test**: A test is a specific instance of a benchmark. A test is run with a configuration which indicates the provider, model, 
temperature, role description, prompt file and dataclass.
- **Test Configuration**: A test configuration is a set of parameters that are used to run a test. 
This suite uses a `benchmarks_tests.csv` file to store the test configurations.  
- **Request**: A benchmark test will trigger requests to the provider's API. The request consists of one or multiple images 
and a prompt. The model will generate a response based on the request. At least one, but usually multiple requests are made for each test.
- **Response**: The response is the model's answer to the task. It is a json object that contains metadata and the model's output.
- **Score**: The score is the result of the evaluation. It indicates how well the model performed on the task.


## How it Works

1. **Load Test Configuration**
2. **Load Data from Benchmark configuration**
3. **Create Benchmark class instance**
4. **Run Benchmark Tests**
   - **Create Request JSON Results**
   - **Create Request Renders**
   - **Create Request Scores**
   - **Create Benchmark Scores**
   - **Create Benchmark Result Documentation**

<img src="benchmark_run.png" alt="Test Results" width="80%">

## Available Benchmarks

This benchmark suite currently includes the following benchmarks for evaluating LLM performance on humanities tasks:

### Bibliographic Data
Evaluates models' ability to extract bibliographic information from historical documents such as publication details, authors, dates, and other metadata from digitized sources.

📁 [View benchmark details](benchmarks/bibliographic_data/)

### Metadata Extraction
Tests models on extracting structured metadata from historical correspondence, including person names, organizations, dates, locations, and other contextual information from 20th century Swiss historical letters.

📁 [View benchmark details](benchmarks/metadata_extraction/)

### Fraktur Text Recognition
Assesses models' capability to recognize and transcribe historical German Fraktur script, a Gothic typeface commonly used in German-language documents from the 16th to 20th centuries.

📁 [View benchmark details](benchmarks/fraktur/)

### Zettelkatalog
A comprehensive benchmark focused on catalog card analysis and information extraction from historical library catalog systems. This benchmark evaluates models on structured data extraction from digitized catalog cards, testing their ability to parse complex bibliographic information, author names, dates, and hierarchical catalog structures from historical Swiss library records.

📁 [View benchmark details](benchmarks/zettelkatalog/)

### Test Benchmarks
Two simple test benchmarks (`test_benchmark` and `test_benchmark2`) used for system validation and basic functionality testing.

📁 [test_benchmark](benchmarks/test_benchmark/) | 📁 [test_benchmark2](benchmarks/test_benchmark2/)

## Expand on this Benchmark Suite

The benchmark suite is designed to be extensible and welcomes contributions from the digital humanities community. Whether you're adding new benchmarks, improving existing ones, or enhancing the evaluation framework, your contributions help advance AI evaluation for humanities research. For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Create a new benchmark
To create a new benchmark, follow these steps:

- Create a new directory in the `benchmarks` folder with the name of the benchmark. 
The directory should have the following structure:

```bash
.
├── benchmarks
│   ├── <new_benchmark_name>
│   │   ├── README.md
│   │   ├── benchmark.py (optional)
│   │   ├── dataclass.py (optional - defines Pydantic models for structured output)
│   │   ├── images
│   │   │   ├── image1.(jpg|png)
│   │   │   ├── image2.(jpg|png)
│   │   │   ├── ...
│   │   ├── prompts
│   │   │   ├── prompt1.txt
│   │   │   ├── prompt2.txt
│   │   │   ├── ...
│   │   ├── ground_truths
│   │   │   ├── image1.(json|txt)
│   │   │   ├── image2.(json|txt)
│   │   │   ├── ...
├── results
```

- Create a `README.md` file with a description of the benchmark by adapting the [`README_TEMPLATE.md`](benchmarks/README_TEMPLATE.md) file. Make sure to include a dataset description
and a description of the task that the model should perform. Explain your evaluation criteria and how the
results are scored. 
- Add images to the `/benchmarks/images` directory. You need at least one image. Per default, one image is used with one request.
If you want to use multiple images for one prompt, format the image names like this: `image1_p1.jpg`, `image1_p2.jpg`, etc. 
This will automatically add multiple images to the same prompt. The ground truth file for this image sequence must be 
named like so: `image1.(txt|json)`.
- Add at least one prompt to the `/benchmarks/prompts` directory. This is a simple text file with the prompt for the model.
- Add the ground truth for each image (or image sequence) to the `/benchmarks/ground_truths` directory.
- (Optional) Create a `dataclass.py` file if you want structured output. This file should contain Pydantic BaseModel classes that define the expected structure of the model's response.
- The results are generated by the model and saved in the `/results` directory. The results are saved in a JSON file

This setup will enable you to add configurations to the `benchmarks_tests.csv` file and run the benchmark with different
LLMs, prompts, and configurations.

### API Keys
To use the benchmark suite, you need to provide API keys for the different providers.
- Create a `.env` file in the root directory of the repository.
- Add the following lines to the `.env` file:

```bash
OPENAI_API_KEY=<your_openai_api_key>
GENAI_API_KEY=<your_genai_api_key>
ANTHROPIC_API_KEY=<your_anthropic_api_key>
MISTRAL_API_KEY=<your_mistral_api_key>
```

### Run a Benchmark Test
To run the suite of tests, you can use the `scripts/run_benchmarks.py` script. This script will run all the tests in the `benchmarks_tests.csv` file.

You also can use the command line interface to run a single test. For example:

```bash
python scripts/dhbm.py --name "folder_name" --provider "anthropic" --model "claude-3-7-sonnet-20250219" \
--role_description "A useful assistant." --prompt_file "prompt.txt" --api_key "your-api-key"
```

To run a test with a specific date (for re-generating renders for that date):

```bash
python scripts/dhbm.py --name "folder_name" --provider "anthropic" --model "claude-3-7-sonnet-20250219" \
--role_description "A useful assistant." --prompt_file "prompt.txt" --date "2025-03-01"
```

Alternatively, you can provide the configuration as a json file:

```bash
python scripts/dhbm.py --config test_config.json --api_key "your-api-key"
```
Instead of providing the api key as a command line argument, you can also set it in the `.env` file.

To run a specific test ID from the benchmarks_tests.csv file:

```python
# In scripts/run_benchmarks.py
from scripts.run_benchmarks import main
main(limit_to=["T0017"])  # Run only the T0017 test
main(limit_to=["T0010", "T0011"], dates=["2025-03-01", "2025-04-01"])  # Run T0010 and T0011 for specific dates
```

### Add Configuration to the Suite
To add a configuration, you need to add a new row to the `benchmarks_tests.csv` file. The file has the following structure:

```csv
id,name,provider,model,dataclass,temperature,role_description,prompt_file,rules,legacy_test
T0001,test_benchmark,openai,gpt-4o,,,,,,false
```

- `id`: A unique identifier for the benchmark using 4-digit zero-padded format (e.g., T0001, T0002).
- `name`: The name of the benchmark. This must match the name of the directory in the `benchmarks` folder.
- `provider`: The provider of the model. This can be `openai`, `genai`, `anthropic`, or `mistral`.
- `model`: The name of the model. This can be any model name that is supported by the provider.
- `dataclass`: The Pydantic model class name (from dataclass.py) used to structure the response of the request.
- `temperature`: The temperature parameter for the model. This can be any value between 0 and 1.
- `role_description`: A description of the role that the model should take on. This can be any description that is supported by the provider.
- `prompt_file`: The name of the prompt file in the `prompts` directory.
- `rules`: Additional configuration rules in JSON format for specialized test scenarios.
- `legacy_test`: A boolean value that indicates whether the benchmark is a legacy test. This can be `true` or `false`.

This allows you to run the benchmark with different models, prompts, and configurations.

### Implement a Benchmark Class
If you want to implement a custom benchmark class, you can create a `benchmark.py` file in the benchmark directory.
This file must contain a class that inherits from the `Benchmark` class. The class must be named like the benchmark 
folder but in CamelCase. Example: `TestBenchmark` for the `test_benchmark` folder.

The class can implement the following methods:

```python
from scripts.benchmark_base import Benchmark

class TestBenchmark(Benchmark):

    def score_answer(self, image_name, response, ground_truth):
        data = self.prepare_scoring_data(response)  # Extracts the relevant data from the response and returns a dictionary
        # [...] Score the answer from the model
        return {"total": 0} # Return a dictionary with scores   
        
    @property
    def convert_result_to_json(self):
        return True

    @property
    def resize_images(self):
        return True

    @property
    def get_page_part_regex(self):
        return r'(.+)_p\d+\.(jpg|jpeg|png)$'

    @property
    def get_output_format(self):
        return "json"
    
    @property
    def title(self):
        return f"{self.name} ({self.provider}/{self.model})"
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

## Providers and Models

This benchmark suite currently tests models from the following providers:

### OpenAI
- **gpt-4o**: OpenAI's multimodal model capable of processing both text and images
- **gpt-4.5-preview**: An updated version of GPT-4 with improved capabilities
- **gpt-4o-mini**: A smaller, faster version of GPT-4o with reduced capabilities
- **gpt-4.1**: Latest GPT-4 iteration with enhanced capabilities
- **gpt-4.1-mini**: Smaller version of GPT-4.1 optimized for efficiency
- **gpt-4.1-nano**: Ultra-compact version of GPT-4.1 for lightweight tasks
- **gpt-5**: OpenAI's next-generation model with advanced reasoning capabilities
- **gpt-5-mini**: Efficient version of GPT-5 with reduced resource requirements
- **gpt-5-nano**: Compact version of GPT-5 optimized for speed
- **o3**: OpenAI's reasoning-focused model for complex problem-solving tasks

### Google/Gemini
- **gemini-2.0-flash**: Fast response multimodal model from Google's Gemini line
- **gemini-2.0-flash-lite**: A lighter version of gemini-2.0-flash
- **gemini-exp-1206**: An experimental Gemini model
- **gemini-1.5-flash**: Earlier generation of the Gemini flash model
- **gemini-1.5-pro**: Higher capability model from the Gemini 1.5 series
- **gemini-2.0-pro-exp-02-05**: Experimental model from the Gemini 2.0 pro line
- **gemini-2.5-pro-exp-03-25**: Latest experimental Gemini model in the benchmark suite
- **gemini-2.5-pro**: Production version of the Gemini 2.5 pro model
- **gemini-2.5-flash-preview-04-17**: Preview version of Gemini 2.5 flash model
- **gemini-2.5-pro-preview-05-06**: Preview version of Gemini 2.5 pro model

### Anthropic
- **claude-3-5-sonnet-20241022**: Mid-tier Claude model with strong reasoning capabilities
- **claude-3-7-sonnet-20250219**: More advanced Claude model with improved capabilities
- **claude-3-opus-20240229**: Anthropic's highest capability Claude 3 model
- **claude-3-5-haiku-20241022**: Anthropic's fastest/smallest Claude 3.5 model
- **claude-opus-4-20250514**: Next-generation Claude 4 Opus with enhanced capabilities
- **claude-sonnet-4-20250514**: Claude 4 Sonnet with improved reasoning and efficiency
- **claude-opus-4-1-20250805**: Updated Claude 4.1 Opus with latest improvements

### Mistral AI
- **pixtral-large-latest**: Mistral's multimodal model for vision tasks

## Benchmarking Methodology

### Ground Truth
In this benchmark suite, a model's output for a task is compared to the ground truth (gold standard) for that task given the same input. Ground truth is the correct or verified output created by domain experts.

When selecting ground truth samples, we ensure:
- They are representative of the overall dataset
- They cover various edge cases and scenarios relevant to humanities tasks
- The sample size is large enough to achieve statistical significance

### Metrics
We use two categories of metrics to evaluate model performance:

#### Internal Metrics (Task Performance)
These metrics evaluate how well the model performs the specific task. Examples include:

- **F1 Score**: The harmonic mean of precision and recall, balancing both metrics
- **Precision**: The ratio of correctly predicted positive observations to all predicted positives
- **Recall**: The ratio of correctly predicted positive observations to all actual positives
- **Character/Word Error Rate**: Used for evaluating text generation and transcription accuracy

#### External Metrics (Practical Considerations)
These metrics evaluate factors beyond task performance that impact usability:

- **Compute Cost**: The financial cost of running the model on humanities-scale datasets
- **Speed**: Response time and throughput for processing humanities materials
- **Deployment Options**: Whether the model can be run locally or requires API calls
- **Legal and Ethical Considerations**: Including data privacy, IP compliance, and model bias

## Current Limitations

The benchmark suite currently has several limitations that could be addressed in future iterations:

### Additional Models
Several important model families are not yet included:
- **Meta/Llama models**: The entire Llama model family is absent (Llama 3/4 series)
- **Additional Mistral models**: Only Pixtral is represented, missing other Mistral models like Mistral Large
- **Cohere Command models**: Entirely absent from the benchmark
- **Various open-source models**: Falcon, Mixtral, and other open-source alternatives
- **Local/self-hosted models**: Limited support for models that can be run locally

### Specialized Capabilities
- **Domain-specific fine-tuned models**: Models specifically optimized for historical research
- **OCR-specialized models**: Models with particular strength in document processing/OCR
- **Multilingual capabilities**: Systematic testing across different languages

### Benchmark Coverage
- **Limited benchmark diversity**: Currently focused on document analysis tasks; missing benchmarks for other humanities domains like art history, archaeology, or musicology
- **Language coverage**: Primarily focused on German and English materials; limited coverage of other European languages and non-Western scripts
- **Historical period coverage**: Concentrated on 19th-20th century materials; limited representation of medieval, early modern, or contemporary sources

### Evaluation Metrics
- **Cost efficiency**: Performance evaluation relative to token cost and processing time
- **Speed metrics**: Systematic response time measurements across different model sizes
- **Context window testing**: Evaluation across different context window sizes and document lengths
- **Standardized error analysis**: More granular error categorization and failure mode analysis

## Practical Considerations

When using this benchmark suite for your own research, consider the following:

### Resource Requirements
- **Skills**: Operationalizing tasks requires both domain knowledge and technical expertise
- **Ground Truth Creation**: Requires domain expertise and careful curation
- **Metric Selection**: Requires understanding of both the humanities domain and evaluation methods

### Technical Considerations
- **Local vs. API Models**: Determine if you need to run models locally or can use API services
- **Data Privacy**: Ensure you're allowed to share your data via APIs if needed
- **Infrastructure**: Consider if you have access to appropriate computing resources

### Compliance Considerations
- **Legal Requirements**: Check for any legal restrictions on data sharing or model usage
- **Ethical Guidelines**: Consider any ethical implications of your benchmarking approach
- **Funder Requirements**: Verify if there are any funding agency requirements
- **FAIR Data Principles**: Consider how to make your benchmark data Findable, Accessible, Interoperable, and Reusable

## Contributors

This project is developed by a multidisciplinary team at the University of Basel's RISE (Research and Infrastructure Support). 

| Name | GitHub | ORCID |
|------|--------|-------|
| Anthea Alberto | [@antheajeanne](https://github.com/antheajeanne) | [0009-0007-0430-0050](https://orcid.org/0009-0007-0430-0050) |
| Sven Burkhardt | [@Sveburk](https://github.com/Sveburk) | [0009-0001-4954-4426](https://orcid.org/0009-0001-4954-4426) |
| Eric Decker | [@edecker](https://github.com/edecker) | [0000-0003-3035-2413](https://orcid.org/0000-0003-3035-2413) |
| Pema Frick | - | [0000-0002-8733-7161](https://orcid.org/0000-0002-8733-7161) |
| Maximilian Hindermann | [@MHindermann](https://github.com/MHindermann) | [0000-0002-9337-4655](https://orcid.org/0000-0002-9337-4655) |
| Lea Kasper | [@lekasp](https://github.com/lekasp) | [0000-0002-4671-1700](https://orcid.org/0000-0002-4671-1700) |
| José Luis Losada Palenzuela | [@editio](https://github.com/editio) | [0000-0002-6530-1328](https://orcid.org/0000-0002-6530-1328) |
| Sorin Marti | [@sorinmarti](https://github.com/sorinmarti) | [0000-0002-9541-1202](https://orcid.org/0000-0002-9541-1202) |
| Gabriel Müller | [@gbmllr1](https://github.com/gbmllr1) | [0000-0001-8320-5148](https://orcid.org/0000-0001-8320-5148) |
| Ina Serif | [@wissen-ist-acht](https://github.com/wissen-ist-acht) | [0000-0003-2419-4252](https://orcid.org/0000-0003-2419-4252) |
| Elena Spadini | [@elespdn](https://github.com/elespdn) | [0000-0002-4522-2833](https://orcid.org/0000-0002-4522-2833) |

For detailed attribution by benchmark and contribution type, see our [CONTRIBUTORS.md](CONTRIBUTORS.md) file.
