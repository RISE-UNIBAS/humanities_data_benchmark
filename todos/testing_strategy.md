# Testing Strategy for Humanities Data Benchmark

This document outlines the comprehensive testing strategy for the humanities data benchmark project, designed to ensure reliability, maintainability, and data integrity across all benchmark implementations. Created by Claude Code on 2025-09-16.

## Table of Contents
- [Overview](#overview)
- [Current Testing Gaps](#current-testing-gaps)
- [Testing Categories](#testing-categories)
- [Implementation Roadmap](#implementation-roadmap)
- [Testing Tools](#testing-tools)
- [Best Practices](#best-practices)

## Overview

The testing strategy addresses the specific challenges of a benchmark suite that:
- Handles diverse humanities data formats (images, JSON, text)
- Integrates with multiple AI provider APIs
- Requires consistent scoring across different domains
- Must maintain data integrity across large datasets
- Needs reproducible and deterministic results

## Current Testing Gaps

Based on project analysis, the current system lacks:
- **Unit tests** for scoring functions and core logic
- **Data validation** for ground truth integrity
- **Integration tests** for API client functionality
- **Schema validation** for dataclass definitions
- **Configuration validation** for benchmark test configurations
- **Regression tests** for score stability over time

## Testing Categories

### 1. Data Integrity & Validation Testing

#### Ground Truth Validation
Ensures all ground truth files are valid, complete, and properly formatted.

```python
def test_ground_truth_integrity():
    """Test that all ground truth files are valid and complete"""
    for benchmark in get_all_benchmarks():
        for image_file in benchmark.get_images():
            ground_truth = benchmark.load_ground_truth(image_file)
            
            # Schema validation
            assert validate_json_schema(ground_truth, benchmark.schema)
            
            # Required fields present
            assert all_required_fields_present(ground_truth)
            
            # Data type consistency
            assert validate_field_types(ground_truth)
```

**Key Tests:**
- JSON schema validation against dataclass definitions
- Required field presence validation
- Data type consistency checks
- Cross-reference validation (e.g., relation fields in bibliographic_data)
- Special character handling in multilingual content

#### Image-Ground Truth Pairing
Validates the relationship between images and their corresponding ground truth files.

```python
def test_image_ground_truth_pairing():
    """Ensure every image has corresponding ground truth"""
    for benchmark in get_all_benchmarks():
        images = set(benchmark.get_image_names())
        ground_truths = set(benchmark.get_ground_truth_names())
        
        # Every image should have ground truth
        assert images == ground_truths
        
        # Multi-page sequences properly handled
        validate_multipage_sequences(benchmark)
```

**Key Tests:**
- One-to-one image/ground truth correspondence
- Multi-page sequence validation (e.g., `image1_p1.jpg`, `image1_p2.jpg`)
- File naming convention consistency
- Missing file detection

### 2. Benchmark Implementation Testing

#### Scoring Function Tests
Validates that all scoring functions behave correctly with known inputs.

```python
def test_scoring_functions():
    """Test scoring functions with known inputs/outputs"""
    # Perfect match scenarios
    perfect_response = load_fixture("perfect_response.json")
    perfect_ground_truth = load_fixture("perfect_ground_truth.json")
    score = benchmark.score_answer("test_image", perfect_response, perfect_ground_truth)
    assert score["total"] == 1.0
    
    # Partial match scenarios
    partial_response = load_fixture("partial_response.json")
    score = benchmark.score_answer("test_image", partial_response, perfect_ground_truth)
    assert 0 < score["total"] < 1.0
    
    # Edge cases
    test_edge_cases(benchmark)
```

**Key Tests:**
- Perfect match scenarios (score = 1.0)
- Partial match scenarios (0 < score < 1.0)
- No match scenarios (score = 0.0)
- Edge cases (empty responses, malformed JSON)
- Score range validation (0 ≤ score ≤ 1)
- Fuzzy matching threshold validation

#### Dataclass Compatibility
Ensures dataclasses work correctly with API providers and serialization.

```python
def test_dataclass_serialization():
    """Test that dataclasses work correctly with API clients"""
    for benchmark in get_benchmarks_with_dataclasses():
        # Test OpenAI structured output compatibility
        if benchmark.provider == "openai":
            assert can_serialize_for_openai(benchmark.dataclass)
        
        # Test JSON schema generation
        schema = generate_schema(benchmark.dataclass)
        assert validate_schema(schema)
```

**Key Tests:**
- OpenAI structured output compatibility
- JSON schema generation from dataclasses
- Pydantic model validation
- Type hint consistency
- Optional field handling

### 3. Integration Testing

#### End-to-End Benchmark Runs
Tests complete benchmark execution with mocked API responses.

```python
def test_benchmark_execution():
    """Test complete benchmark runs with mock API responses"""
    with mock_api_client() as client:
        client.set_response("mock_response.json")
        
        benchmark = load_benchmark("test_benchmark")
        results = benchmark.run()
        
        assert results["total_tests"] > 0
        assert "scores" in results
        assert results["execution_time"] > 0
```

**Key Tests:**
- Complete benchmark execution flow
- Result format validation
- Error recovery mechanisms
- Progress tracking and logging
- Output file generation

#### API Client Testing
Validates all API client implementations with mock responses.

```python
def test_api_clients():
    """Test all API clients with mock responses"""
    providers = ["openai", "anthropic", "genai", "mistral"]
    
    for provider in providers:
        client = AiApiClient(api=provider, api_key="test_key")
        
        with mock_provider_api(provider):
            response = client.query(images=["test.jpg"], prompt="test")
            assert validate_response_format(response)
```

**Key Tests:**
- Provider-specific API implementations
- Request format validation
- Response parsing accuracy
- Error handling for API failures
- Rate limiting and retry logic

### 4. Performance & Reliability Testing

#### Cost Estimation Testing
Validates cost calculation accuracy across providers and models.

```python
def test_cost_estimation():
    """Test cost calculation accuracy"""
    benchmark = load_benchmark("metadata_extraction")
    
    # Mock token counting
    estimated_cost = benchmark.estimate_cost(
        provider="openai", 
        model="gpt-4o",
        num_images=57
    )
    
    assert estimated_cost["total_cost"] > 0
    assert estimated_cost["per_image_cost"] > 0
    assert "token_estimate" in estimated_cost
```

**Key Tests:**
- Token count estimation accuracy
- Cost calculation per provider/model
- Batch processing cost efficiency
- Historical cost tracking

#### Timeout & Error Handling
Tests graceful handling of API failures and timeouts.

```python
def test_error_handling():
    """Test graceful handling of API failures"""
    with mock_api_failure():
        benchmark = load_benchmark("test_benchmark")
        
        # Should not crash, should log errors
        results = benchmark.run()
        assert "errors" in results
        assert results["completed_tests"] >= 0
```

**Key Tests:**
- Network timeout handling
- API rate limit responses
- Invalid API key scenarios
- Malformed response handling
- Partial failure recovery

### 5. Regression Testing

#### Score Stability Tests
Ensures scoring functions produce deterministic, reproducible results.

```python
def test_score_reproducibility():
    """Ensure scoring is deterministic"""
    response = load_fixture("stable_response.json")
    ground_truth = load_fixture("stable_ground_truth.json")
    
    scores = []
    for _ in range(10):
        score = benchmark.score_answer("test", response, ground_truth)
        scores.append(score["total"])
    
    # All scores should be identical
    assert len(set(scores)) == 1
```

**Key Tests:**
- Deterministic scoring across multiple runs
- Consistent fuzzy matching behavior
- Random seed control for reproducibility
- Version compatibility for scoring algorithms

#### Configuration Validation
Validates all benchmark configurations in `benchmarks_tests.csv`.

```python
def test_benchmark_configurations():
    """Validate all test configurations in benchmarks_tests.csv"""
    configs = load_test_configurations()
    
    for config in configs:
        # Required fields present
        assert all(field in config for field in REQUIRED_CONFIG_FIELDS)
        
        # Valid provider/model combinations
        assert is_valid_provider_model(config["provider"], config["model"])
        
        # Benchmark directory exists
        assert benchmark_exists(config["name"])
        
        # Prompt file exists if specified
        if config["prompt_file"]:
            assert prompt_file_exists(config["name"], config["prompt_file"])
```

**Key Tests:**
- CSV format validation
- Required field completeness
- Provider/model combination validity
- File path resolution
- Configuration schema compliance

### 6. Property-Based Testing

#### Fuzzy Matching Properties
Tests mathematical properties of fuzzy string matching algorithms.

```python
from hypothesis import given, strategies as st

@given(
    text1=st.text(min_size=1, max_size=100),
    text2=st.text(min_size=1, max_size=100)
)
def test_fuzzy_matching_properties(text1, text2):
    """Test properties of fuzzy string matching"""
    score = fuzzy_match(text1, text2)
    
    # Score is between 0 and 1
    assert 0 <= score <= 1
    
    # Identity: text matches itself perfectly
    assert fuzzy_match(text1, text1) == 1.0
    
    # Symmetry: order doesn't matter
    assert fuzzy_match(text1, text2) == fuzzy_match(text2, text1)
```

**Key Properties:**
- Score range validation (0 ≤ score ≤ 1)
- Identity property (text matches itself perfectly)
- Symmetry property (order independence)
- Transitivity relationships
- Threshold consistency

### 7. Benchmark Quality Assurance

#### Cross-Benchmark Consistency
Tests that all benchmarks follow consistent implementation patterns.

```python
def test_benchmark_consistency():
    """Test that all benchmarks follow consistent patterns"""
    benchmarks = get_all_benchmarks()
    
    for benchmark in benchmarks:
        # Has required files
        assert has_required_files(benchmark)
        
        # README follows template
        assert validate_readme_structure(benchmark.readme_path)
        
        # Scoring returns expected format
        assert validate_scoring_format(benchmark)
        
        # Image formats supported
        assert validate_image_formats(benchmark)
```

**Key Tests:**
- Required file structure validation
- README template compliance
- Scoring interface consistency
- Image format standardization
- Documentation completeness

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
**Priority: Critical**
1. **Data validation tests** - Prevent runtime failures
2. **Basic unit tests** for core scoring functions
3. **Configuration validation** - Ensure `benchmarks_tests.csv` integrity

**Deliverables:**
- `test_data_validation.py` - Ground truth integrity tests
- `test_scoring_functions.py` - Unit tests for all scoring implementations
- `test_configurations.py` - CSV validation and benchmark existence checks

### Phase 2: Core Functionality (Week 3-4)
**Priority: High**
1. **Benchmark implementation tests** - Verify all benchmarks work correctly
2. **API client mocking** - Test without expensive API calls
3. **Schema validation** for dataclass definitions

**Deliverables:**
- `test_benchmark_implementations.py` - Tests for each benchmark class
- `test_api_clients.py` - Mocked API integration tests
- `test_dataclass_schemas.py` - Schema validation tests

### Phase 3: Integration & Reliability (Week 5-6)
**Priority: Medium**
1. **End-to-end integration tests** - Full workflow validation
2. **Error handling and timeout tests** - Robustness validation
3. **Performance regression tests** - Ensure consistent performance

**Deliverables:**
- `test_integration.py` - End-to-end workflow tests
- `test_error_handling.py` - Failure scenario tests
- `test_performance.py` - Performance and regression tests

### Phase 4: Advanced (Week 7-8)
**Priority: Low**
1. **Property-based testing** - Mathematical property validation
2. **Cross-benchmark consistency tests** - Standardization enforcement
3. **Automated cost estimation validation** - Financial accuracy tests

**Deliverables:**
- `test_properties.py` - Property-based tests using Hypothesis
- `test_consistency.py` - Cross-benchmark standardization tests
- `test_cost_estimation.py` - Cost calculation validation

## Testing Tools

### Core Testing Framework

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=scripts
    --cov=benchmarks
    --cov-report=html
    --cov-report=term-missing
    --durations=10
```

### Dependencies

```txt
# requirements-test.txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-xdist>=3.3.0  # parallel test execution
hypothesis>=6.82.0  # property-based testing
responses>=0.23.0  # HTTP request mocking
jsonschema>=4.19.0  # JSON schema validation
Pillow>=10.0.0  # image testing support
```

### Test Configuration

```python
# conftest.py
import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory"""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def temp_benchmark_dir():
    """Create temporary benchmark directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_api_responses():
    """Provide mock API responses for testing"""
    return {
        "openai": {"response": "test response", "usage": {"tokens": 100}},
        "anthropic": {"response": "test response", "usage": {"tokens": 100}},
        "genai": {"response": "test response"},
        "mistral": {"response": "test response"}
    }

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key")
    monkeypatch.setenv("GENAI_API_KEY", "test_key")
    monkeypatch.setenv("MISTRAL_API_KEY", "test_key")
```

## Best Practices

### Test Organization
- **One test file per module** being tested
- **Clear, descriptive test names** that explain what is being tested
- **Group related tests** using classes when appropriate
- **Use fixtures** to avoid code duplication

### Test Data Management
- **Store test fixtures** in `tests/fixtures/` directory
- **Use small, focused test data** that covers edge cases
- **Version control test data** alongside code
- **Document test data sources** and any licensing requirements

### Mocking Strategy
- **Mock external APIs** to avoid costs and rate limits
- **Mock file system operations** when testing file handling
- **Use dependency injection** to make mocking easier
- **Test both mocked and real scenarios** when practical

### Assertion Quality
- **Use specific assertions** rather than generic ones
- **Include error messages** in assertions for better debugging
- **Test both positive and negative cases**
- **Validate complete response structure**, not just presence

### Performance Considerations
- **Use pytest-xdist** for parallel test execution
- **Mark slow tests** with `@pytest.mark.slow`
- **Provide fast test subset** for development workflow
- **Monitor test execution time** and optimize slow tests

### Continuous Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: pytest --cov --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

This comprehensive testing strategy will significantly improve the reliability, maintainability, and trustworthiness of the humanities data benchmark project while ensuring consistent quality across all benchmark implementations.