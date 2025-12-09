# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.4.0] - 2025-11-23

### Added
- 4 new models: gpt-5.1 (OpenAI), gemini-3-pro-preview (GenAI), magistral-medium-2509 (Mistral), mistral-small-2506 (Mistral)
- 42 new benchmark test configurations (T0403-T0444) across all benchmarks for new models
- Pricing data for 2025-11-24 with updated model prices and source URLs
- Cohere provider support with 5 models: command-r-08-2024, command-r-plus-08-2024, command-r7b-12-2024, command-a-03-2025, command-a-vision-07-2025
- book_advert_xml benchmark for correcting malformed XML from 18th century book advertisements
- 43 new benchmark test configurations (T0445-T0487) for book_advert_xml across all providers
- Pricing data for Cohere models (2025-12-09)

### Changed
- All requests are now handled by https://pypi.org/project/generic-llm-api-client/
- Suite name is now "RISE Humanities Data Benchmark"
- Remap "latest" suffix to actual model used

### Removed
- All tests with claude-3-5-sonnet-20241022 (now legacy)
- All renders and related docs (now handled by dedicated frontend)

## [v0.3.1] - 2025-10-29

### Added
- OpenRouter provider support with fallback for models not supporting structured outputs
- sciCORE provider support (LiteLLM-based OpenAI-compatible API)
- blacklist benchmark on extracting structured company information from historical index cards
- company_lists benchmark on extracting structured company information (company name and location) from historical trade indexes
- medieval_manuscripts benchmark for 15th century page segmentation and handwritten text extraction with CER and fuzzy matching
- 6 new models: qwen/qwen3-vl-8b-thinking, qwen/qwen3-vl-30b-a3b-instruct, qwen/qwen3-vl-8b-instruct, meta-llama/llama-4-maverick, x-ai/grok-4, GLM-4.5V-FP8
- 170 new benchmark test configurations (T0233-T0402) across blacklist, medieval_manuscripts, and company_lists benchmarks
- Tests on 2025-10-03: T0164
- Tests on 2025-10-17: T0233-T0234, T0237-T0252
- Tests on 2025-10-20: T0253-T0270
- Tests on 2025-10-24: T0271-T0336
- Tests on 2025-10-28: T0336-T0402
- Update pricing data to 2025-10-28

### Fixed
- metadata_extraction scoring now correctly counts failed requests as complete failures (0 TP, all FN) instead of excluding them
- Fuzzy score matching now handles type mismatches between strings and integers (e.g., "1965" vs 1965 for year fields)
- Pricing lookup now searches through all available dates to find provider/model pricing instead of only checking the most recent date

## [v0.3.0] - 2025-10-03

### Added
- Cost tracking system with pricing database and automatic cost calculation
  - Token usage extraction for all providers (OpenAI, GenAI, Anthropic, Mistral)
  - Automatic cost calculation based on token usage and date-based pricing data
  - Cost summary in benchmark scoring files with detailed token and cost breakdowns
  - tables showing test execution costs
  - Cost per Point metric in global leaderboard showing normalized cost efficiency ($/performance point)
- 7 new models: pixtral-12b, mistral-large-latest, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-flash-lite-preview-09-2025, gemini-2.5-flash-preview-09-2025, claude-sonnet-4-5-20250929
- 50 new benchmark test configurations (T0181-T0230) for new models across all benchmark variants
- Test Time tracking and metrics
  - Test Time (s) column in benchmark tables showing total execution time per test
  - Time per Point column in benchmark tables showing time efficiency (seconds/point per item)
  - Time/Point metric in global leaderboard showing normalized time efficiency
  - Multi-level normalized calculation: per-test (average time per item / score), per-benchmark (average of test ratios), global (average of benchmark ratios)
  - Analogous to cost calculation methodology for consistency
- Structured outputs for Google Gen AI, Anthropic (native tool calling), and Mistral models
- Automatic regeneration of empty or invalid JSON result files
- Tests on 2025-09-24: T0099, T0107, T0117, T0120, T0125, T0130, T0132, T0134, T0145, T0151, T0162
- Tests on 2025-09-25: T0023, T0035, T0095, T0159
- Tests on 2025-09-26: T0169-T0180
- Tests on 2025-09-30: T0001-T0010, T0012-T0013, T0017-T0018, T0020, T0023-T0025, T0027, T0031, T0033, T0035-T0036, T0038-T0039, T0042-T0045, T0052-T0053, T0056-T0057, T0060-T0063, T0066-T0079, T0082-T0086, T0090, T0092-T0095, T0098-T0107, T0108-T0133, T0160, T0193-T0200, T0230
- Tests on 2025-10-01: T0129-T0148, T0151-T0152, T0155, T0159-T0161, T0165-T0192, T0201-T0229
- Tests on 2025-10-02: T0161-T0162, T0164

### Changed
- All provider response objects now converted to JSON-serializable format before storage
- Schema default values automatically removed for GenAI API compatibility

### Fixed
- Empty log files (FileHandler now properly configured)
- JSON serialization errors for OpenAI, GenAI, Anthropic, and Mistral response objects
- Pydantic validation errors now handled gracefully with fallback to raw tool input
- Letter dataclass normalization for list-formatted fields (letter_title, send_date)
- bibliographic_data attributions
- Pydantic dataclass models

## [v0.2.2] - 2025-09-19

### Added
- bibliographic_data README.md sections
- CONTRIBUTING.md
- CONTRIBUTORS.md

## [v0.2.1] - 2025-09-10

### Added
- Radar chart top 10 models
- Zettelkatalog benchmark
- Tests on 2025-09-02: T0066, T0143-T0148, T0151-T0152, T0155, T0159-T0162, T0164-T0168

## [v0.2.0] - 2025-08-31

### Added
- Global model performance leaderboard to docs
- Tests on 2025-08-27: T0106, T0136-T0141

### Fixed
- Broken link patterns in docs

### Changed
- Standardize test-IDs to 4-digit zero-padded format (T0001)

## [v0.1.0] - 2025-08-25

### Added
- Changelog

[Unreleased]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/compare/v0.2.2...HEAD
[v0.1.0]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.1.0
[v0.2.0]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.2.0
[v0.2.1]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.2.1
[v0.2.2]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.2.2
[v0.3.0]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.3.0
[v0.3.1]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.3.1