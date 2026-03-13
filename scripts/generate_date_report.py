#!/usr/bin/env python3
"""
Generate a report for all tests run on a specific date or date range.
Usage: python scripts/generate_date_report.py --date 2025-03-05 --format html
       python scripts/generate_date_report.py --start-date 2025-03-01 --end-date 2025-03-05 --format both
       python scripts/generate_date_report.py --date 2025-03-05 --format both --no-warnings
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import csv


def load_test_metadata():
    """Load test metadata from benchmarks_tests.csv"""
    csv_path = Path(__file__).parent.parent / "benchmarks" / "benchmarks_tests.csv"
    tests = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tests[row['id']] = {
                'name': row['name'],
                'provider': row['provider'],
                'model': row['model'],
                'dataclass': row['dataclass'],
                'temperature': row['temperature'],
            }
    return tests


def get_date_range(start_date_str, end_date_str):
    """Generate list of dates between start_date and end_date (inclusive)"""
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")

    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return dates


def detect_warnings(result):
    """Detect potential issues with test results."""
    warnings = []

    # Skip warnings for test benchmarks (test_ prefix)
    benchmark_name = result.get('name', '')
    if benchmark_name.startswith('test_'):
        return warnings

    # Warning 1: Zero cost
    if result['total_cost'] == 0:
        warnings.append({
            'code': 'ZERO_COST',
            'severity': 'high',
            'message': 'Total cost is $0 (pricing issue)'
        })

    # Warning 2: All metrics are N/A
    f1_macro = result['f1_macro']
    f1_micro = result['f1_micro']
    fuzzy = result['fuzzy']
    cer = result['cer']

    if (f1_macro == 'N/A' and f1_micro == 'N/A' and
        fuzzy == 'N/A' and cer == 'N/A'):
        warnings.append({
            'code': 'ALL_NA',
            'severity': 'critical',
            'message': 'All metrics are N/A (scoring failed)'
        })

    # Warning 3: Exactly one of macro/micro/fuzzy is 0
    metrics = [f1_macro, f1_micro, fuzzy]
    zero_count = sum(1 for m in metrics if m != 'N/A' and m == 0.0)

    if zero_count == 1:
        warnings.append({
            'code': 'ZERO_SCORE',
            'severity': 'medium',
            'message': 'Score is 0 (exceptionally bad performance)'
        })

    # Warning 4: Zero items processed
    if result['items_count'] == 0:
        warnings.append({
            'code': 'ZERO_ITEMS',
            'severity': 'critical',
            'message': 'No items processed'
        })

    # Warning 5: Zero duration
    if result['total_duration'] == 0:
        warnings.append({
            'code': 'ZERO_DURATION',
            'severity': 'high',
            'message': 'No timing captured'
        })

    return warnings


def analyze_test_results(results_dir, test_id, date=None):
    """Analyze results for a specific test"""
    test_dir = results_dir / test_id
    if not test_dir.exists():
        return None

    # Load scoring data
    scoring_file = test_dir / "scoring.json"
    scoring = {}
    if scoring_file.exists():
        with open(scoring_file, 'r') as f:
            scoring = json.load(f)

    # Analyze request files
    request_files = list(test_dir.glob("request_*.json"))
    items_count = len(request_files)

    durations = []
    providers = set()
    models = set()

    for req_file in request_files:
        with open(req_file, 'r') as f:
            data = json.load(f)
            if 'duration' in data:
                durations.append(data['duration'])
            if 'provider' in data:
                providers.add(data['provider'])
            if 'model' in data:
                models.add(data['model'])

    avg_duration = sum(durations) / len(durations) if durations else 0
    total_duration = sum(durations) if durations else 0

    # Extract cost information from cost_summary in scoring.json
    cost_summary = scoring.get('cost_summary', {})
    total_input_cost = cost_summary.get('input_cost_usd', 0.0)
    total_output_cost = cost_summary.get('output_cost_usd', 0.0)
    total_cost = cost_summary.get('total_cost_usd', 0.0)

    result = {
        'test_id': test_id,
        'date': date,
        'items_count': items_count,
        'f1_macro': scoring.get('f1_macro', 'N/A'),
        'f1_micro': scoring.get('f1_micro', 'N/A'),
        'fuzzy': scoring.get('fuzzy', 'N/A'),
        'cer': scoring.get('cer', 'N/A'),
        'avg_duration': avg_duration,
        'total_duration': total_duration,
        'input_cost': total_input_cost,
        'output_cost': total_output_cost,
        'total_cost': total_cost,
        'providers': list(providers),
        'models': list(models),
    }

    # Note: warnings will be detected after metadata is added in generate_*_report functions

    return result


def generate_html_report(dates, base_dir, test_metadata, output_file):
    """Generate HTML report"""

    # Collect all test results from all dates
    test_results = []
    total_folders = 0

    for date in dates:
        results_dir = base_dir / "results" / date
        if not results_dir.exists():
            print(f"  ⚠️  Skipping {date} (no results found)")
            continue

        # Collect all test folders for this date
        test_dirs = sorted([d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith('T')])
        total_tests = len(test_dirs)
        total_folders += total_tests
        print(f"  Found {total_tests} tests for {date}")

        # Analyze each test
        for idx, test_dir in enumerate(test_dirs, 1):
            test_id = test_dir.name
            result = analyze_test_results(results_dir, test_id, date)
            if result:
                # Add metadata
                if test_id in test_metadata:
                    result.update(test_metadata[test_id])
                # Detect warnings after metadata is available
                result['warnings'] = detect_warnings(result)
                test_results.append(result)

    print(f"  Total: {len(test_results)} tests analyzed across {len(dates)} date(s)")

    # Sort by date, then by test ID
    test_results.sort(key=lambda x: (x['date'], x['test_id']))

    # Generate title based on single date or date range
    if len(dates) == 1:
        title = f"Test Results - {dates[0]}"
    else:
        title = f"Test Results - {dates[0]} to {dates[-1]}"

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        th:hover {{
            background: #0056b3;
        }}
        th.sortable:after {{
            content: ' ⇅';
            opacity: 0.3;
            font-size: 0.8em;
        }}
        th.sort-asc:after {{
            content: ' ↑';
            opacity: 1;
        }}
        th.sort-desc:after {{
            content: ' ↓';
            opacity: 1;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .score {{
            font-weight: bold;
        }}
        .score.high {{ color: #28a745; }}
        .score.medium {{ color: #ffc107; }}
        .score.low {{ color: #dc3545; }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .badge-provider {{
            background: #e7f3ff;
            color: #004085;
        }}
        .badge-model {{
            background: #fff3cd;
            color: #856404;
        }}
        .benchmark-name {{
            font-weight: 600;
            color: #333;
        }}
        .duration {{
            color: #666;
            font-size: 0.9em;
        }}
        .warnings {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }}
        .warning-badge {{
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.75em;
            font-weight: 600;
            white-space: nowrap;
            cursor: help;
        }}
        .warning-critical {{
            background: #dc3545;
            color: white;
        }}
        .warning-high {{
            background: #fd7e14;
            color: white;
        }}
        .warning-medium {{
            background: #ffc107;
            color: #000;
        }}
        .warning-none {{
            color: #28a745;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>📊 {title}</h1>

    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-value">{len(dates)}</div>
                <div class="stat-label">Date(s)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(test_results)}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(r['items_count'] for r in test_results)}</div>
                <div class="stat-label">Total Items Tested</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(set(r.get('name', 'Unknown') for r in test_results))}</div>
                <div class="stat-label">Unique Benchmarks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(r['total_duration'] for r in test_results):.1f}s</div>
                <div class="stat-label">Total Duration</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${sum(r['total_cost'] for r in test_results):.6f}</div>
                <div class="stat-label">Total Cost (USD)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(1 for r in test_results if r.get('warnings', []))}</div>
                <div class="stat-label">Tests with Warnings</div>
            </div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Test ID</th>
                <th>Benchmark</th>
                <th>Provider</th>
                <th>Model</th>
                <th>Items</th>
                <th>F1 Macro</th>
                <th>F1 Micro</th>
                <th>Fuzzy</th>
                <th>CER</th>
                <th>Avg Duration</th>
                <th>Total Duration</th>
                <th>Input Cost ($)</th>
                <th>Output Cost ($)</th>
                <th>Total Cost ($)</th>
                <th>Warnings</th>
            </tr>
        </thead>
        <tbody>
"""

    for result in test_results:
        f1_macro = result['f1_macro']
        f1_micro = result['f1_micro']
        fuzzy = result['fuzzy']
        cer = result['cer']

        # Determine score class
        def get_score_class(score):
            if score == 'N/A':
                return ''
            if score >= 0.8:
                return 'high'
            elif score >= 0.5:
                return 'medium'
            else:
                return 'low'

        # For CER, lower is better, so invert the logic
        def get_cer_class(score):
            if score == 'N/A':
                return ''
            if score <= 0.2:
                return 'high'  # Good (low error)
            elif score <= 0.5:
                return 'medium'
            else:
                return 'low'  # Bad (high error)

        f1_macro_class = get_score_class(f1_macro) if f1_macro != 'N/A' else ''
        f1_micro_class = get_score_class(f1_micro) if f1_micro != 'N/A' else ''
        fuzzy_class = get_score_class(fuzzy) if fuzzy != 'N/A' else ''
        cer_class = get_cer_class(cer) if cer != 'N/A' else ''

        f1_macro_display = f"{f1_macro:.4f}" if f1_macro != 'N/A' else 'N/A'
        f1_micro_display = f"{f1_micro:.4f}" if f1_micro != 'N/A' else 'N/A'
        fuzzy_display = f"{fuzzy:.4f}" if fuzzy != 'N/A' else 'N/A'
        cer_display = f"{cer:.4f}" if cer != 'N/A' else 'N/A'

        # Format cost values
        input_cost_display = f"${result['input_cost']:.6f}" if result['input_cost'] > 0 else '$0.00'
        output_cost_display = f"${result['output_cost']:.6f}" if result['output_cost'] > 0 else '$0.00'
        total_cost_display = f"${result['total_cost']:.6f}" if result['total_cost'] > 0 else '$0.00'

        # Format warnings
        warnings = result.get('warnings', [])
        if warnings:
            warnings_html = '<div class="warnings">'
            for warning in warnings:
                severity_class = f"warning-{warning['severity']}"
                warnings_html += f'<span class="warning-badge {severity_class}" title="{warning["message"]}">{warning["code"]}</span>'
            warnings_html += '</div>'
        else:
            warnings_html = '<span class="warning-none">✓</span>'

        html += f"""
            <tr>
                <td>{result.get('date', 'N/A')}</td>
                <td><strong>{result['test_id']}</strong></td>
                <td class="benchmark-name">{result.get('name', 'Unknown')}</td>
                <td><span class="badge badge-provider">{result.get('provider', 'Unknown')}</span></td>
                <td><span class="badge badge-model">{result.get('model', 'Unknown')}</span></td>
                <td>{result['items_count']}</td>
                <td><span class="score {f1_macro_class}">{f1_macro_display}</span></td>
                <td><span class="score {f1_micro_class}">{f1_micro_display}</span></td>
                <td><span class="score {fuzzy_class}">{fuzzy_display}</span></td>
                <td><span class="score {cer_class}">{cer_display}</span></td>
                <td class="duration">{result['avg_duration']:.2f}s</td>
                <td class="duration">{result['total_duration']:.2f}s</td>
                <td>{input_cost_display}</td>
                <td>{output_cost_display}</td>
                <td>{total_cost_display}</td>
                <td>{warnings_html}</td>
            </tr>
"""

    html += """
        </tbody>
    </table>

    <div class="footer">
        <p>Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </div>

    <script>
        // Make table sortable
        document.addEventListener('DOMContentLoaded', function() {{
            const table = document.querySelector('table');
            const headers = table.querySelectorAll('th');
            const tbody = table.querySelector('tbody');

            // Add sortable class to headers
            headers.forEach(header => header.classList.add('sortable'));

            headers.forEach((header, index) => {{
                header.addEventListener('click', () => {{
                    // Get current sort direction
                    const currentSort = header.classList.contains('sort-asc') ? 'asc' :
                                       header.classList.contains('sort-desc') ? 'desc' : 'none';

                    // Remove sort classes from all headers
                    headers.forEach(h => {{
                        h.classList.remove('sort-asc', 'sort-desc');
                    }});

                    // Determine new sort direction
                    const newSort = currentSort === 'none' ? 'asc' :
                                   currentSort === 'asc' ? 'desc' : 'asc';

                    // Add appropriate class
                    header.classList.add(newSort === 'asc' ? 'sort-asc' : 'sort-desc');

                    // Sort rows
                    const rows = Array.from(tbody.querySelectorAll('tr'));

                    rows.sort((a, b) => {{
                        let aValue = a.cells[index].textContent.trim();
                        let bValue = b.cells[index].textContent.trim();

                        // Handle N/A values
                        if (aValue === 'N/A') aValue = newSort === 'asc' ? 'zzz' : '';
                        if (bValue === 'N/A') bValue = newSort === 'asc' ? 'zzz' : '';

                        // Extract numeric values from strings with $ or other prefixes
                        const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
                        const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));

                        // Determine if values are numeric
                        const isNumeric = !isNaN(aNum) && !isNaN(bNum);

                        let comparison = 0;
                        if (isNumeric) {{
                            comparison = aNum - bNum;
                        }} else {{
                            comparison = aValue.localeCompare(bValue);
                        }}

                        return newSort === 'asc' ? comparison : -comparison;
                    }});

                    // Reappend sorted rows
                    rows.forEach(row => tbody.appendChild(row));
                }});
            }});
        }});
    </script>
</body>
</html>
"""

    print(f"  Writing HTML file...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  ✓ HTML report generated: {output_file}")


def generate_markdown_report(dates, base_dir, test_metadata, output_file):
    """Generate Markdown report"""

    # Collect all test results from all dates
    test_results = []

    for date in dates:
        results_dir = base_dir / "results" / date
        if not results_dir.exists():
            print(f"  ⚠️  Skipping {date} (no results found)")
            continue

        # Collect all test folders for this date
        test_dirs = sorted([d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith('T')])
        total_tests = len(test_dirs)
        print(f"  Found {total_tests} tests for {date}")

        # Analyze each test
        for idx, test_dir in enumerate(test_dirs, 1):
            test_id = test_dir.name
            result = analyze_test_results(results_dir, test_id, date)
            if result:
                # Add metadata
                if test_id in test_metadata:
                    result.update(test_metadata[test_id])
                # Detect warnings after metadata is available
                result['warnings'] = detect_warnings(result)
                test_results.append(result)

    print(f"  Total: {len(test_results)} tests analyzed across {len(dates)} date(s)")

    # Sort by date, then by test ID
    test_results.sort(key=lambda x: (x['date'], x['test_id']))

    # Generate title based on single date or date range
    if len(dates) == 1:
        title = f"Test Results for {dates[0]}"
    else:
        title = f"Test Results for {dates[0]} to {dates[-1]}"

    # Generate Markdown
    md = f"""# {title}

## Summary

- **Date Range:** {dates[0]} to {dates[-1]} ({len(dates)} date(s))
- **Total Tests:** {len(test_results)}
- **Total Items Tested:** {sum(r['items_count'] for r in test_results)}
- **Unique Benchmarks:** {len(set(r.get('name', 'Unknown') for r in test_results))}
- **Total Duration:** {sum(r['total_duration'] for r in test_results):.1f}s
- **Total Cost:** ${sum(r['total_cost'] for r in test_results):.6f} USD
- **Tests with Warnings:** {sum(1 for r in test_results if r.get('warnings', []))}

## Results

| Date | Test ID | Benchmark | Provider | Model | Items | F1 Macro | F1 Micro | Fuzzy | CER | Avg Duration | Total Duration | Input Cost ($) | Output Cost ($) | Total Cost ($) | Warnings |
|------|---------|-----------|----------|-------|-------|----------|----------|-------|-----|--------------|----------------|----------------|-----------------|----------------|----------|
"""

    for result in test_results:
        f1_macro = result['f1_macro']
        f1_micro = result['f1_micro']
        fuzzy = result['fuzzy']
        cer = result['cer']

        f1_macro_display = f"{f1_macro:.4f}" if f1_macro != 'N/A' else 'N/A'
        f1_micro_display = f"{f1_micro:.4f}" if f1_micro != 'N/A' else 'N/A'
        fuzzy_display = f"{fuzzy:.4f}" if fuzzy != 'N/A' else 'N/A'
        cer_display = f"{cer:.4f}" if cer != 'N/A' else 'N/A'

        # Format cost values
        input_cost_display = f"${result['input_cost']:.6f}" if result['input_cost'] > 0 else '$0.00'
        output_cost_display = f"${result['output_cost']:.6f}" if result['output_cost'] > 0 else '$0.00'
        total_cost_display = f"${result['total_cost']:.6f}" if result['total_cost'] > 0 else '$0.00'

        # Format warnings for markdown
        warnings = result.get('warnings', [])
        if warnings:
            warnings_md = ', '.join([f"{w['code']}" for w in warnings])
        else:
            warnings_md = '✓'

        md += f"| {result.get('date', 'N/A')} | {result['test_id']} | {result.get('name', 'Unknown')} | {result.get('provider', 'Unknown')} | {result.get('model', 'Unknown')} | {result['items_count']} | {f1_macro_display} | {f1_micro_display} | {fuzzy_display} | {cer_display} | {result['avg_duration']:.2f}s | {result['total_duration']:.2f}s | {input_cost_display} | {output_cost_display} | {total_cost_display} | {warnings_md} |\n"

    md += f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    print(f"  Writing Markdown file...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"  ✓ Markdown report generated: {output_file}")


def generate_warnings_report(dates, base_dir, test_metadata, output_file):
    """Generate warnings-only report as GitHub issue template"""

    # Collect all test results from all dates
    test_results = []

    for date in dates:
        results_dir = base_dir / "results" / date
        if not results_dir.exists():
            print(f"  ⚠️  Skipping {date} (no results found)")
            continue

        # Collect all test folders for this date
        test_dirs = sorted([d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith('T')])
        total_tests = len(test_dirs)

        # Analyze each test
        for idx, test_dir in enumerate(test_dirs, 1):
            test_id = test_dir.name
            result = analyze_test_results(results_dir, test_id, date)
            if result:
                # Add metadata
                if test_id in test_metadata:
                    result.update(test_metadata[test_id])
                # Detect warnings after metadata is available
                result['warnings'] = detect_warnings(result)
                # Only include tests with warnings
                if result['warnings']:
                    test_results.append(result)

    print(f"  Total: {len(test_results)} tests with warnings across {len(dates)} date(s)")

    # Sort by date, then by test ID
    test_results.sort(key=lambda x: (x['date'], x['test_id']))

    # Generate title based on single date or date range
    if len(dates) == 1:
        title = f"Test Warnings Report - {dates[0]}"
        date_display = dates[0]
    else:
        title = f"Test Warnings Report - {dates[0]} to {dates[-1]}"
        date_display = f"{dates[0]} to {dates[-1]}"

    # Generate warnings report
    md = f"""# {title}

**Date Range:** {date_display}
**Tests with warnings:** {len(test_results)}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**Note:** For detailed error messages and stack traces, check the log files in `scripts/logs/`.

*Add GitHub issue links in the Ticket column for tracking.*

| Date | Test ID | Benchmark | Provider | Model | Severity | Warning Codes | Ticket | Action | Completed |
|------|---------|-----------|----------|-------|----------|---------------|--------|--------|-----------|
"""

    for result in test_results:
        # Get highest severity
        severities = [w['severity'] for w in result['warnings']]
        if 'critical' in severities:
            severity = '🔴 Critical'
        elif 'high' in severities:
            severity = '🟠 High'
        elif 'medium' in severities:
            severity = '🟡 Medium'
        else:
            severity = 'Low'

        warning_codes = ', '.join([w['code'] for w in result['warnings']])

        md += f"| {result.get('date', 'N/A')} | {result['test_id']} | {result.get('name', 'Unknown')} | {result.get('provider', 'Unknown')} | {result.get('model', 'Unknown')} | {severity} | {warning_codes} | | | |\n"

    md += "\n---\n\n"
    md += "## Warning Codes Explanation\n\n"
    md += "| Code | Severity | Description |\n"
    md += "|------|----------|-------------|\n"
    md += "| **ZERO_COST** | 🟠 High | Total cost is $0 (pricing issue) |\n"
    md += "| **ALL_NA** | 🔴 Critical | All metrics are N/A (scoring failed) |\n"
    md += "| **ZERO_SCORE** | 🟡 Medium | Score is 0 (exceptionally bad performance) |\n"
    md += "| **ZERO_ITEMS** | 🔴 Critical | No items processed |\n"
    md += "| **ZERO_DURATION** | 🟠 High | No timing captured |\n"
    md += "\n---\n\n"
    md += "## Action Required\n\n"
    md += "- [ ] Review all critical issues\n"
    md += "- [ ] Investigate high priority issues\n"
    md += "- [ ] Check medium priority issues as time permits\n"
    md += "- [ ] Re-run failed tests if needed\n"
    md += "- [ ] Update pricing data if ZERO_COST warnings present\n"
    md += "- [ ] Fix scoring issues if ALL_NA or ZERO_SCORE warnings present\n"

    print(f"  Writing warnings file...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"  ✓ Warnings report generated: {output_file} ({len(test_results)} tests with warnings)")


def main():
    parser = argparse.ArgumentParser(
        description='Generate a report for tests run on a specific date or date range',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single date:
    python scripts/generate_date_report.py --date 2025-03-05 --format html

  Date range:
    python scripts/generate_date_report.py --start-date 2025-03-01 --end-date 2025-03-05 --format both

  With custom output:
    python scripts/generate_date_report.py --date 2025-03-05 --output custom_report.html
        """
    )

    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument('--date', help='Single date in YYYY-MM-DD format')
    date_group.add_argument('--start-date', help='Start date for range (use with --end-date)')

    parser.add_argument('--end-date', help='End date for range (use with --start-date)')
    parser.add_argument('--format', choices=['html', 'md', 'both'], default='html',
                        help='Output format (html, md, or both)')
    parser.add_argument('--output', help='Output file path (optional)')
    parser.add_argument('--no-warnings', action='store_true',
                        help='Skip generating the warnings report')

    args = parser.parse_args()

    # Validate date arguments
    if args.start_date and not args.end_date:
        parser.error("--start-date requires --end-date")
    if args.end_date and not args.start_date:
        parser.error("--end-date requires --start-date")

    # Setup paths
    base_dir = Path(__file__).parent.parent

    # Determine date range
    if args.date:
        dates = [args.date]
        date_label = args.date
    else:
        try:
            dates = get_date_range(args.start_date, args.end_date)
            date_label = f"{args.start_date}_to_{args.end_date}"
        except ValueError as e:
            print(f"❌ Error: {e}")
            return

    print(f"=" * 70)
    print(f"Report Generator")
    print(f"Date(s): {dates[0]}" + (f" to {dates[-1]} ({len(dates)} dates)" if len(dates) > 1 else ""))
    print(f"=" * 70)

    # Check if any results exist
    existing_dates = []
    for date in dates:
        results_dir = base_dir / "results" / date
        if results_dir.exists():
            existing_dates.append(date)

    if not existing_dates:
        print(f"❌ Error: No results found for any of the specified dates")
        print(f"   Dates checked: {', '.join(dates)}")
        return

    if len(existing_dates) < len(dates):
        missing_dates = set(dates) - set(existing_dates)
        print(f"⚠️  Warning: Results not found for: {', '.join(sorted(missing_dates))}")

    # Load test metadata
    print("\n📋 Loading test metadata...")
    test_metadata = load_test_metadata()
    print(f"   ✓ Loaded metadata for {len(test_metadata)} tests")

    # Create reports directory if it doesn't exist
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Generate reports
    if args.format in ['html', 'both']:
        print(f"\n📊 Generating HTML report...")
        output_file = args.output or reports_dir / f"{date_label}_report.html"
        generate_html_report(existing_dates, base_dir, test_metadata, output_file)

    if args.format in ['md', 'both']:
        print(f"\n📝 Generating Markdown report...")
        output_file = args.output or reports_dir / f"{date_label}_report.md"
        generate_markdown_report(existing_dates, base_dir, test_metadata, output_file)

    # Generate warnings report unless disabled
    if not args.no_warnings:
        print(f"\n⚠️  Generating warnings report...")
        warnings_file = reports_dir / f"{date_label}_report_warnings.md"
        generate_warnings_report(existing_dates, base_dir, test_metadata, warnings_file)

    print(f"\n{'=' * 70}")
    print(f"✅ All reports generated successfully!")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
