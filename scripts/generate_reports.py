import json
import os
import csv
import re
import logging
import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from data_loader import write_file, read_file
from report_helper import get_square, create_html_table, get_rectangle, get_badge
from run_benchmarks import BENCHMARKS_DIR, CONFIG_FILE, REPORTS_DIR


def load_test_configuration(test_id):
    """Load the test configuration from the configuration file."""
    with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
        tests = csv.DictReader(csvfile)
        for test in tests:
            if test['id'] == test_id:
                return test


def load_all_benchmarks():
    """Load all benchmark results from the results directory."""
    results = []
    for benchmark in os.listdir(BENCHMARKS_DIR):
        if not os.path.isdir(os.path.join(BENCHMARKS_DIR, benchmark)):
            continue
        results.append(benchmark)
    return sorted(results)


def load_test_dates():
    """Load all test results from the results directory."""
    dates = []
    for date in sorted(os.listdir("../results"), reverse=True):
        if os.path.isdir(os.path.join("../results", date)):
            dates.append(date)
    return dates


def find_latest_date(test_id):
    """Find the latest result for a test."""
    results_dir = "../results"

    # Get all valid date folders and sort them descending
    date_folders = sorted(
        [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))],
        reverse=True,  # Sort descending
        key=lambda date: date  # Dates are already in YYYY-MM-DD format
    )

    # Find the latest valid date containing the test_id
    for date in date_folders:
        if os.path.isdir(os.path.join(results_dir, date, test_id)):
            return date  # Return the first match (latest date)

    return None


def create_archive_overview(dates, benchmark_names):
    """Generate an overview of all tests."""
    overview_path = os.path.join(REPORTS_DIR, "archive", "overview.md")
    os.makedirs(os.path.dirname(overview_path), exist_ok=True)

    md_string =  ("# Benchmark Overview\n\n"
                 "This page provides an overview of all benchmark tests."
                 "Click on the test name to see the detailed results.\n\n")

    table_headers = ["Date"]
    for benchmark in benchmark_names:
        table_headers.append(benchmark)

    table_data = []

    for date in dates:
        row_data = [date]
        for benchmark in benchmark_names:
            result_path = os.path.join("..", "results", date)
            if os.path.exists(result_path):
                cell = ""
                for test in os.listdir(result_path):
                    conf = load_test_configuration(test)
                    if conf is None:
                        print(f"Warning: Could not find configuration for test ID '{test}' in {date}")
                        continue
                    if conf['name'] == benchmark:
                        cell += get_square(test, href=f"/humanities_data_benchmark/archive/{date}/{test}") + "&nbsp;"
            else:
                cell = ""
            row_data.append(cell)
        table_data.append(row_data)

    md_string += create_html_table(table_headers, table_data)
    write_file(overview_path, md_string)


def create_individual_reports():
    """Generate detailed reports for each test."""

    for date in os.listdir("../results"):
        for test in os.listdir("../results/" + date):
            test_config = load_test_configuration(test)
            if test_config is None:
                print(f"Warning: Could not find configuration for test ID '{test}' in {date}, skipping...")
                continue
                
            renders_directory = os.path.join("..", "renders", date, test)

            test_report_path = os.path.join(REPORTS_DIR, "archive", date, f"{test}.md")
            os.makedirs(os.path.dirname(test_report_path), exist_ok=True)

            test_score_path = os.path.join('..', "results", date, test, "scoring.json")
            if os.path.exists(test_score_path):
                with open(test_score_path, "r", encoding="utf-8") as f:
                    score_data = json.load(f)
            else:
                score_data = {'Total': 0}

            md_string = "# Test Report\n\n"
            md_string += f"This test has the following configuration:\n\n"
            md_string += get_badge("data", test_config['name'], "lightgrey",
                                     href=f"/humanities_data_benchmark/benchmarks/{test_config['name']}") + "&nbsp;"
            md_string += get_badge("provider", test_config['provider'], "green") + "&nbsp;"
            md_string += get_badge("model", test_config['model'], "blue") + "&nbsp;"
            if test_config['dataclass'] != "":
                md_string += get_badge("dataclass", test_config['dataclass'], "purple") + "&nbsp;"
            if test_config['temperature'] != "":
                md_string += get_badge("temperature", test_config['temperature'], r_to_g=(0, 1)) + "&nbsp;"

            md_string += get_badge("prompt_file", test_config['prompt_file'] or "prompt.txt", "lightgrey") + "&nbsp;"

            if test_config['legacy_test'] == "false":
                md_string += get_badge("active", "yes", "brightgreen")
            else:
                md_string += get_badge("active", "no", "red")

            md_string += "\n\n## Test Results\n"
            for key, value in score_data.items():
                md_string += get_badge(key, value) + "&nbsp;"
            md_string += "\n\n"

            md_string += "## Detailed Results\n"
            if os.path.exists(renders_directory):
                for render in os.listdir(renders_directory):
                    md_string += read_file(os.path.join(renders_directory, render))
                    md_string += "\n\n"
            else:
                md_string += "No renders available\n\n"

            write_file(test_report_path, md_string)


def create_leaderboard_radar_chart(leaderboard_data):
    """Create a radar chart image for the top performing models in the leaderboard."""
    if not leaderboard_data:
        return "<p>No leaderboard data available for radar chart.</p>"
    
    # Take top 10 models for better readability
    top_models = leaderboard_data[:10]
    
    # Categories for the radar chart
    categories = ['bibliographic_data', 'fraktur', 'metadata_extraction', 'zettelkatalog']
    category_labels = ['Bibliographic Data', 'Fraktur', 'Metadata Extraction', 'Zettelkatalog']
    
    # Number of variables
    N = len(categories)
    
    # Compute angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the circle
    
    # Create the plot with better styling
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor('white')
    
    # Extended color palette for 10 models with better contrast
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83', 
              '#0D7377', '#14A085', '#7209B7', '#B08D57', '#E74C3C']
    line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
    
    # Customize grid appearance
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10, alpha=0.7)
    ax.grid(True, alpha=0.4, linewidth=0.8)
    ax.set_facecolor('#fafafa')
    
    # Plot each model with improved styling
    for i, model_data in enumerate(top_models):
        if i >= len(colors):
            break
            
        # Get values for this model
        values = []
        for category in categories:
            value = model_data[category]
            if value is not None:
                values.append(value)
            else:
                values.append(0)
        
        values += values[:1]  # Complete the circle
        
        # Plot with improved styling
        ax.plot(angles, values, 'o', linewidth=3, label=model_data['model'], 
                color=colors[i], linestyle=line_styles[i], markersize=8, 
                markerfacecolor='white', markeredgecolor=colors[i], markeredgewidth=2)
        ax.fill(angles, values, alpha=0.1, color=colors[i])
    
    # Add category labels with better formatting
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(category_labels, fontsize=12, fontweight='bold', color='#333333')
    
    # Remove radial labels at 0 degrees to reduce clutter
    ax.set_rlabel_position(45)
    
    # Add legend with better positioning and styling
    legend = plt.legend(loc='center left', bbox_to_anchor=(1.15, 0.5), fontsize=11, 
                       frameon=True, fancybox=True, shadow=True, framealpha=0.9)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_edgecolor('#cccccc')
    
    # Set title with better styling
    plt.title('Model Performance Across Benchmarks', size=16, fontweight='bold', 
              color='#2c3e50', y=1.12, pad=20)
    
    # Add subtitle
    plt.figtext(0.5, 0.93, 'Comparison of Top 10 Models', ha='center', va='top', 
                fontsize=12, alpha=0.8, style='italic')
    
    # Add generation date with better styling
    generation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    plt.figtext(0.99, 0.02, f'Generated: {generation_date}', 
                ha='right', va='bottom', fontsize=9, alpha=0.6, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Save the plot with higher quality
    chart_path = os.path.join(REPORTS_DIR, 'radar_chart.png')
    plt.tight_layout()
    plt.savefig(chart_path, dpi=200, bbox_inches='tight', facecolor='white', 
                edgecolor='none', pad_inches=0.2)
    plt.close()
    
    # Return HTML to embed the image
    return f'<div style="text-align: center; margin: 20px 0;"><img src="radar_chart.png" alt="Radar Chart" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></div>'


def create_leaderboard():
    """Create a leaderboard section showing global averages for each model across key benchmarks."""
    
    # Target benchmarks for global average calculation
    target_benchmarks = ['bibliographic_data', 'fraktur', 'metadata_extraction', 'zettelkatalog']
    
    # Dictionary to store model scores: {model_name: {benchmark: [scores], provider: provider_name}}
    model_scores = {}
    
    # Common company name mappings for providers already used
    provider_mappings = {
        'anthropic': 'Anthropic',
        'openai': 'OpenAI',
        'genai': 'Google',
        'mistral': 'Mistral AI'
    }
    
    with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
        tests = csv.DictReader(csvfile)
        for test in tests:
            # Only process target benchmarks
            if test['name'] not in target_benchmarks:
                continue
                
            test_id = test['id']
            model = test['model']
            provider = test['provider']
            benchmark = test['name']
            
            # Find latest date for this test
            date = find_latest_date(test_id)
            if date is None:
                continue
                
            # Load scoring data
            scoring_file = os.path.join('..', 'results', date, test_id, 'scoring.json')
            scoring_data = read_file(scoring_file)
            try:
                scoring_data = json.loads(scoring_data)
            except json.decoder.JSONDecodeError:
                continue
            
            # Initialize model entry if not exists
            if model not in model_scores:
                model_scores[model] = {'provider': provider, 'costs': []}
            if benchmark not in model_scores[model]:
                model_scores[model][benchmark] = []
            
            # Extract the main score based on benchmark type
            score = None
            if benchmark == 'bibliographic_data':
                # Use fuzzy score for bibliographic_data
                score = scoring_data.get('fuzzy')
            elif benchmark == 'fraktur':
                # Use fuzzy score for fraktur
                score = scoring_data.get('fuzzy')
            elif benchmark == 'metadata_extraction':
                # Use f1_micro for metadata_extraction
                score = scoring_data.get('f1_micro')
            elif benchmark == 'zettelkatalog':
                # Use f1_micro for zettelkatalog
                score = scoring_data.get('f1_micro')
            
            if score is not None:
                try:
                    score_value = float(score) if isinstance(score, (str, int, float)) else 0
                    model_scores[model][benchmark].append(score_value)

                    # Extract cost information
                    if 'cost_summary' in scoring_data and scoring_data['cost_summary'] and 'total_cost_usd' in scoring_data['cost_summary']:
                        try:
                            cost_usd = float(scoring_data['cost_summary']['total_cost_usd'])
                            model_scores[model]['costs'].append(cost_usd)
                        except (ValueError, TypeError):
                            pass

                except (ValueError, TypeError):
                    continue
    
    # Calculate global averages for each model
    leaderboard_data = []
    for model, benchmarks in model_scores.items():
        benchmark_averages = {}
        total_score = 0
        benchmark_count = 0
        
        for benchmark_name in target_benchmarks:
            if benchmark_name in benchmarks and benchmarks[benchmark_name]:
                avg_score = sum(benchmarks[benchmark_name]) / len(benchmarks[benchmark_name])
                benchmark_averages[benchmark_name] = avg_score
                total_score += avg_score
                benchmark_count += 1
            else:
                benchmark_averages[benchmark_name] = None
        
        # Only include models that have results for all four benchmarks
        if benchmark_count == len(target_benchmarks):
            global_average = total_score / benchmark_count
            provider_name = provider_mappings.get(benchmarks.get('provider', '').lower(), benchmarks.get('provider', 'Unknown'))

            # Calculate average cost and cost per point
            avg_cost = None
            cost_per_point = None
            if 'costs' in benchmarks and benchmarks['costs']:
                avg_cost = sum(benchmarks['costs']) / len(benchmarks['costs'])
                if global_average > 0:
                    cost_per_point = avg_cost / global_average

            leaderboard_data.append({
                'model': model,
                'provider': provider_name,
                'global_avg': global_average,
                'avg_cost': avg_cost,
                'cost_per_point': cost_per_point,
                'bibliographic_data': benchmark_averages['bibliographic_data'],
                'fraktur': benchmark_averages['fraktur'],
                'metadata_extraction': benchmark_averages['metadata_extraction'],
                'zettelkatalog': benchmark_averages['zettelkatalog']
            })
    
    # Sort by global average (highest first)
    leaderboard_data.sort(key=lambda x: x['global_avg'], reverse=True)
    
    # Create leaderboard HTML table
    if not leaderboard_data:
        return "<p>No leaderboard data available.</p>"
    
    leaderboard_html = '''<div>
<table id="leaderboard-table" style="width:100%; border-collapse: collapse; margin-bottom: 20px;">
<thead>
<tr>
<th onclick="sortTable(0)" style="cursor: pointer;">Model ↕</th>
<th onclick="sortTable(1)" style="cursor: pointer;">Provider ↕</th>
<th onclick="sortTable(2)" style="cursor: pointer;">Global Average ↕</th>
<th onclick="sortTable(3)" style="cursor: pointer;">Cost per Point ↕</th>
<th onclick="sortTable(4)" style="cursor: pointer;"><a href="benchmarks/bibliographic_data/" style="color: inherit; text-decoration: none;">bibliographic_data</a> ↕</th>
<th onclick="sortTable(5)" style="cursor: pointer;"><a href="benchmarks/fraktur/" style="color: inherit; text-decoration: none;">fraktur</a> ↕</th>
<th onclick="sortTable(6)" style="cursor: pointer;"><a href="benchmarks/metadata_extraction/" style="color: inherit; text-decoration: none;">metadata_extraction</a> ↕</th>
<th onclick="sortTable(7)" style="cursor: pointer;"><a href="benchmarks/zettelkatalog/" style="color: inherit; text-decoration: none;">zettelkatalog</a> ↕</th>
</tr>
</thead>
<tbody>'''
    
    for rank, data in enumerate(leaderboard_data, 1):
        model_html = get_rectangle(data['model'])
        provider_html = get_rectangle(data['provider'])
        global_avg_badge = get_badge("global", f"{data['global_avg']:.3f}")

        # Create cost per point badge
        cost_per_point_badge = "N/A"
        cost_per_point_sort = "999"  # High value for N/A entries to sort last
        if data['cost_per_point'] is not None:
            cost_per_point_badge = get_badge("cost/pt", f"${data['cost_per_point']:.4f}/pt")
            cost_per_point_sort = f"{data['cost_per_point']:.4f}"

        biblio_badge = get_badge("fuzzy", f"{data['bibliographic_data']:.3f}") if data['bibliographic_data'] is not None else "N/A"
        fraktur_badge = get_badge("fuzzy", f"{data['fraktur']:.3f}") if data['fraktur'] is not None else "N/A"
        metadata_badge = get_badge("f1_micro", f"{data['metadata_extraction']:.3f}") if data['metadata_extraction'] is not None else "N/A"
        zettelkatalog_badge = get_badge("f1_micro", f"{data['zettelkatalog']:.3f}") if data['zettelkatalog'] is not None else "N/A"
        
        biblio_sort = f'{data["bibliographic_data"]:.3f}' if data["bibliographic_data"] is not None else "0"
        fraktur_sort = f'{data["fraktur"]:.3f}' if data["fraktur"] is not None else "0"  
        metadata_sort = f'{data["metadata_extraction"]:.3f}' if data["metadata_extraction"] is not None else "0"
        zettelkatalog_sort = f'{data["zettelkatalog"]:.3f}' if data["zettelkatalog"] is not None else "0"
        
        leaderboard_html += f'<tr><td data-sort="{data["model"]}">{model_html}</td><td data-sort="{data["provider"]}">{provider_html}</td><td data-sort="{data["global_avg"]:.3f}">{global_avg_badge}</td><td data-sort="{cost_per_point_sort}">{cost_per_point_badge}</td><td data-sort="{biblio_sort}">{biblio_badge}</td><td data-sort="{fraktur_sort}">{fraktur_badge}</td><td data-sort="{metadata_sort}">{metadata_badge}</td><td data-sort="{zettelkatalog_sort}">{zettelkatalog_badge}</td></tr>'
    
    leaderboard_html += '''</tbody>
</table>

<script>
function sortTable(columnIndex) {
const table = document.getElementById("leaderboard-table");
const tbody = table.getElementsByTagName("tbody")[0];
const rows = Array.from(tbody.getElementsByTagName("tr"));

const isAscending = table.getAttribute("data-sort-dir") !== "asc";
table.setAttribute("data-sort-dir", isAscending ? "asc" : "desc");

rows.sort((a, b) => {
const cellA = a.getElementsByTagName("td")[columnIndex];
const cellB = b.getElementsByTagName("td")[columnIndex];

let valueA = cellA.getAttribute("data-sort") || cellA.textContent.trim();
let valueB = cellB.getAttribute("data-sort") || cellB.textContent.trim();

if (!isNaN(valueA) && !isNaN(valueB)) {
valueA = parseFloat(valueA);
valueB = parseFloat(valueB);
}

if (valueA < valueB) return isAscending ? -1 : 1;
if (valueA > valueB) return isAscending ? 1 : -1;
return 0;
});


rows.forEach(row => tbody.appendChild(row));

const headers = table.getElementsByTagName("th");
for (let i = 0; i < headers.length; i++) {
const header = headers[i];
const text = header.innerHTML.replace(/ [↕↑↓]/g, '');
if (i === columnIndex) {
header.innerHTML = text + (isAscending ? ' ↑' : ' ↓');
} else {
header.innerHTML = text + ' ↕';
}
}
}

// Function to sort benchmark tables
function sortBenchmarkTable(benchmarkName, columnIndex) {
const table = document.getElementById(benchmarkName + "-table");
const tbody = table.getElementsByTagName("tbody")[0];
const rows = Array.from(tbody.getElementsByTagName("tr"));

const isAscending = table.getAttribute("data-sort-dir") !== "asc";
table.setAttribute("data-sort-dir", isAscending ? "asc" : "desc");

rows.sort((a, b) => {
const cellA = a.getElementsByTagName("td")[columnIndex];
const cellB = b.getElementsByTagName("td")[columnIndex];

let valueA = cellA.getAttribute("data-sort") || cellA.textContent.trim();
let valueB = cellB.getAttribute("data-sort") || cellB.textContent.trim();

if (!isNaN(valueA) && !isNaN(valueB)) {
valueA = parseFloat(valueA);
valueB = parseFloat(valueB);
}

if (valueA < valueB) return isAscending ? -1 : 1;
if (valueA > valueB) return isAscending ? 1 : -1;
return 0;
});

rows.forEach(row => tbody.appendChild(row));

const headers = table.getElementsByTagName("th");
for (let i = 0; i < headers.length; i++) {
const header = headers[i];
const text = header.innerHTML.replace(/ [↕↑↓]/g, '');
if (i === columnIndex) {
header.innerHTML = text + (isAscending ? ' ↑' : ' ↓');
} else {
header.innerHTML = text + ' ↕';
}
}
}
</script>
</div>'''
    
    return leaderboard_html, leaderboard_data


def create_index():
    """Generate the index page."""

    latest_results = {}

    with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
        tests = csv.DictReader(csvfile)
        for test in tests:
            if test['name'] not in latest_results:
                latest_results[test['name']] = {}

            # Create grouping key based on prompt_file and rules
            prompt_file = test.get('prompt_file', '') or 'prompt.txt'
            rules = test.get('rules', '') or ''
            group_key = f"{prompt_file}|{rules}"
            
            if group_key not in latest_results[test['name']]:
                latest_results[test['name']][group_key] = []
            
            latest_results[test['name']][group_key].append({
                'id': test['id'],
                'date': find_latest_date(test['id']),
                'config': test
            })

    # Create individual benchmark sections
    benchmark_sections = ""
    
    # Sort benchmarks alphabetically
    for benchmark in sorted(latest_results.keys()):
        if len(latest_results[benchmark]) == 0:
            # Skip benchmarks with no results
            continue

        benchmark_sections += f'### <a href="benchmarks/{benchmark}/">{benchmark}</a>\n\n'
        
        # Create table for this benchmark
        benchmark_table = f'''<table class="inner-table sortable-table" id="{benchmark}-table">
<thead>
<tr>
<th onclick="sortBenchmarkTable('{benchmark}', 0)" style="cursor: pointer;">Model ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 1)" style="cursor: pointer;">Provider ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 2)" style="cursor: pointer;">Test ID ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 3)" style="cursor: pointer;">Date ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 4)" style="cursor: pointer;">Prompt ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 5)" style="cursor: pointer;">Rules ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 6)" style="cursor: pointer;">Results ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 7)" style="cursor: pointer;">Cost (USD) ↕</th>
</tr>
</thead>
<tbody>'''
        
        # Collect all tests for this benchmark (no grouping)
        all_tests = []
        for group_key in latest_results[benchmark].keys():
            prompt_file, rules = group_key.split('|', 1)
            group_tests = latest_results[benchmark][group_key]
            
            for test_info in group_tests:
                test_id = test_info['id']
                date = test_info['date']
                test_config = test_info['config']
                
                if date is None:
                    continue
                
                # Get scoring data
                scoring_file = os.path.join('..', 'results', date, test_id, 'scoring.json')
                scoring_data = read_file(scoring_file)
                try:
                    scoring_data = json.loads(scoring_data)
                except json.decoder.JSONDecodeError:
                    scoring_data = {'Total': 0}

                # Extract the main score for sorting
                score_value = 0
                if benchmark == 'bibliographic_data' or benchmark == 'fraktur':
                    score_value = scoring_data.get('fuzzy', 0)
                elif benchmark == 'metadata_extraction' or benchmark == 'zettelkatalog':
                    score_value = scoring_data.get('f1_micro', 0)
                
                try:
                    score_value = float(score_value) if score_value else 0
                except (ValueError, TypeError):
                    score_value = 0

                # Show appropriate score with 3 decimal places as badge based on benchmark type
                badge_html = "N/A"
                if benchmark == 'metadata_extraction' or benchmark == 'zettelkatalog':
                    # Use f1_micro for metadata_extraction and zettelkatalog
                    if 'f1_micro' in scoring_data:
                        f1_value = scoring_data['f1_micro']
                        try:
                            f1_float = float(f1_value) if f1_value else 0
                            badge_html = get_badge('f1_micro', f"{f1_float:.3f}")
                        except (ValueError, TypeError):
                            badge_html = "N/A"
                else:
                    # Use fuzzy for bibliographic_data, fraktur, and other benchmarks
                    if 'fuzzy' in scoring_data:
                        fuzzy_value = scoring_data['fuzzy']
                        try:
                            fuzzy_float = float(fuzzy_value) if fuzzy_value else 0
                            badge_html = get_badge('fuzzy', f"{fuzzy_float:.3f}")
                        except (ValueError, TypeError):
                            badge_html = "N/A"

                # Extract cost information
                cost_html = "N/A"
                if 'cost_summary' in scoring_data and scoring_data['cost_summary'] and 'total_cost_usd' in scoring_data['cost_summary']:
                    try:
                        cost_usd = float(scoring_data['cost_summary']['total_cost_usd'])
                        cost_html = f"${cost_usd:.4f}"
                    except (ValueError, TypeError):
                        cost_html = "N/A"
                
                all_tests.append({
                    'test_id': test_id,
                    'model': test_config['model'],
                    'provider': test_config['provider'],
                    'date': date,
                    'prompt': prompt_file if prompt_file else "prompt.txt",
                    'rules': rules if rules else "None",
                    'badges': badge_html,
                    'cost': cost_html,
                    'score': score_value
                })
        
        # Sort by score (highest first)
        all_tests.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rows to table
        for test in all_tests:
            model_html = get_rectangle(test['model'])
            
            # Use provider mappings from leaderboard
            provider_mappings = {
                'anthropic': 'Anthropic',
                'openai': 'OpenAI',
                'genai': 'Google',
                'mistral': 'Mistral AI'
            }
            provider_display = provider_mappings.get(test['provider'].lower(), test['provider'])
            provider_html = get_rectangle(provider_display)
            
            # Create rules cell (always expanded)
            if test['rules'] and test['rules'].strip() and test['rules'] != "None":
                rules_display = f'''<div style="padding: 5px; background-color: #f5f5f5; border-radius: 3px; font-size: 0.9em; white-space: pre-wrap; max-width: 200px; overflow-wrap: break-word;">{test['rules']}</div>'''
            else:
                rules_display = "None"
            
            # Create clickable test ID using get_square for consistent styling
            test_id_square = get_square(test["test_id"], href="/humanities_data_benchmark/tests/" + test["test_id"])
            
            benchmark_table += f'<tr><td data-sort="{test["model"]}">{model_html}</td><td data-sort="{provider_display}">{provider_html}</td><td data-sort="{test["test_id"]}">{test_id_square}</td><td data-sort="{test["date"]}">{test["date"]}</td><td data-sort="{test["prompt"]}">{test["prompt"]}</td><td data-sort="{test["rules"] if test["rules"] != "None" else ""}">{rules_display}</td><td data-sort="{test["score"]:.3f}">{test["badges"]}</td><td data-sort="{test["cost"]}">{test["cost"]}</td></tr>'
        
        benchmark_table += '</tbody></table>\n\n'
        benchmark_sections += benchmark_table

    # Import TEST_STYLE from report_helper for styling
    from report_helper import TEST_STYLE
    
    # Generate leaderboard and radar chart
    leaderboard_html, leaderboard_data = create_leaderboard()
    
    # Generate radar chart HTML
    radar_chart_html = create_leaderboard_radar_chart(leaderboard_data)
    
    index_md = f"""
# Humanities Data Benchmark
Welcome to the **Humanities Data Benchmark** report page. This page provides an overview of all benchmark tests, 
results, and comparisons.

{TEST_STYLE}

## Leaderboard

The table below shows the **global average performance** and **cost efficiency** of each model across the four core benchmarks:
[bibliographic_data](benchmarks/bibliographic_data/), [fraktur](benchmarks/fraktur/), [metadata_extraction](benchmarks/metadata_extraction/), and [zettelkatalog](benchmarks/zettelkatalog/). The "Cost per Point" column shows how much each performance point costs in USD, helping you identify the most cost-effective models for your research. Only models with results in all four benchmarks are included. Click on any column header to sort the table.

{leaderboard_html}

The following radar chart shows the performance distribution of top models across the four core benchmarks:

{radar_chart_html}

## Latest Benchmark Results

{benchmark_sections}


## About This Page
This benchmark suite is designed to test **AI models** on humanities data tasks. The tests run **monthly** and 
results are automatically updated.

For more details, visit the [GitHub repository](https://github.com/RISE-UNIBAS/humanities_data_benchmark)."""

    write_file(os.path.join(REPORTS_DIR, "index.md"), index_md)

def create_test_runs_pages():
    """Generate detailed reports for each test run."""
    with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
        tests = csv.DictReader(csvfile)
        for test_config in tests:
            test_run_file = os.path.join(REPORTS_DIR, "tests", f"{test_config['id']}.md")
            os.makedirs(os.path.dirname(test_run_file), exist_ok=True)

            test_run_md = f"# Test {test_config['id']}\n\n"
            test_run_md += f"This test has the following configuration:\n\n"
            test_run_md += get_badge("data", test_config['name'], "lightgrey", href=f"/humanities_data_benchmark/benchmarks/{test_config['name']}") + "&nbsp;"
            test_run_md += get_badge("provider", test_config['provider'], "green") + "&nbsp;"
            test_run_md += get_badge("model", test_config['model'], "blue") + "&nbsp;"
            if test_config['dataclass'] != "":
                test_run_md += get_badge("dataclass", test_config['dataclass'], "purple") + "&nbsp;"
            if test_config['temperature'] != "":
                test_run_md += get_badge("temperature", test_config['temperature'], r_to_g=(0,1)) + "&nbsp;"

            test_run_md += get_badge("prompt_file", test_config['prompt_file'] or "prompt.txt", "lightgrey") + "&nbsp;"

            if test_config['legacy_test'] == "false":
                test_run_md += get_badge("active", "yes", "brightgreen")
            else:
                test_run_md += get_badge("active", "no", "red")

            test_run_md += "\n\n\n## Test Runs\n\n"

            table_data = []
            for date in os.listdir(os.path.join("..", "results")):
                for test in os.listdir(os.path.join("..", "results", date)):
                    if test == test_config['id']:
                        score_file = os.path.join("..", "results", date, test, "scoring.json")
                        score_data = read_file(score_file)
                        try:
                            score_data = json.loads(score_data)
                        except json.decoder.JSONDecodeError:
                            score_data = {'Total': 0}

                        score_html = ""
                        for key, value in score_data.items():
                            score_html += get_badge(key, value) + "&nbsp;"

                        table_data.append([date, score_html, "<a href='/humanities_data_benchmark/archive/" + date + "/" + test + "'>Details</a>"])

            test_run_md += create_html_table(["Date", "Results", "Details"], table_data)
            write_file(test_run_file, test_run_md)



def create_tests_overview():
    """Generate an overview of all tests."""
    overview_path = os.path.join(REPORTS_DIR, "tests.md")

    # Markdown Header
    md_string = ("# Test Overview\n\n"
                 "This page provides an overview of all tests. "
                 "Click on the test name to see the detailed results.\n\n")

    table_headers = ["Test", "Name", "Provider", "Model", "Dataclass", "Temperature", "Role Description", "Prompt File", "Legacy Test"]
    table_data = []

    # Read CSV and populate table rows
    with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
        tests = csv.DictReader(csvfile)
        for test_config in tests:

            test_id = test_config['id']
            row_data = [
                get_square(test_id, href="/humanities_data_benchmark/tests/" + test_id),
                f'<a href="/humanities_data_benchmark/benchmarks/{test_config["name"]}/">{test_config["name"]}</a>',
                get_rectangle(test_config['provider']),
                get_rectangle(test_config['model']),
                test_config['dataclass'],
                test_config['temperature'],
                test_config['role_description'],
                test_config['prompt_file'],
                test_config['legacy_test']
            ]
            table_data.append(row_data)

    # Close table and add DataTables script
    md_string += create_html_table(table_headers, table_data)

    # Write to Markdown file
    with open(overview_path, "w", encoding="utf-8") as f:
        f.write(md_string)


def create_benchmark_overview(benchmark_name):
    readme_path = os.path.join(BENCHMARKS_DIR, benchmark_name, "README.md")
    readme_text = read_file(readme_path)

    benchmark_overview_path = os.path.join(REPORTS_DIR, "benchmarks", f"{benchmark_name}.md")
    os.makedirs(os.path.dirname(benchmark_overview_path), exist_ok=True)
    result_overview = f"## Test Results\n\n"

    overview = f"{readme_text}\n\n{result_overview}"
    write_file(benchmark_overview_path, overview)


def generate_site_navigation():
    """Generate site navigation."""
    mkdocs_yml = """
site_name: Humanities Data Benchmark

theme:
  name: material
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.expand
    - toc.integrate
    - search.suggest
    - search.highlight

nav:
  - Home: index.md
  - Tests: 
    - tests.md"""

    for test_ow in os.listdir(os.path.join(REPORTS_DIR, "tests")):
        mkdocs_yml += f"\n    - {test_ow.split(".")[0]}: tests/{test_ow}"

    mkdocs_yml += """\n
  - Benchmarks:"""

    for filename in os.listdir(BENCHMARKS_DIR):
        if not os.path.isdir(os.path.join(BENCHMARKS_DIR, filename)):
            continue
        mkdocs_yml += f"\n    - {filename}: benchmarks/{filename}.md"

    mkdocs_yml += """\n  - Archive:
    - Overview: archive/overview.md"""

    for date in sorted(os.listdir(os.path.join(REPORTS_DIR, "archive")), reverse=True):
        if os.path.isdir(os.path.join(REPORTS_DIR, "archive", date)):
            mkdocs_yml += f"\n    - {date}:"
            for test in os.listdir(os.path.join(REPORTS_DIR, "archive", date)):
                mkdocs_yml += f"\n        - {test.replace('.md', '')}: archive/{date}/{test}"

    mkdocs_yml += """

markdown_extensions:
  - toc:
      permalink: true
  - admonition
  - pymdownx.details
  - pymdownx.superfences
"""
    write_file("../mkdocs.yml", mkdocs_yml)


def add_new_results_to_changelog():
    """Add new test results to CHANGELOG.md under the Added section."""
    import logging
    
    changelog_path = "../CHANGELOG.md"
    results_dir = "../results"
    
    if not os.path.exists(changelog_path) or not os.path.exists(results_dir):
        logging.warning("CHANGELOG.md or results directory not found")
        return
    
    changelog_content = read_file(changelog_path)
    
    # Find existing test entries in changelog
    existing_entries = set()
    for line in changelog_content.split('\n'):
        match = re.search(r'- (T\d+) on (\d{4}-\d{2}-\d{2})', line)
        if match:
            test_id, date = match.groups()
            existing_entries.add(f"{test_id}_{date}")
    
    # Find all test results in results directory (only after 2025-08-25)
    new_entries = []
    cutoff_date = "2025-08-25"
    
    for date_folder in sorted(os.listdir(results_dir)):
        date_path = os.path.join(results_dir, date_folder)
        if not os.path.isdir(date_path):
            continue
            
        # Skip dates that are not later than 2025-08-25
        if date_folder <= cutoff_date:
            continue
            
        for test_id in sorted(os.listdir(date_path)):
            test_path = os.path.join(date_path, test_id)
            if not os.path.isdir(test_path):
                continue
                
            entry_key = f"{test_id}_{date_folder}"
            if entry_key not in existing_entries:
                new_entries.append(f"- {test_id} on {date_folder}")
    
    if not new_entries:
        logging.info("No new test results to add to changelog")
        return
    
    # Find the "### Added" section under "## [Unreleased]"
    lines = changelog_content.split('\n')
    added_section_idx = None
    
    for i, line in enumerate(lines):
        if line.strip() == "### Added" and i > 0:
            # Check if this is under the Unreleased section
            for j in range(i-1, -1, -1):
                if lines[j].startswith("## "):
                    if "[Unreleased]" in lines[j]:
                        added_section_idx = i
                    break
            break
    
    if added_section_idx is None:
        logging.warning("Could not find '### Added' section under [Unreleased] in CHANGELOG.md")
        return
    
    # Insert new entries after the "### Added" line
    insert_idx = added_section_idx + 1
    
    # Skip any existing entries to find the right insertion point
    while (insert_idx < len(lines) and 
           (lines[insert_idx].startswith("- ") or lines[insert_idx].strip() == "")):
        insert_idx += 1
    
    # Insert new entries
    for entry in reversed(new_entries):  # Reverse to maintain chronological order
        lines.insert(insert_idx, entry)
    
    # Write back to changelog
    updated_content = '\n'.join(lines)
    write_file(changelog_path, updated_content)
    
    logging.info(f"Added {len(new_entries)} new entries to CHANGELOG.md")
    for entry in new_entries:
        logging.info(f"  {entry}")


if __name__ == "__main__":
    os.makedirs(REPORTS_DIR, exist_ok=True)
    test_dates = load_test_dates()
    benchmarks = load_all_benchmarks()

    create_index()  # Creates the base file for the reports

    for benchmark in benchmarks:
        create_benchmark_overview(benchmark)   # Generate benchmark overview:
                                               # -> Copies Readme and adds test results

    create_archive_overview(test_dates, benchmarks)
    create_individual_reports()

    create_tests_overview()
    create_test_runs_pages()

    generate_site_navigation()  # Generate mkdocs.yml
    create_index()
    add_new_results_to_changelog()

    logging.info("Reports generated successfully!")
