#!/usr/bin/env python3
"""
Generate a report for all tests run on a specific date.
Usage: python scripts/generate_date_report.py --date 2025-03-05 --format html
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
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


def analyze_test_results(results_dir, test_id):
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

    return {
        'test_id': test_id,
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


def generate_html_report(date, results_dir, test_metadata, output_file):
    """Generate HTML report"""

    # Collect all test folders
    test_dirs = sorted([d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith('T')])

    # Analyze each test
    test_results = []
    for test_dir in test_dirs:
        test_id = test_dir.name
        result = analyze_test_results(results_dir, test_id)
        if result:
            # Add metadata
            if test_id in test_metadata:
                result.update(test_metadata[test_id])
            test_results.append(result)

    # Sort by test ID
    test_results.sort(key=lambda x: x['test_id'])

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Results - {date}</title>
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
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>📊 Test Results for {date}</h1>

    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-stats">
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
        </div>
    </div>

    <table>
        <thead>
            <tr>
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

        html += f"""
            <tr>
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

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML report generated: {output_file}")


def generate_markdown_report(date, results_dir, test_metadata, output_file):
    """Generate Markdown report"""

    # Collect all test folders
    test_dirs = sorted([d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith('T')])

    # Analyze each test
    test_results = []
    for test_dir in test_dirs:
        test_id = test_dir.name
        result = analyze_test_results(results_dir, test_id)
        if result:
            # Add metadata
            if test_id in test_metadata:
                result.update(test_metadata[test_id])
            test_results.append(result)

    # Sort by test ID
    test_results.sort(key=lambda x: x['test_id'])

    # Generate Markdown
    md = f"""# Test Results for {date}

## Summary

- **Total Tests:** {len(test_results)}
- **Total Items Tested:** {sum(r['items_count'] for r in test_results)}
- **Unique Benchmarks:** {len(set(r.get('name', 'Unknown') for r in test_results))}
- **Total Duration:** {sum(r['total_duration'] for r in test_results):.1f}s
- **Total Cost:** ${sum(r['total_cost'] for r in test_results):.6f} USD

## Results

| Test ID | Benchmark | Provider | Model | Items | F1 Macro | F1 Micro | Fuzzy | CER | Avg Duration | Total Duration | Input Cost ($) | Output Cost ($) | Total Cost ($) |
|---------|-----------|----------|-------|-------|----------|----------|-------|-----|--------------|----------------|----------------|-----------------|----------------|
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

        md += f"| {result['test_id']} | {result.get('name', 'Unknown')} | {result.get('provider', 'Unknown')} | {result.get('model', 'Unknown')} | {result['items_count']} | {f1_macro_display} | {f1_micro_display} | {fuzzy_display} | {cer_display} | {result['avg_duration']:.2f}s | {result['total_duration']:.2f}s | {input_cost_display} | {output_cost_display} | {total_cost_display} |\n"

    md += f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"Markdown report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate a report for tests run on a specific date')
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--format', choices=['html', 'md', 'both'], default='html',
                        help='Output format (html, md, or both)')
    parser.add_argument('--output', help='Output file path (optional)')

    args = parser.parse_args()

    # Setup paths
    base_dir = Path(__file__).parent.parent
    results_dir = base_dir / "results" / args.date

    if not results_dir.exists():
        print(f"Error: No results found for date {args.date}")
        print(f"Looking in: {results_dir}")
        return

    # Load test metadata
    print("Loading test metadata...")
    test_metadata = load_test_metadata()

    # Generate reports
    if args.format in ['html', 'both']:
        output_file = args.output or base_dir / "results" / args.date / f"report_{args.date}.html"
        print(f"Generating HTML report...")
        generate_html_report(args.date, results_dir, test_metadata, output_file)

    if args.format in ['md', 'both']:
        output_file = args.output or base_dir / "results" / args.date / f"report_{args.date}.md"
        print(f"Generating Markdown report...")
        generate_markdown_report(args.date, results_dir, test_metadata, output_file)

    print("Done!")


if __name__ == '__main__':
    main()
