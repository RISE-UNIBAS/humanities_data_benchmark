# Cost Tracking System Implementation - Session Changes

**Date:** September 28, 2025
**Session Summary:** Implemented comprehensive cost tracking with historical pricing accuracy

## Overview

This session implemented a complete cost tracking system for the benchmark suite, with the key innovation being historical pricing accuracy - each benchmark uses the pricing that was correct at the time it was run.

## 1. Initial Cost Tracking Implementation

### Files Created/Modified:
- **`scripts/simple_ai_clients.py`** - Added `CostCalculator` class
- **`scripts/benchmark_base.py`** - Added cost aggregation to benchmark results
- **`scripts/run_benchmarks.py`** - Added real-time cost logging
- **`scripts/cost_analyzer.py`** - New comprehensive cost analysis utility

### Key Features:
- Token usage extraction from all API providers (OpenAI, Anthropic, Gemini, Mistral)
- Cost calculation based on provider pricing models
- Cost storage in individual API responses and aggregated in `scoring.json`
- Real-time cost display during benchmark execution
- Comprehensive cost analysis and reporting tools

## 2. Pricing Accuracy Issues Identified

### Problem Discovered:
- GPT-5 pricing was incorrect: $50/$150 per 1M tokens → should be $1.25/$10 per 1M tokens
- T0130 result showed $0.8455 but should have been $0.0533 (93.7% overestimation)
- Need for reliable method to get current pricing data

### Root Cause:
- No programmatic pricing endpoints available from API providers
- Manual pricing data became outdated
- Costs calculated during API calls, not at scoring time

## 3. Pricing System Improvements

### Files Modified:
- **`scripts/simple_ai_clients.py`** - Updated with corrected pricing data
- **`scripts/pricing_validator.py`** - New utility for pricing validation
- **`scripts/benchmark_base.py`** - Fixed to calculate costs at scoring time

### Key Changes:
- **Corrected pricing data** with source URLs and timestamps
- **Cost calculation timing fix** - now happens when `scoring.json` is created, not during API calls
- **Pricing validation tools** to check coverage and identify missing models
- **Cost recalculation utility** to fix existing results

## 4. Historical Pricing Infrastructure (Major Feature)

### Problem Statement:
User wanted historically accurate costs - each benchmark should use pricing that was correct when it was actually run, not current pricing.

### Solution Architecture:

#### Files Created:
- **`scripts/historical_pricing_db.py`** - Core database manager
- **`scripts/pricing_db_manager.py`** - Management tools and CLI
- **`scripts/recalculate_costs.py`** - Updated for historical pricing
- **`scripts/test_historical_pricing.py`** - Demonstration/testing script

#### Database Structure:
```json
{
  "metadata": {
    "created": "2025-09-28T...",
    "version": "1.0"
  },
  "pricing_history": {
    "2025-09-01": {
      "openai": {
        "gpt-5-mini": {
          "input_price_per_1m": 0.30,
          "output_price_per_1m": 2.50,
          "source": "OpenAI pricing page",
          "added": "2025-09-28T..."
        }
      }
    }
  }
}
```

#### Key Features:
- **Date-based pricing lookup** with automatic fallback to nearest available date
- **Bulk import/export** capabilities for pricing data management
- **Validation tools** to identify missing pricing data and date gaps
- **Graceful fallback** to current pricing when historical data unavailable

## 5. Updated System Architecture

### Cost Calculation Flow:
1. **API Call** → Extract token counts, store in response
2. **Benchmark Completion** → Aggregate tokens, calculate cost using `CostCalculator.calculate_cost_for_date(benchmark_date, ...)`
3. **Historical Lookup** → Database returns pricing for specific date (or nearest available)
4. **Scoring File** → Stores final cost with historical accuracy

### Fallback Hierarchy:
1. **Exact date match** in historical database
2. **Nearest earlier date** in historical database
3. **Current pricing** from `CostCalculator.PRICING`

## 6. Management Tools

### Command Line Interface:
```bash
# Core benchmark operations
python scripts/run_benchmarks.py
python scripts/cost_analyzer.py

# Pricing validation
python scripts/pricing_validator.py
python scripts/pricing_validator.py coverage

# Historical pricing management
python scripts/pricing_db_manager.py init
python scripts/pricing_db_manager.py add 2025-09-01 openai gpt-5 1.25 10.00
python scripts/pricing_db_manager.py validate
python scripts/pricing_db_manager.py export pricing_backup.json

# Cost recalculation
python scripts/recalculate_costs.py all
python scripts/recalculate_costs.py T0130
```

## 7. Documentation Updates

### Files Modified:
- **`CLAUDE.md`** - Added all new commands and tools
- **`COST_TRACKING_CHANGES.md`** - This documentation file

## 8. Benefits Achieved

### Historical Accuracy:
- **Benchmark run on 2025-09-01** uses 2025-09-01 pricing
- **Benchmark run on 2025-09-28** uses 2025-09-28 pricing
- **Fair cost comparisons** between different time periods
- **Price change analysis** and trend tracking capabilities

### Operational Benefits:
- **Real-time cost monitoring** during benchmark execution
- **Comprehensive cost analysis** across providers, models, and time periods
- **Automated cost recalculation** for existing results
- **Pricing validation tools** to ensure data completeness

### Data Integrity:
- **Source documentation** for all pricing data
- **Timestamp tracking** for pricing updates
- **Validation utilities** to identify gaps and inconsistencies
- **Graceful error handling** with fallback mechanisms

## 9. Future Work

### User Responsibilities:
- **Populate historical pricing database** with accurate historical data
- **Regular pricing updates** as providers change rates
- **Database maintenance** and validation

### System Capabilities Ready:
- **Bulk import tools** for historical pricing data
- **API endpoint integration** when/if providers offer pricing endpoints
- **Automated validation** and gap detection
- **Export/sharing** of pricing databases

## 10. Technical Implementation Details

### Key Classes:
- **`CostCalculator`** - Core pricing and cost calculation logic
- **`HistoricalPricingDB`** - Database management and queries
- **`Benchmark`** - Updated to use historical pricing automatically

### Integration Points:
- **`benchmark_base.py:271-273`** - Historical cost calculation
- **`simple_ai_clients.py:64-88`** - Historical pricing lookup
- **`run_benchmarks.py:126-127`** - Real-time cost logging

### Data Flow:
```
API Response → Token Counts → Historical DB Lookup → Cost Calculation → scoring.json
```

## 11. Testing and Validation

### Tests Created:
- **`test_historical_pricing.py`** - Complete system test
- **`test_cost_recalc.py`** - Cost recalculation validation
- **`pricing_validator.py`** - Coverage and completeness checking

### Verified Scenarios:
- ✅ Historical pricing lookup with exact date match
- ✅ Fallback to nearest earlier date when exact match unavailable
- ✅ Graceful fallback to current pricing when no historical data
- ✅ Cost recalculation for existing results
- ✅ Bulk pricing data import/export
- ✅ Database validation and gap detection

## 12. Next Steps - Implementation Roadmap

### 12.1 Wayback Machine Integration for Historical Pricing

**Objective:** Automatically ingest historical pricing data from archived pricing pages

#### Implementation Tasks:
- **Create `wayback_pricing_scraper.py`**
  - Interface with Wayback Machine API (web.archive.org)
  - Parse archived pricing pages for each provider
  - Extract pricing data from historical snapshots
  - Handle different page formats and structures over time
  - Map pricing data to our database format

- **Provider-Specific Parsers:**
  - `parse_openai_pricing()` - Extract from archived openai.com/pricing
  - `parse_anthropic_pricing()` - Extract from archived claude.ai/pricing
  - `parse_google_pricing()` - Extract from archived cloud.google.com/vertex-ai/pricing
  - `parse_mistral_pricing()` - Extract from archived mistral.ai/pricing

- **Date Range Processing:**
  - Query available snapshots for date ranges
  - Identify pricing change points automatically
  - Fill pricing database with historical accuracy
  - Validate scraped data against known pricing changes

#### CLI Interface:
```bash
# Scrape all historical pricing for a provider
python scripts/wayback_pricing_scraper.py openai --start-date 2024-01-01 --end-date 2025-09-28

# Scrape specific dates
python scripts/wayback_pricing_scraper.py anthropic --dates 2024-06-01,2024-12-01,2025-03-01

# Auto-fill pricing gaps
python scripts/wayback_pricing_scraper.py --fill-gaps
```

### 12.2 Automated Pricing Documentation Snapshots

**Objective:** Create snapshots of pricing pages when benchmarks are run

#### Implementation Tasks:
- **Create `pricing_snapshot_manager.py`**
  - Automatically trigger when new benchmarks run
  - Capture pricing pages via Wayback Machine save API
  - Store snapshot URLs in benchmark metadata
  - Verify successful archival before continuing benchmark

- **Integration Points:**
  - Modify `benchmark_base.py` to call snapshot manager
  - Add snapshot metadata to `scoring.json` files
  - Include snapshot verification in benchmark validation

- **Snapshot Metadata Format:**
```json
{
  "pricing_snapshots": {
    "openai": {
      "snapshot_url": "https://web.archive.org/web/20250928123456/https://openai.com/pricing",
      "snapshot_date": "2025-09-28T12:34:56Z",
      "verification_status": "archived_successfully"
    }
  }
}
```

#### CLI Interface:
```bash
# Manual snapshot creation
python scripts/pricing_snapshot_manager.py create --providers openai,anthropic

# Verify existing snapshots
python scripts/pricing_snapshot_manager.py verify --date 2025-09-28

# Bulk snapshot creation for date range
python scripts/pricing_snapshot_manager.py bulk --start-date 2025-09-01 --end-date 2025-09-28
```

### 12.3 Proper Unit Test Implementation

**Objective:** Transform ad-hoc tests into comprehensive unit test suite

#### Test Structure:
```
tests/
├── __init__.py
├── test_cost_calculator.py
├── test_historical_pricing_db.py
├── test_pricing_validation.py
├── test_wayback_integration.py
├── test_benchmark_cost_integration.py
├── fixtures/
│   ├── sample_pricing_data.json
│   ├── mock_wayback_responses.json
│   └── test_scoring_files/
└── conftest.py  # pytest fixtures
```

#### Unit Tests to Implement:

**`test_cost_calculator.py`:**
- Test pricing calculations with known values
- Test historical pricing lookup with various date scenarios
- Test fallback mechanisms (exact date → nearest date → current pricing)
- Test error handling for missing providers/models
- Test pricing data validation

**`test_historical_pricing_db.py`:**
- Test database initialization and structure
- Test pricing data CRUD operations
- Test date-based queries and fallbacks
- Test bulk import/export functionality
- Test gap detection and validation
- Test database migration scenarios

**`test_pricing_validation.py`:**
- Test pricing validator against benchmark requirements
- Test model availability checking
- Test pricing completeness validation
- Test cost estimation accuracy

**`test_wayback_integration.py`:**
- Test Wayback Machine API integration
- Test pricing page parsing for each provider
- Test historical data extraction accuracy
- Test error handling for unavailable snapshots
- Mock Wayback responses for consistent testing

**`test_benchmark_cost_integration.py`:**
- Test end-to-end cost calculation in benchmark runs
- Test cost recalculation utilities
- Test historical accuracy with mock data
- Test cost aggregation and reporting

#### Testing Infrastructure:
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Run specific test categories
pytest tests/test_cost_calculator.py -v
pytest tests/ -k "historical_pricing"

# Integration tests
pytest tests/ --integration
```

#### Mock Data and Fixtures:
- **Sample pricing databases** for different scenarios
- **Mock Wayback Machine responses** for consistent testing
- **Sample benchmark results** with known cost expectations
- **Historical pricing datasets** for validation testing

### 12.4 Implementation Priority

#### Phase 1 (High Priority):
1. **Unit test implementation** - Ensure code quality and prevent regressions
2. **Wayback Machine integration** - Enable historical pricing data collection

#### Phase 2 (Medium Priority):
3. **Automated pricing snapshots** - Ensure future pricing accuracy
4. **Enhanced validation tools** - Improve data quality monitoring

#### Phase 3 (Enhancement):
- Performance optimizations for large pricing databases
- Advanced analytics and pricing trend analysis
- Integration with CI/CD for automated testing
- Documentation improvements and user guides

### 12.5 Success Criteria

#### Wayback Machine Integration:
- [ ] Successfully scrape historical pricing from major providers
- [ ] Populate pricing database with 90%+ historical coverage
- [ ] Validate scraped data accuracy against known pricing changes
- [ ] Handle parsing errors and edge cases gracefully

#### Automated Snapshots:
- [ ] Automatic snapshot creation for all benchmark runs
- [ ] 100% successful archival verification rate
- [ ] Integration with benchmark workflow without delays
- [ ] Metadata tracking for snapshot verification

#### Unit Testing:
- [ ] 95%+ code coverage for cost tracking components
- [ ] All critical paths covered with unit tests
- [ ] Mock data fixtures for consistent testing
- [ ] Integration with CI/CD pipeline
- [ ] Performance benchmarks for database operations

---

**Result:** Complete cost tracking system with historical pricing accuracy, comprehensive management tools, and robust error handling. Each benchmark now uses the pricing that was correct when it was actually run, providing historically accurate cost tracking over time.

**Next Phase:** Implementation of Wayback Machine integration, automated pricing snapshots, and comprehensive unit testing to ensure long-term accuracy and maintainability of the cost tracking system.