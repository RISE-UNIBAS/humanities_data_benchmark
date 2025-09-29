# Cost Tracking System Unit Tests

This directory contains comprehensive unit tests for the cost tracking system implemented in the humanities data benchmark project.

## Test Files

### 1. `test_pricing_database.py`
Tests the `PricingDatabase` class functionality:
- Database initialization (new and existing)
- Adding and retrieving pricing data
- Data persistence to JSON file
- Error handling for invalid data
- Global database instance management

### 2. `test_wayback_scraper.py`
Tests the `WaybackScraper` class functionality:
- Wayback Machine API integration
- Snapshot retrieval and backward date searching
- Content fetching from archived URLs
- HTML parsing for OpenAI and GenAI pricing
- Error handling for network failures

### 3. `test_cost_calculator.py`
Tests the `CostCalculator` class functionality:
- Cost calculation with cached pricing
- Wayback Machine fallback pricing
- Token cost precision calculations
- Pricing info retrieval and verification
- Model availability checking
- Error handling and edge cases

### 4. `test_benchmark_token_estimation.py`
Tests the token estimation methods in `Benchmark` class:
- Input token estimation from prompts and images
- Output token estimation from response JSON
- Image processing and resizing integration
- Error handling for missing files
- Consistency across different content sizes

## Running Tests

### Run All Tests
```bash
cd tests
python test_runner.py
```

### Run Specific Test Module
```bash
cd tests
python test_runner.py pricing_database
python test_runner.py wayback_scraper
python test_runner.py cost_calculator
python test_runner.py benchmark_token_estimation
```

### Run Individual Test Files
```bash
cd tests
python -m unittest test_pricing_database.py
python -m unittest test_wayback_scraper.py -v
```

## Test Coverage

The tests cover:
- ✅ **Happy path scenarios** - Normal operation with valid data
- ✅ **Error conditions** - Network failures, missing files, invalid data
- ✅ **Edge cases** - Empty responses, circular references, malformed JSON
- ✅ **Integration points** - Database persistence, API calls, file operations
- ✅ **Mocking external dependencies** - Network requests, file system, databases

## Dependencies

The tests use:
- `unittest` - Python standard testing framework
- `unittest.mock` - Mocking external dependencies
- `tempfile` - Creating temporary test files
- `requests` - HTTP client library (mocked in tests)

## Test Data

Tests use:
- Temporary directories for database files
- Mock HTTP responses for Wayback Machine API
- Sample HTML content for pricing parsing
- Mock image data for token estimation

## Expected Results

All tests should pass when the cost tracking system is working correctly. Failed tests indicate issues with:
- Database operations
- Network connectivity simulation
- Token calculation accuracy
- File system operations
- Error handling robustness

## Continuous Integration

These tests can be integrated into CI/CD pipelines to ensure cost tracking functionality remains stable across code changes.