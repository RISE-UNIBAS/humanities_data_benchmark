#!/usr/bin/env python3
"""Pricing validation and model availability checker."""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional


def check_model_availability():
    """Check which models are available via API endpoints where possible."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'providers': {}
    }

    # Check OpenAI models (if API key available)
    try:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            client = OpenAI(api_key=api_key)
            models = client.models.list()
            openai_models = [model.id for model in models.data]
            results['providers']['openai'] = {
                'available_models': openai_models,
                'status': 'success'
            }
            print(f"✓ OpenAI: Found {len(openai_models)} models")
        else:
            results['providers']['openai'] = {
                'status': 'no_api_key',
                'message': 'OPENAI_API_KEY not found'
            }
            print("⚠ OpenAI: No API key found")
    except Exception as e:
        results['providers']['openai'] = {
            'status': 'error',
            'message': str(e)
        }
        print(f"❌ OpenAI: Error - {e}")

    # Check Google Gemini models (if API key available)
    try:
        from google import genai
        api_key = os.getenv('GENAI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if api_key:
            client = genai.Client(api_key=api_key)
            # Try to list models (this endpoint may exist)
            models_response = client.models.list()
            gemini_models = [model.name for model in models_response]
            results['providers']['genai'] = {
                'available_models': gemini_models,
                'status': 'success'
            }
            print(f"✓ Gemini: Found {len(gemini_models)} models")
        else:
            results['providers']['genai'] = {
                'status': 'no_api_key',
                'message': 'GENAI_API_KEY not found'
            }
            print("⚠ Gemini: No API key found")
    except Exception as e:
        results['providers']['genai'] = {
            'status': 'error',
            'message': str(e)
        }
        print(f"❌ Gemini: Error - {e}")

    # Check Anthropic models (no list endpoint, just test with known model)
    try:
        from anthropic import Anthropic
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            # Anthropic doesn't have a models list endpoint
            results['providers']['anthropic'] = {
                'status': 'no_list_endpoint',
                'message': 'Anthropic does not provide a models list endpoint'
            }
            print("⚠ Anthropic: No models list endpoint available")
        else:
            results['providers']['anthropic'] = {
                'status': 'no_api_key',
                'message': 'ANTHROPIC_API_KEY not found'
            }
            print("⚠ Anthropic: No API key found")
    except Exception as e:
        results['providers']['anthropic'] = {
            'status': 'error',
            'message': str(e)
        }
        print(f"❌ Anthropic: Error - {e}")

    # Check Mistral models (if API key available)
    try:
        from mistralai import Mistral
        api_key = os.getenv('MISTRAL_API_KEY')
        if api_key:
            client = Mistral(api_key=api_key)
            models = client.models.list()
            mistral_models = [model.id for model in models.data]
            results['providers']['mistral'] = {
                'available_models': mistral_models,
                'status': 'success'
            }
            print(f"✓ Mistral: Found {len(mistral_models)} models")
        else:
            results['providers']['mistral'] = {
                'status': 'no_api_key',
                'message': 'MISTRAL_API_KEY not found'
            }
            print("⚠ Mistral: No API key found")
    except Exception as e:
        results['providers']['mistral'] = {
            'status': 'error',
            'message': str(e)
        }
        print(f"❌ Mistral: Error - {e}")

    return results


def validate_pricing_coverage():
    """Check which models in our benchmarks have pricing data."""
    try:
        from simple_ai_clients import CostCalculator
    except ImportError:
        print("❌ Cannot import CostCalculator")
        return

    # Read benchmark configuration
    config_file = "../benchmarks/benchmarks_tests.csv"
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return

    import csv
    models_in_use = set()

    with open(config_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('legacy_test', 'false').lower() == 'false':
                provider = row['provider']
                model = row['model']
                models_in_use.add((provider, model))

    print(f"\nFound {len(models_in_use)} provider/model combinations in benchmarks:")

    missing_pricing = []
    available_pricing = []

    for provider, model in sorted(models_in_use):
        if CostCalculator.verify_model_availability(provider, model):
            pricing_info = CostCalculator.get_pricing_info(provider, model)
            available_pricing.append((provider, model, pricing_info))
            print(f"✓ {provider}/{model}: ${pricing_info['input_price_per_1m']:.3f}/${pricing_info['output_price_per_1m']:.3f} per 1M tokens")
        else:
            missing_pricing.append((provider, model))
            print(f"❌ {provider}/{model}: NO PRICING DATA")

    if missing_pricing:
        print(f"\n⚠ Warning: {len(missing_pricing)} models missing pricing data:")
        for provider, model in missing_pricing:
            print(f"   - {provider}/{model}")

    print(f"\n✓ {len(available_pricing)} models have pricing data")
    return {
        'models_in_use': len(models_in_use),
        'with_pricing': len(available_pricing),
        'missing_pricing': missing_pricing,
        'available_pricing': available_pricing
    }


def estimate_benchmark_costs():
    """Estimate costs for different benchmark scenarios."""
    try:
        from simple_ai_clients import CostCalculator
    except ImportError:
        print("❌ Cannot import CostCalculator")
        return

    # Typical token usage estimates for different benchmark types
    scenarios = {
        'small_text': {'input_tokens': 500, 'output_tokens': 200},
        'medium_document': {'input_tokens': 2000, 'output_tokens': 800},
        'large_image_analysis': {'input_tokens': 5000, 'output_tokens': 1500},
        'complex_reasoning': {'input_tokens': 8000, 'output_tokens': 3000}
    }

    print(f"\n{'='*60}")
    print("COST ESTIMATES PER REQUEST")
    print(f"{'='*60}")

    # Get unique providers/models from pricing data
    providers_models = []
    for provider, models in CostCalculator.PRICING.items():
        for model in models.keys():
            providers_models.append((provider, model))

    for scenario_name, tokens in scenarios.items():
        print(f"\n{scenario_name.upper()} ({tokens['input_tokens']} input + {tokens['output_tokens']} output tokens):")
        print("-" * 40)

        costs = []
        for provider, model in providers_models:
            cost = CostCalculator.calculate_cost(
                provider, model,
                tokens['input_tokens'], tokens['output_tokens']
            )
            costs.append((cost, provider, model))

        # Sort by cost
        costs.sort()

        # Show cheapest 5 and most expensive 5
        print("Cheapest options:")
        for cost, provider, model in costs[:5]:
            print(f"  ${cost:.6f} - {provider}/{model}")

        if len(costs) > 10:
            print("...")

        print("Most expensive options:")
        for cost, provider, model in costs[-5:]:
            print(f"  ${cost:.6f} - {provider}/{model}")


def generate_pricing_report():
    """Generate comprehensive pricing report."""
    print("="*80)
    print("PRICING VALIDATION REPORT")
    print("="*80)

    print("\n1. Checking model availability via APIs...")
    availability_results = check_model_availability()

    print("\n2. Validating pricing coverage for benchmark models...")
    pricing_coverage = validate_pricing_coverage()

    print("\n3. Generating cost estimates...")
    estimate_benchmark_costs()

    # Save detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'model_availability': availability_results,
        'pricing_coverage': pricing_coverage
    }

    report_file = "../pricing_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n✓ Detailed report saved to: {report_file}")

    return report


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "availability":
            check_model_availability()
        elif command == "coverage":
            validate_pricing_coverage()
        elif command == "estimates":
            estimate_benchmark_costs()
        else:
            print("Usage: python pricing_validator.py [availability|coverage|estimates]")
    else:
        generate_pricing_report()