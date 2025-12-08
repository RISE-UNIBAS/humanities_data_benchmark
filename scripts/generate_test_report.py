#!/usr/bin/env python3
"""Generate HTML reports for benchmark test results.

This script creates detailed HTML reports from test result folders,
including scoring metrics, model responses, ground truth comparisons,
and cost analysis.
"""

import argparse
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file and return parsed data."""
    if not file_path.exists():
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return None


def get_test_config(test_id: str) -> Optional[Dict[str, Any]]:
    """Load test configuration from benchmarks_tests.csv."""
    csv_path = Path(__file__).parent.parent / "benchmarks" / "benchmarks_tests.csv"
    if not csv_path.exists():
        return None

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:  # Skip header
                parts = line.strip().split(',')
                if parts[0] == test_id:
                    return {
                        "id": parts[0],
                        "benchmark": parts[1],
                        "provider": parts[2],
                        "model": parts[3],
                        "dataclass": parts[4],
                        "temperature": parts[5],
                        "role_description": parts[6],
                        "prompt_file": parts[7],
                        "rules": parts[8],
                        "legacy_test": parts[9] if len(parts) > 9 else "false"
                    }
    except Exception as e:
        print(f"Error loading test config: {e}", file=sys.stderr)

    return None


def get_benchmark_meta(benchmark_name: str) -> Optional[Dict[str, Any]]:
    """Load benchmark metadata from meta.json."""
    meta_path = Path(__file__).parent.parent / "benchmarks" / benchmark_name / "meta.json"
    return load_json(meta_path)


def load_ground_truth(benchmark_name: str, item_id: str) -> Optional[Dict[str, Any]]:
    """Load ground truth data for a specific item."""
    gt_path = Path(__file__).parent.parent / "benchmarks" / benchmark_name / "ground_truths" / f"{item_id}.json"
    return load_json(gt_path)


def format_cost(cost_usd: float) -> str:
    """Format cost in USD with appropriate precision."""
    if cost_usd >= 1:
        return f"${cost_usd:.2f}"
    elif cost_usd >= 0.01:
        return f"${cost_usd:.4f}"
    else:
        return f"${cost_usd:.6f}"


def format_duration(seconds: float) -> str:
    """Format duration in seconds."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.0f}s"


def generate_html_report(
    result_folder: Path,
    output_file: Path,
    include_raw: bool = False,
    include_images: bool = True
) -> None:
    """Generate HTML report for a test result folder."""

    # Extract test metadata from folder structure
    date_str = result_folder.parent.name
    test_id = result_folder.name

    # Load test configuration
    test_config = get_test_config(test_id)
    if not test_config:
        print(f"Warning: Could not load test configuration for {test_id}", file=sys.stderr)
        test_config = {"id": test_id, "benchmark": "Unknown"}

    # Load benchmark metadata
    benchmark_name = test_config.get("benchmark", "Unknown")
    benchmark_meta = get_benchmark_meta(benchmark_name)

    # Load scoring data
    scoring_path = result_folder / "scoring.json"
    scoring = load_json(scoring_path)

    # Load all request/response files
    request_files = sorted(result_folder.glob("request_*.json"))
    results = []

    for req_file in request_files:
        req_data = load_json(req_file)
        if not req_data:
            continue

        # Extract item ID from filename
        # Examples:
        #   request_T0360_156089_1321091_28.json -> 156089_1321091_28
        #   request_T10_letter01.json -> letter01
        parts = req_file.stem.split('_')
        item_id = '_'.join(parts[2:]) if len(parts) > 2 else req_file.stem

        # Load ground truth
        ground_truth = load_ground_truth(benchmark_name, item_id)

        results.append({
            "item_id": item_id,
            "request_data": req_data,
            "ground_truth": ground_truth
        })

    # Generate HTML
    html = generate_html_content(
        test_id=test_id,
        date_str=date_str,
        test_config=test_config,
        benchmark_meta=benchmark_meta,
        scoring=scoring,
        results=results,
        include_raw=include_raw,
        include_images=include_images
    )

    # Write HTML file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Report generated: {output_file}")


def generate_html_content(
    test_id: str,
    date_str: str,
    test_config: Dict[str, Any],
    benchmark_meta: Optional[Dict[str, Any]],
    scoring: Optional[Dict[str, Any]],
    results: List[Dict[str, Any]],
    include_raw: bool,
    include_images: bool
) -> str:
    """Generate the HTML content for the report."""

    benchmark_name = test_config.get("benchmark", "Unknown")
    benchmark_title = benchmark_meta.get("title", benchmark_name) if benchmark_meta else benchmark_name

    # Start HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report: {test_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header .meta {{
            opacity: 0.9;
            font-size: 14px;
        }}

        .content {{
            padding: 30px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section h2 {{
            font-size: 22px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
            color: #667eea;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .info-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}

        .info-card .label {{
            font-size: 12px;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 5px;
            font-weight: 600;
        }}

        .info-card .value {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }}

        .score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .score-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
        }}

        .score-card .score {{
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .score-card .label {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }}

        .result-item {{
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .result-item h3 {{
            font-size: 18px;
            margin-bottom: 15px;
            color: #333;
        }}

        .comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }}

        .comparison-col {{
            background: white;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        }}

        .comparison-col h4 {{
            font-size: 14px;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #e0e0e0;
        }}

        .json-view {{
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.4;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 5px;
        }}

        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}

        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}

        .cost-summary {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }}

        .cost-summary h4 {{
            font-size: 14px;
            margin-bottom: 10px;
            color: #856404;
        }}

        .cost-row {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 14px;
        }}

        .cost-row.total {{
            font-weight: 700;
            border-top: 2px solid #ffc107;
            padding-top: 10px;
            margin-top: 5px;
        }}

        details {{
            margin-top: 15px;
        }}

        summary {{
            cursor: pointer;
            font-weight: 600;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            user-select: none;
        }}

        summary:hover {{
            background: #e9ecef;
        }}

        .field-comparison {{
            margin-top: 10px;
        }}

        .field-row {{
            display: grid;
            grid-template-columns: 200px 1fr 1fr 80px;
            gap: 10px;
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
            align-items: start;
        }}

        .field-row:hover {{
            background: #f8f9fa;
        }}

        .field-name {{
            font-weight: 600;
            color: #555;
            font-size: 13px;
        }}

        .field-value {{
            font-size: 13px;
            word-break: break-word;
        }}

        .field-score {{
            text-align: right;
            font-weight: 600;
        }}

        .field-score.high {{ color: #28a745; }}
        .field-score.medium {{ color: #ffc107; }}
        .field-score.low {{ color: #dc3545; }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}

            .result-item {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{benchmark_title}</h1>
            <div class="meta">
                Test ID: {test_id} | Date: {date_str} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </div>
        </div>

        <div class="content">
"""

    # Test Configuration Section
    html += f"""
            <div class="section">
                <h2>Test Configuration</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <div class="label">Provider</div>
                        <div class="value">{test_config.get('provider', 'N/A')}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Model</div>
                        <div class="value">{test_config.get('model', 'N/A')}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Temperature</div>
                        <div class="value">{test_config.get('temperature', 'N/A')}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Dataclass</div>
                        <div class="value">{test_config.get('dataclass', 'N/A')}</div>
                    </div>
"""

    if test_config.get('role_description'):
        html += f"""
                    <div class="info-card">
                        <div class="label">Role Description</div>
                        <div class="value">{test_config.get('role_description')}</div>
                    </div>
"""

    if test_config.get('prompt_file'):
        html += f"""
                    <div class="info-card">
                        <div class="label">Prompt File</div>
                        <div class="value">{test_config.get('prompt_file')}</div>
                    </div>
"""

    html += """
                </div>
            </div>
"""

    # Scoring Summary Section
    if scoring:
        html += """
            <div class="section">
                <h2>Scoring Summary</h2>
                <div class="score-grid">
"""

        # Main metrics
        if 'f1_macro' in scoring:
            html += f"""
                    <div class="score-card">
                        <div class="score">{scoring['f1_macro']:.3f}</div>
                        <div class="label">F1 Macro</div>
                    </div>
"""

        if 'f1_micro' in scoring:
            html += f"""
                    <div class="score-card">
                        <div class="score">{scoring['f1_micro']:.3f}</div>
                        <div class="label">F1 Micro</div>
                    </div>
"""

        if 'micro_precision' in scoring:
            html += f"""
                    <div class="score-card">
                        <div class="score">{scoring['micro_precision']:.3f}</div>
                        <div class="label">Precision</div>
                    </div>
"""

        if 'micro_recall' in scoring:
            html += f"""
                    <div class="score-card">
                        <div class="score">{scoring['micro_recall']:.3f}</div>
                        <div class="label">Recall</div>
                    </div>
"""

        if 'total_instances' in scoring:
            html += f"""
                    <div class="score-card">
                        <div class="score">{scoring['total_instances']}</div>
                        <div class="label">Total Instances</div>
                    </div>
"""

        html += """
                </div>
"""

        # Cost Summary
        if 'cost_summary' in scoring:
            cost = scoring['cost_summary']
            html += f"""
                <div class="cost-summary">
                    <h4>Cost Summary</h4>
                    <div class="cost-row">
                        <span>Input Tokens:</span>
                        <span>{cost.get('total_input_tokens', 0):,}</span>
                    </div>
                    <div class="cost-row">
                        <span>Output Tokens:</span>
                        <span>{cost.get('total_output_tokens', 0):,}</span>
                    </div>
                    <div class="cost-row">
                        <span>Input Cost:</span>
                        <span>{format_cost(cost.get('input_cost_usd', 0))}</span>
                    </div>
                    <div class="cost-row">
                        <span>Output Cost:</span>
                        <span>{format_cost(cost.get('output_cost_usd', 0))}</span>
                    </div>
                    <div class="cost-row total">
                        <span>Total Cost:</span>
                        <span>{format_cost(cost.get('total_cost_usd', 0))}</span>
                    </div>
                </div>
"""

        html += """
            </div>
"""

    # Individual Results Section
    html += """
            <div class="section">
                <h2>Individual Results</h2>
"""

    for idx, result in enumerate(results, 1):
        item_id = result['item_id']
        req_data = result['request_data']
        ground_truth = result['ground_truth']

        # Calculate item score
        score_data = req_data.get('score', {})
        item_score = None
        if 'f1_score' in score_data:
            item_score = score_data['f1_score']

        html += f"""
                <div class="result-item">
                    <h3>#{idx}: {item_id}</h3>
"""

        # Item metadata
        duration = req_data.get('duration')
        usage = req_data.get('usage', {})

        html += f"""
                    <div style="margin-bottom: 15px;">
"""

        if item_score is not None:
            score_class = 'success' if item_score >= 0.8 else ('warning' if item_score >= 0.5 else 'danger')
            html += f"""
                        <span class="badge badge-{score_class}">Score: {item_score:.3f}</span>
"""

        if duration:
            html += f"""
                        <span class="badge badge-info">Duration: {format_duration(duration)}</span>
"""

        if usage.get('total_tokens'):
            html += f"""
                        <span class="badge badge-info">Tokens: {usage['total_tokens']}</span>
"""

        if usage.get('estimated_cost_usd'):
            html += f"""
                        <span class="badge badge-info">Cost: {format_cost(usage['estimated_cost_usd'])}</span>
"""

        html += """
                    </div>
"""

        # Comparison view
        html += """
                    <div class="comparison">
                        <div class="comparison-col">
                            <h4>Model Response</h4>
                            <div class="json-view">
"""

        parsed = req_data.get('parsed')
        if parsed:
            html += f"""<pre>{json.dumps(parsed, indent=2, ensure_ascii=False)}</pre>"""
        else:
            html += "<em>No parsed response</em>"

        html += """
                            </div>
                        </div>
                        <div class="comparison-col">
                            <h4>Ground Truth</h4>
                            <div class="json-view">
"""

        if ground_truth:
            html += f"""<pre>{json.dumps(ground_truth, indent=2, ensure_ascii=False)}</pre>"""
        else:
            html += "<em>No ground truth available</em>"

        html += """
                            </div>
                        </div>
                    </div>
"""

        # Field-by-field comparison
        if score_data.get('field_scores'):
            html += """
                    <details>
                        <summary>Field-by-Field Comparison</summary>
                        <div class="field-comparison">
                            <div class="field-row" style="font-weight: 600; background: #f8f9fa;">
                                <div>Field</div>
                                <div>Response</div>
                                <div>Ground Truth</div>
                                <div style="text-align: right;">Score</div>
                            </div>
"""

            for field_name, field_data in score_data['field_scores'].items():
                field_score = field_data.get('score', 0)
                score_class = 'high' if field_score >= 0.8 else ('medium' if field_score >= 0.5 else 'low')

                response_val = field_data.get('response', '')
                gt_val = field_data.get('ground_truth', '')

                # Truncate long values
                if isinstance(response_val, str) and len(response_val) > 100:
                    response_val = response_val[:100] + "..."
                if isinstance(gt_val, str) and len(gt_val) > 100:
                    gt_val = gt_val[:100] + "..."

                html += f"""
                            <div class="field-row">
                                <div class="field-name">{field_name}</div>
                                <div class="field-value">{response_val}</div>
                                <div class="field-value">{gt_val}</div>
                                <div class="field-score {score_class}">{field_score:.2f}</div>
                            </div>
"""

            html += """
                        </div>
                    </details>
"""

        # Raw response (if requested)
        if include_raw and req_data.get('raw_response'):
            html += """
                    <details>
                        <summary>Raw API Response</summary>
                        <div class="json-view" style="margin-top: 10px;">
"""
            html += f"""<pre>{json.dumps(req_data['raw_response'], indent=2, ensure_ascii=False)[:5000]}</pre>"""
            html += """
                        </div>
                    </details>
"""

        html += """
                </div>
"""

    html += """
            </div>
        </div>
    </div>
</body>
</html>
"""

    return html


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate HTML reports for benchmark test results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report for a specific test result
  python scripts/generate_test_report.py results/2025-11-24/T0360

  # Generate report with custom output path
  python scripts/generate_test_report.py results/2025-11-24/T0360 -o reports/my_report.html

  # Include raw API responses and open in browser
  python scripts/generate_test_report.py results/2025-11-24/T0360 --include-raw --open
"""
    )

    parser.add_argument(
        'result_folder',
        type=str,
        help='Path to the test result folder (e.g., results/2025-11-24/T0360)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output HTML file path (default: reports/<test_id>_report.html)'
    )

    parser.add_argument(
        '--include-raw',
        action='store_true',
        help='Include raw API responses in the report'
    )

    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Do not include images in the report'
    )

    parser.add_argument(
        '--open',
        action='store_true',
        help='Open the report in the default web browser after generation'
    )

    args = parser.parse_args()

    # Validate result folder
    result_folder = Path(args.result_folder)
    if not result_folder.exists():
        print(f"Error: Result folder not found: {result_folder}", file=sys.stderr)
        sys.exit(1)

    if not result_folder.is_dir():
        print(f"Error: Not a directory: {result_folder}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_file = Path(args.output)
    else:
        test_id = result_folder.name
        reports_dir = Path(__file__).parent.parent / "reports"
        output_file = reports_dir / f"{test_id}_report.html"

    # Generate report
    try:
        generate_html_report(
            result_folder=result_folder,
            output_file=output_file,
            include_raw=args.include_raw,
            include_images=not args.no_images
        )
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Open in browser if requested
    if args.open:
        try:
            webbrowser.open(f"file://{output_file.absolute()}")
            print(f"✓ Opened report in browser")
        except Exception as e:
            print(f"Warning: Could not open browser: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
