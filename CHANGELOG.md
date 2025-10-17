# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- OpenRouter support with fallback for models not supporting structured outputs
- T0233 on 2025-10-17
- T0234 on 2025-10-17

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
- T0099 on 2025-09-24
- T0107 on 2025-09-24
- T0117 on 2025-09-24
- T0120 on 2025-09-24
- T0125 on 2025-09-24
- T0130 on 2025-09-24
- T0132 on 2025-09-24
- T0134 on 2025-09-24
- T0145 on 2025-09-24
- T0151 on 2025-09-24
- T0162 on 2025-09-24
- T0023 on 2025-09-25
- T0035 on 2025-09-25
- T0095 on 2025-09-25
- T0159 on 2025-09-25
- T0169 on 2025-09-26
- T0170 on 2025-09-26
- T0171 on 2025-09-26
- T0172 on 2025-09-26
- T0173 on 2025-09-26
- T0174 on 2025-09-26
- T0175 on 2025-09-26
- T0176 on 2025-09-26
- T0177 on 2025-09-26
- T0178 on 2025-09-26
- T0179 on 2025-09-26
- T0180 on 2025-09-26
- T0107 on 2025-09-30
- T0169 on 2025-09-30
- T0001 on 2025-09-30
- T0002 on 2025-09-30
- T0003 on 2025-09-30
- T0004 on 2025-09-30
- T0005 on 2025-09-30
- T0006 on 2025-09-30
- T0007 on 2025-09-30
- T0008 on 2025-09-30
- T0009 on 2025-09-30
- T0010 on 2025-09-30
- T0012 on 2025-09-30
- T0013 on 2025-09-30
- T0017 on 2025-09-30
- T0018 on 2025-09-30
- T0020 on 2025-09-30
- T0023 on 2025-09-30
- T0024 on 2025-09-30
- T0025 on 2025-09-30
- T0027 on 2025-09-30
- T0031 on 2025-09-30
- T0033 on 2025-09-30
- T0035 on 2025-09-30
- T0036 on 2025-09-30
- T0038 on 2025-09-30
- T0039 on 2025-09-30
- T0042 on 2025-09-30
- T0043 on 2025-09-30
- T0044 on 2025-09-30
- T0045 on 2025-09-30
- T0052 on 2025-09-30
- T0053 on 2025-09-30
- T0056 on 2025-09-30
- T0057 on 2025-09-30
- T0060 on 2025-09-30
- T0061 on 2025-09-30
- T0062 on 2025-09-30
- T0063 on 2025-09-30
- T0066 on 2025-09-30
- T0067 on 2025-09-30
- T0068 on 2025-09-30
- T0069 on 2025-09-30
- T0070 on 2025-09-30
- T0071 on 2025-09-30
- T0072 on 2025-09-30
- T0073 on 2025-09-30
- T0074 on 2025-09-30
- T0075 on 2025-09-30
- T0076 on 2025-09-30
- T0077 on 2025-09-30
- T0078 on 2025-09-30
- T0079 on 2025-09-30
- T0082 on 2025-09-30
- T0083 on 2025-09-30
- T0084 on 2025-09-30
- T0085 on 2025-09-30
- T0086 on 2025-09-30
- T0090 on 2025-09-30
- T0092 on 2025-09-30
- T0093 on 2025-09-30
- T0094 on 2025-09-30
- T0095 on 2025-09-30
- T0098 on 2025-09-30
- T0099 on 2025-09-30
- T0100 on 2025-09-30
- T0101 on 2025-09-30
- T0102 on 2025-09-30
- T0103 on 2025-09-30
- T0104 on 2025-09-30
- T0105 on 2025-09-30
- T0106 on 2025-09-30
- T0108 on 2025-09-30
- T0109 on 2025-09-30
- T0110 on 2025-09-30
- T0111 on 2025-09-30
- T0112 on 2025-09-30
- T0113 on 2025-09-30
- T0114 on 2025-09-30
- T0115 on 2025-09-30
- T0116 on 2025-09-30
- T0117 on 2025-09-30
- T0118 on 2025-09-30
- T0119 on 2025-09-30
- T0120 on 2025-09-30
- T0121 on 2025-09-30
- T0122 on 2025-09-30
- T0123 on 2025-09-30
- T0124 on 2025-09-30
- T0125 on 2025-09-30
- T0126 on 2025-09-30
- T0127 on 2025-09-30
- T0128 on 2025-09-30
- T0129 on 2025-09-30
- T0130 on 2025-09-30
- T0131 on 2025-09-30
- T0132 on 2025-09-30
- T0133 on 2025-09-30
- T0160 on 2025-09-30
- T0193 on 2025-09-30
- T0194 on 2025-09-30
- T0195 on 2025-09-30
- T0196 on 2025-09-30
- T0197 on 2025-09-30
- T0198 on 2025-09-30
- T0199 on 2025-09-30
- T0200 on 2025-09-30
- T0230 on 2025-09-30
- T0129 on 2025-10-01
- T0130 on 2025-10-01
- T0131 on 2025-10-01
- T0132 on 2025-10-01
- T0133 on 2025-10-01
- T0134 on 2025-10-01
- T0135 on 2025-10-01
- T0136 on 2025-10-01
- T0137 on 2025-10-01
- T0138 on 2025-10-01
- T0139 on 2025-10-01
- T0140 on 2025-10-01
- T0141 on 2025-10-01
- T0143 on 2025-10-01
- T0144 on 2025-10-01
- T0145 on 2025-10-01
- T0146 on 2025-10-01
- T0147 on 2025-10-01
- T0148 on 2025-10-01
- T0151 on 2025-10-01
- T0152 on 2025-10-01
- T0155 on 2025-10-01
- T0159 on 2025-10-01
- T0160 on 2025-10-01
- T0161 on 2025-10-01
- T0165 on 2025-10-01
- T0169 on 2025-10-01
- T0170 on 2025-10-01
- T0171 on 2025-10-01
- T0172 on 2025-10-01
- T0173 on 2025-10-01
- T0174 on 2025-10-01
- T0175 on 2025-10-01
- T0176 on 2025-10-01
- T0177 on 2025-10-01
- T0178 on 2025-10-01
- T0179 on 2025-10-01
- T0180 on 2025-10-01
- T0181 on 2025-10-01
- T0182 on 2025-10-01
- T0183 on 2025-10-01
- T0184 on 2025-10-01
- T0185 on 2025-10-01
- T0201 on 2025-10-01
- T0202 on 2025-10-01
- T0203 on 2025-10-01
- T0204 on 2025-10-01
- T0205 on 2025-10-01
- T0206 on 2025-10-01
- T0207 on 2025-10-01
- T0208 on 2025-10-01
- T0209 on 2025-10-01
- T0210 on 2025-10-01
- T0211 on 2025-10-01
- T0212 on 2025-10-01
- T0213 on 2025-10-01
- T0214 on 2025-10-01
- T0215 on 2025-10-01
- T0216 on 2025-10-01
- T0217 on 2025-10-01
- T0218 on 2025-10-01
- T0219 on 2025-10-01
- T0220 on 2025-10-01
- T0221 on 2025-10-01
- T0222 on 2025-10-01
- T0223 on 2025-10-01
- T0224 on 2025-10-01
- T0225 on 2025-10-01
- T0226 on 2025-10-01
- T0227 on 2025-10-01
- T0228 on 2025-10-01
- T0229 on 2025-10-01
- T0186 on 2025-10-01
- T0187 on 2025-10-01
- T0188 on 2025-10-01
- T0189 on 2025-10-01
- T0190 on 2025-10-01
- T0191 on 2025-10-01
- T0192 on 2025-10-01
- T0168 on 2025-10-01
- T0166 on 2025-10-01
- T0167 on 2025-10-01
- T0161 on 2025-10-02
- T0162 on 2025-10-02
- T0164 on 2025-10-02

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
- Radar chart top 10 models.
- Zettelkatalog benchmark.
- T0066 on 2025-09-02
- T0143 on 2025-09-02
- T0144 on 2025-09-02
- T0145 on 2025-09-02
- T0146 on 2025-09-02
- T0147 on 2025-09-02
- T0148 on 2025-09-02
- T0159 on 2025-09-02
- T0160 on 2025-09-02
- T0161 on 2025-09-02
- T0162 on 2025-09-02
- T0164 on 2025-09-02
- T0165 on 2025-09-02
- T0166 on 2025-09-02
- T0151 on 2025-09-02
- T0152 on 2025-09-02
- T0155 on 2025-09-02
- T0167 on 2025-09-02
- T0168 on 2025-09-02

## [v0.2.0] - 2025-08-31

### Added
- Global model performance leaderboard to docs.
- T0136 on 2025-08-27
- T0137 on 2025-08-27
- T0138 on 2025-08-27
- T0139 on 2025-08-27
- T0140 on 2025-08-27
- T0141 on 2025-08-27
- T0106 on 2025-08-27

### Fixed
- Broken link patterns in docs.

### Changed
- Standardize test-IDs to 4-digit zero-padded format (T0001).

## [v0.1.0] - 2025-08-25

### Added

- Changelog.

[Unreleased]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/compare/v0.2.2...HEAD
[v0.1.0]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.1.0
[v0.2.0]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.2.0
[v0.2.1]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.2.1
[v0.2.2]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.2.2
[v0.3.0]: https://github.com/RISE-UNIBAS/humanities_data_benchmark/releases/tag/v0.3.0