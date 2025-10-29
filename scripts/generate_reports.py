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
    categories = ['bibliographic_data', 'blacklist', 'company_lists', 'fraktur', 'medieval_manuscripts', 'metadata_extraction', 'zettelkatalog']
    category_labels = ['Bibliographic Data', 'Blacklist', 'Company Lists', 'Fraktur', 'Medieval Manuscripts', 'Metadata Extraction', 'Zettelkatalog']
    
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


def get_provider_display_name(provider, model):
    """
    Get the display name for a provider based on the model.
    Handles special cases for models accessed via intermediaries.
    """
    # Direct provider mappings (existing)
    provider_mappings = {
        'anthropic': 'Anthropic',
        'openai': 'OpenAI',
        'genai': 'Google',
        'mistral': 'Mistral AI'
    }

    # Special model-specific mappings (override provider)
    model_specific_mappings = {
        'meta-llama/llama-4-maverick': 'Meta (via OpenRouter)',
        'qwen/qwen3-vl-8b-thinking': 'Alibaba (via OpenRouter)',
        'qwen/qwen3-vl-30b-a3b-instruct': 'Alibaba (via OpenRouter)',
        'qwen/qwen3-vl-8b-instruct': 'Alibaba (via OpenRouter)',
        'x-ai/grok-4': 'xAI (via OpenRouter)',
        'GLM-4.5V-FP8': 'Z.ai (via sciCORE)'
    }

    # Check if model has a specific mapping first
    if model in model_specific_mappings:
        return model_specific_mappings[model]

    # Fall back to provider mapping
    return provider_mappings.get(provider.lower(), provider)


def create_leaderboard():
    """Create a leaderboard section showing global averages for each model across key benchmarks."""

    # Target benchmarks for global average calculation
    target_benchmarks = ['bibliographic_data', 'blacklist', 'company_lists', 'fraktur', 'medieval_manuscripts', 'metadata_extraction', 'zettelkatalog']

    # Dictionary to store model scores: {model_name: {benchmark: [scores], provider: provider_name, benchmark_costs: {benchmark: [costs]}, benchmark_times: {benchmark: [times]}}}
    model_scores = {}
    
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

            # Collect all test times from answer files in this test to calculate average
            test_result_dir = os.path.join('..', 'results', date, test_id)
            avg_test_time = None
            if os.path.exists(test_result_dir):
                test_times = []
                for answer_file in os.listdir(test_result_dir):
                    if answer_file.endswith('.json') and answer_file != 'scoring.json':
                        answer_path = os.path.join(test_result_dir, answer_file)
                        try:
                            answer_data = json.loads(read_file(answer_path))
                            if 'test_time' in answer_data:
                                test_times.append(float(answer_data['test_time']))
                        except (json.JSONDecodeError, ValueError, KeyError):
                            pass
                if test_times:
                    avg_test_time = sum(test_times) / len(test_times)
            
            # Initialize model entry if not exists
            if model not in model_scores:
                model_scores[model] = {'provider': provider, 'benchmark_costs': {}, 'benchmark_times': {}}
            if benchmark not in model_scores[model]:
                model_scores[model][benchmark] = []
            if benchmark not in model_scores[model]['benchmark_costs']:
                model_scores[model]['benchmark_costs'][benchmark] = []
            if benchmark not in model_scores[model]['benchmark_times']:
                model_scores[model]['benchmark_times'][benchmark] = []
            
            # Extract the main score based on benchmark type
            score = None
            if benchmark == 'bibliographic_data':
                # Use fuzzy score for bibliographic_data
                score = scoring_data.get('fuzzy')
            elif benchmark == 'blacklist':
                # Use fuzzy score for blacklist
                score = scoring_data.get('fuzzy')
            elif benchmark == 'company_lists':
                # Use f1_micro for company_lists
                score = scoring_data.get('f1_micro')
            elif benchmark == 'fraktur':
                # Use fuzzy score for fraktur
                score = scoring_data.get('fuzzy')
            elif benchmark == 'medieval_manuscripts':
                # Use fuzzy score for medieval_manuscripts
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

                    # Extract cost information and store per benchmark
                    if 'cost_summary' in scoring_data and scoring_data['cost_summary'] and 'total_cost_usd' in scoring_data['cost_summary']:
                        try:
                            cost_usd = float(scoring_data['cost_summary']['total_cost_usd'])
                            model_scores[model]['benchmark_costs'][benchmark].append(cost_usd)
                        except (ValueError, TypeError):
                            pass

                    # Store average test time per benchmark (analogous to cost)
                    if avg_test_time is not None:
                        model_scores[model]['benchmark_times'][benchmark].append(avg_test_time)

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
            provider_name = get_provider_display_name(benchmarks.get('provider', ''), model)

            # Calculate normalized cost per point: average of per-benchmark cost/point ratios
            cost_per_point = None
            benchmark_cost_ratios = []

            if 'benchmark_costs' in benchmarks:
                for benchmark_name in target_benchmarks:
                    if (benchmark_name in benchmark_averages and
                        benchmark_averages[benchmark_name] is not None and
                        benchmark_averages[benchmark_name] > 0 and
                        benchmark_name in benchmarks['benchmark_costs'] and
                        benchmarks['benchmark_costs'][benchmark_name]):

                        # Calculate average cost for this benchmark
                        avg_benchmark_cost = sum(benchmarks['benchmark_costs'][benchmark_name]) / len(benchmarks['benchmark_costs'][benchmark_name])
                        # Calculate cost per point for this benchmark
                        benchmark_cost_ratio = avg_benchmark_cost / benchmark_averages[benchmark_name]
                        benchmark_cost_ratios.append(benchmark_cost_ratio)

                # Average the per-benchmark cost/point ratios
                if benchmark_cost_ratios:
                    cost_per_point = sum(benchmark_cost_ratios) / len(benchmark_cost_ratios)

            # Calculate normalized time per point: average of per-benchmark time/point ratios
            time_per_point = None
            benchmark_time_ratios = []

            if 'benchmark_times' in benchmarks:
                for benchmark_name in target_benchmarks:
                    if (benchmark_name in benchmark_averages and
                        benchmark_averages[benchmark_name] is not None and
                        benchmark_averages[benchmark_name] > 0 and
                        benchmark_name in benchmarks['benchmark_times'] and
                        benchmarks['benchmark_times'][benchmark_name]):

                        # Calculate average time for this benchmark
                        avg_benchmark_time = sum(benchmarks['benchmark_times'][benchmark_name]) / len(benchmarks['benchmark_times'][benchmark_name])
                        # Calculate time per point for this benchmark
                        benchmark_time_ratio = avg_benchmark_time / benchmark_averages[benchmark_name]
                        benchmark_time_ratios.append(benchmark_time_ratio)

                # Average the per-benchmark time/point ratios
                if benchmark_time_ratios:
                    time_per_point = sum(benchmark_time_ratios) / len(benchmark_time_ratios)

            leaderboard_data.append({
                'model': model,
                'provider': provider_name,
                'global_avg': global_average,
                'cost_per_point': cost_per_point,
                'time_per_point': time_per_point,
                'bibliographic_data': benchmark_averages['bibliographic_data'],
                'blacklist': benchmark_averages['blacklist'],
                'company_lists': benchmark_averages['company_lists'],
                'fraktur': benchmark_averages['fraktur'],
                'medieval_manuscripts': benchmark_averages['medieval_manuscripts'],
                'metadata_extraction': benchmark_averages['metadata_extraction'],
                'zettelkatalog': benchmark_averages['zettelkatalog']
            })
    
    # Sort by global average (highest first)
    leaderboard_data.sort(key=lambda x: x['global_avg'], reverse=True)

    # Create leaderboard HTML table
    if not leaderboard_data:
        return "<p>No leaderboard data available.</p>", []
    
    leaderboard_html = '''<div>
<table id="leaderboard-table" style="width:100%; border-collapse: collapse; margin-bottom: 20px;">
<thead>
<tr>
<th onclick="sortTable(0)" style="cursor: pointer;">Model ↕</th>
<th onclick="sortTable(1)" style="cursor: pointer;">Provider ↕</th>
<th onclick="sortTable(2)" style="cursor: pointer;">Global Average ↕</th>
<th onclick="sortTable(3)" style="cursor: pointer;">Cost/Point ↕</th>
<th onclick="sortTable(4)" style="cursor: pointer;">Time/Point ↕</th>
<th onclick="sortTable(5)" style="cursor: pointer;"><a href="benchmarks/bibliographic_data/" style="color: inherit; text-decoration: none;">bibliographic_data</a> ↕</th>
<th onclick="sortTable(6)" style="cursor: pointer;"><a href="benchmarks/blacklist/" style="color: inherit; text-decoration: none;">blacklist</a> ↕</th>
<th onclick="sortTable(7)" style="cursor: pointer;"><a href="benchmarks/company_lists/" style="color: inherit; text-decoration: none;">company_lists</a> ↕</th>
<th onclick="sortTable(8)" style="cursor: pointer;"><a href="benchmarks/fraktur/" style="color: inherit; text-decoration: none;">fraktur</a> ↕</th>
<th onclick="sortTable(9)" style="cursor: pointer;"><a href="benchmarks/medieval_manuscripts/" style="color: inherit; text-decoration: none;">medieval_manuscripts</a> ↕</th>
<th onclick="sortTable(10)" style="cursor: pointer;"><a href="benchmarks/metadata_extraction/" style="color: inherit; text-decoration: none;">metadata_extraction</a> ↕</th>
<th onclick="sortTable(11)" style="cursor: pointer;"><a href="benchmarks/zettelkatalog/" style="color: inherit; text-decoration: none;">zettelkatalog</a> ↕</th>
</tr>
</thead>
<tbody>'''
    
    for rank, data in enumerate(leaderboard_data, 1):
        model_html = get_rectangle(data['model'])
        provider_html = get_rectangle(data['provider'])
        global_avg_display = f"{data['global_avg']:.3f}"

        # Create cost per point display (without badge)
        cost_per_point_display = "N/A"
        cost_per_point_sort = "999"  # High value for N/A entries to sort last
        if data['cost_per_point'] is not None:
            cost_per_point_display = f"${data['cost_per_point']:.4f}"
            cost_per_point_sort = f"{data['cost_per_point']:.4f}"

        # Create time per point display (without badge)
        time_per_point_display = "N/A"
        time_per_point_sort = "999999"  # High value for N/A entries to sort last
        if data['time_per_point'] is not None:
            time_per_point_display = f"{data['time_per_point']:.2f}s"
            time_per_point_sort = f"{data['time_per_point']:.2f}"

        biblio_badge = get_badge("fuzzy", f"{data['bibliographic_data']:.3f}") if data['bibliographic_data'] is not None else "N/A"
        blacklist_badge = get_badge("fuzzy", f"{data['blacklist']:.3f}") if data['blacklist'] is not None else "N/A"
        company_lists_badge = get_badge("f1_micro", f"{data['company_lists']:.3f}") if data['company_lists'] is not None else "N/A"
        fraktur_badge = get_badge("fuzzy", f"{data['fraktur']:.3f}") if data['fraktur'] is not None else "N/A"
        medieval_manuscripts_badge = get_badge("fuzzy", f"{data['medieval_manuscripts']:.3f}") if data['medieval_manuscripts'] is not None else "N/A"
        metadata_badge = get_badge("f1_micro", f"{data['metadata_extraction']:.3f}") if data['metadata_extraction'] is not None else "N/A"
        zettelkatalog_badge = get_badge("f1_micro", f"{data['zettelkatalog']:.3f}") if data['zettelkatalog'] is not None else "N/A"

        biblio_sort = f'{data["bibliographic_data"]:.3f}' if data["bibliographic_data"] is not None else "0"
        blacklist_sort = f'{data["blacklist"]:.3f}' if data["blacklist"] is not None else "0"
        company_lists_sort = f'{data["company_lists"]:.3f}' if data["company_lists"] is not None else "0"
        fraktur_sort = f'{data["fraktur"]:.3f}' if data["fraktur"] is not None else "0"
        medieval_manuscripts_sort = f'{data["medieval_manuscripts"]:.3f}' if data["medieval_manuscripts"] is not None else "0"
        metadata_sort = f'{data["metadata_extraction"]:.3f}' if data["metadata_extraction"] is not None else "0"
        zettelkatalog_sort = f'{data["zettelkatalog"]:.3f}' if data["zettelkatalog"] is not None else "0"
        
        leaderboard_html += f'<tr><td data-sort="{data["model"]}">{model_html}</td><td data-sort="{data["provider"]}">{provider_html}</td><td data-sort="{data["global_avg"]:.3f}">{global_avg_display}</td><td data-sort="{cost_per_point_sort}">{cost_per_point_display}</td><td data-sort="{time_per_point_sort}">{time_per_point_display}</td><td data-sort="{biblio_sort}">{biblio_badge}</td><td data-sort="{blacklist_sort}">{blacklist_badge}</td><td data-sort="{company_lists_sort}">{company_lists_badge}</td><td data-sort="{fraktur_sort}">{fraktur_badge}</td><td data-sort="{medieval_manuscripts_sort}">{medieval_manuscripts_badge}</td><td data-sort="{metadata_sort}">{metadata_badge}</td><td data-sort="{zettelkatalog_sort}">{zettelkatalog_badge}</td></tr>'
    
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
<th onclick="sortBenchmarkTable('{benchmark}', 8)" style="cursor: pointer;">Cost/Point ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 9)" style="cursor: pointer;">Test Time (s) ↕</th>
<th onclick="sortBenchmarkTable('{benchmark}', 10)" style="cursor: pointer;">Time/Point ↕</th>
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
                if benchmark == 'bibliographic_data' or benchmark == 'blacklist' or benchmark == 'fraktur' or benchmark == 'medieval_manuscripts':
                    score_value = scoring_data.get('fuzzy', 0)
                elif benchmark == 'company_lists' or benchmark == 'metadata_extraction' or benchmark == 'zettelkatalog':
                    score_value = scoring_data.get('f1_micro', 0)
                
                try:
                    score_value = float(score_value) if score_value else 0
                except (ValueError, TypeError):
                    score_value = 0

                # Show appropriate score with 3 decimal places as badge based on benchmark type
                badge_html = "N/A"
                if benchmark == 'company_lists' or benchmark == 'metadata_extraction' or benchmark == 'zettelkatalog':
                    # Use f1_micro for company_lists, metadata_extraction and zettelkatalog
                    if 'f1_micro' in scoring_data:
                        f1_value = scoring_data['f1_micro']
                        try:
                            f1_float = float(f1_value) if f1_value else 0
                            badge_html = get_badge('f1_micro', f"{f1_float:.3f}")
                        except (ValueError, TypeError):
                            badge_html = "N/A"
                else:
                    # Use fuzzy for bibliographic_data, blacklist, fraktur, medieval_manuscripts, and other benchmarks
                    if 'fuzzy' in scoring_data:
                        fuzzy_value = scoring_data['fuzzy']
                        try:
                            fuzzy_float = float(fuzzy_value) if fuzzy_value else 0
                            badge_html = get_badge('fuzzy', f"{fuzzy_float:.3f}")
                        except (ValueError, TypeError):
                            badge_html = "N/A"

                # Extract cost information
                cost_html = "N/A"
                cost_per_point_html = "N/A"
                cost_per_point_sort = "999"
                if 'cost_summary' in scoring_data and scoring_data['cost_summary'] and 'total_cost_usd' in scoring_data['cost_summary']:
                    try:
                        cost_usd = float(scoring_data['cost_summary']['total_cost_usd'])
                        cost_html = f"${cost_usd:.4f}"

                        # Calculate cost per point for this test
                        if score_value > 0:
                            cost_per_point = cost_usd / score_value
                            cost_per_point_html = f"${cost_per_point:.4f}"
                            cost_per_point_sort = f"{cost_per_point:.4f}"
                    except (ValueError, TypeError):
                        cost_html = "N/A"

                # Extract test time information from answer files
                test_time_html = "N/A"
                time_per_point_html = "N/A"
                time_per_point_sort = "999999"
                test_result_dir = os.path.join('..', 'results', date, test_id)
                if os.path.exists(test_result_dir):
                    test_times = []
                    for answer_file in os.listdir(test_result_dir):
                        if answer_file.endswith('.json') and answer_file != 'scoring.json':
                            answer_path = os.path.join(test_result_dir, answer_file)
                            try:
                                answer_data = json.loads(read_file(answer_path))
                                if 'test_time' in answer_data:
                                    test_times.append(float(answer_data['test_time']))
                            except (json.JSONDecodeError, ValueError, KeyError):
                                pass

                    if test_times:
                        total_test_time = sum(test_times)
                        test_time_html = f"{total_test_time:.2f}"

                        # Calculate time per point for this test
                        if score_value > 0:
                            time_per_point = total_test_time / score_value
                            time_per_point_html = f"{time_per_point:.2f}"
                            time_per_point_sort = f"{time_per_point:.2f}"

                all_tests.append({
                    'test_id': test_id,
                    'model': test_config['model'],
                    'provider': test_config['provider'],
                    'date': date,
                    'prompt': prompt_file if prompt_file else "prompt.txt",
                    'rules': rules if rules else "None",
                    'badges': badge_html,
                    'cost': cost_html,
                    'cost_per_point': cost_per_point_html,
                    'cost_per_point_sort': cost_per_point_sort,
                    'test_time': test_time_html,
                    'time_per_point': time_per_point_html,
                    'time_per_point_sort': time_per_point_sort,
                    'score': score_value
                })
        
        # Sort by score (highest first)
        all_tests.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rows to table
        for test in all_tests:
            model_html = get_rectangle(test['model'])

            # Use get_provider_display_name for consistent provider naming
            provider_display = get_provider_display_name(test['provider'], test['model'])
            provider_html = get_rectangle(provider_display)
            
            # Create rules cell (always expanded)
            if test['rules'] and test['rules'].strip() and test['rules'] != "None":
                rules_display = f'''<div style="padding: 5px; background-color: #f5f5f5; border-radius: 3px; font-size: 0.9em; white-space: pre-wrap; max-width: 200px; overflow-wrap: break-word;">{test['rules']}</div>'''
            else:
                rules_display = "None"
            
            # Create clickable test ID using get_square for consistent styling
            test_id_square = get_square(test["test_id"], href="/humanities_data_benchmark/tests/" + test["test_id"])

            benchmark_table += f'<tr><td data-sort="{test["model"]}">{model_html}</td><td data-sort="{provider_display}">{provider_html}</td><td data-sort="{test["test_id"]}">{test_id_square}</td><td data-sort="{test["date"]}">{test["date"]}</td><td data-sort="{test["prompt"]}">{test["prompt"]}</td><td data-sort="{test["rules"] if test["rules"] != "None" else ""}">{rules_display}</td><td data-sort="{test["score"]:.3f}">{test["badges"]}</td><td data-sort="{test["cost"]}">{test["cost"]}</td><td data-sort="{test["cost_per_point_sort"]}">{test["cost_per_point"]}</td><td data-sort="{test["test_time"]}">{test["test_time"]}</td><td data-sort="{test["time_per_point_sort"]}">{test["time_per_point"]}</td></tr>'
        
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

The table below shows the **global average performance**, **cost efficiency**, and **time efficiency** of each model
across the seven core benchmarks: [bibliographic_data](benchmarks/bibliographic_data/), [blacklist](
benchmarks/blacklist/), [company_lists](benchmarks/company_lists/), [fraktur](benchmarks/fraktur/),
[medieval_manuscripts](benchmarks/medieval_manuscripts/), [metadata_extraction](benchmarks/metadata_extraction/),
and [zettelkatalog](benchmarks/zettelkatalog/).

The **Model** and **Provider** columns identify each AI system. **Global Average** represents the mean performance
score across all seven benchmarks (higher is better). **Cost/Point** and **Time/Point** show normalized efficiency
metrics calculated per test, averaged per benchmark, then averaged globally; this multi-level normalization accounts
for different numbers of items, test configurations, and benchmark scales. For efficiency metrics, lower values are
better, indicating less cost or time needed per performance point achieved. The seven benchmark-specific columns show
average performance for each individual benchmark. Only models with results in all seven benchmarks are included.
Click on any column header to sort the table.

{leaderboard_html}

The following radar chart shows the performance distribution of top models across the seven core benchmarks:

{radar_chart_html}

## Latest Benchmark Results

The tables below show detailed results for each benchmark, with each row representing a single test configuration run 
on the most recent date. The **Model** and **Provider** columns identify the AI system used. Each test has a unique 
**Test ID** (click to see full history) and shows the most recent execution **Date**. The **Prompt** and **Rules** 
columns indicate the configuration used. **Results** show the performance score (fuzzy match for 
bibliographic_data/fraktur, F1-micro for metadata_extraction/zettelkatalog; higher is better). **Cost (USD)** 
represents the total cost for processing all items in the test. **Cost/Point** shows cost efficiency ($/performance 
point; lower is better). **Test Time (s)** is the total execution time for all items. **Time/Point** shows time 
efficiency (seconds/performance point; lower is better).

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

    logging.info("Reports generated successfully!")
