# Contributing to the LLM Benchmark Suite for Humanities Image Data

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

### Benchmark Structure

Each benchmark must include:
- `README.md` - Description using our template
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
