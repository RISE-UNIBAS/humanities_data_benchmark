import json
import os
import csv
import re
import logging

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
                    if conf['name'] == benchmark:
                        cell += get_square(test, href=f"/archive/{date}/{test}") + "&nbsp;"
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
                                     href=f"/benchmarks/{test_config['name']}") + "&nbsp;"
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

    # Get all available date folders (sorted by date descending)
    table_headers = ["Benchmark", "Latest Results"]
    table_data = []

    # Sort benchmarks alphabetically
    for benchmark in sorted(latest_results.keys()):
        # Add link to the benchmark name with the correct URL path
        benchmark_link = f'<a href="benchmarks/{benchmark}/">{benchmark}</a>'
        row_data = [benchmark_link]

        if len(latest_results[benchmark]) == 0:
            # Skip benchmarks with no results
            continue

        # Create inner table for this benchmark's tests grouped by prompt and rules
        inner_table = '<table class="inner-table" style="width:100%; border-collapse: collapse;">'
        inner_table += '<tr><th style="width:15%;">Prompt</th><th style="width:10%;">Rules</th><th style="width:8%;">ID</th><th style="width:15%;">Model</th><th style="width:12%;">Date</th><th style="width:40%;">Results</th></tr>'
        
        # Process each prompt/rules group
        for group_key in sorted(latest_results[benchmark].keys()):
            prompt_file, rules = group_key.split('|', 1)
            group_tests = latest_results[benchmark][group_key]
            
            # Store test results to sort them later
            test_results = []
            for test_info in group_tests:
                test_id = test_info['id']
                date = test_info['date']
                test_config = test_info['config']
                
                if date is None:
                    # Add entries with no results available with score of -1 (to ensure they appear below entries with score 0)
                    test_results.append((test_id, None, None, "No results available", -1, test_config))
                    continue
                
                # Get test configuration to access model information
                model_info = test_config['model'] if test_config and 'model' in test_config else "unknown"

                scoring_file = os.path.join('..', 'results', date, test_id, 'scoring.json')
                scoring_data = read_file(scoring_file)
                try:
                    scoring_data = json.loads(scoring_data)
                except json.decoder.JSONDecodeError:
                    scoring_data = {'Total': 0}

                badges = []
                score_value = 0
                for key, value in scoring_data.items():
                    badges.append(get_badge(key, value))
                    # Extract numeric value for sorting
                    try:
                        if isinstance(value, (int, float)):
                            score_value = float(value)
                        else:
                            score_value = float(value) if value.replace('.', '', 1).isdigit() else 0
                    except (ValueError, AttributeError):
                        score_value = 0

                badge_html = " ".join(badges)
                test_results.append((test_id, date, model_info, badge_html, score_value, test_config))

            # Sort test results by score value (highest to lowest)
            # For Fraktur benchmark, sort specifically by fuzzy score
            if benchmark == "fraktur":
                # Extract fuzzy score from scoring data for sorting
                fraktur_test_results = []
                for test_id, date, model_info, badge_html, _, test_config in test_results:
                    if date is None:
                        fraktur_test_results.append((test_id, date, model_info, badge_html, -1, test_config))
                        continue
                    
                    scoring_file = os.path.join('..', 'results', date, test_id, 'scoring.json')
                    scoring_data = read_file(scoring_file)
                    try:
                        scoring_data = json.loads(scoring_data)
                        # Use fuzzy score for sorting if available
                        fuzzy_score = scoring_data.get('fuzzy', 0)
                        if isinstance(fuzzy_score, str):
                            fuzzy_score = float(fuzzy_score) if fuzzy_score.replace('.', '', 1).isdigit() else 0
                        fraktur_test_results.append((test_id, date, model_info, badge_html, fuzzy_score, test_config))
                    except (json.decoder.JSONDecodeError, ValueError):
                        fraktur_test_results.append((test_id, date, model_info, badge_html, 0, test_config))
                
                # Replace the original test_results with the fuzzy score sorted version
                test_results = fraktur_test_results
                
            # Sort by the score value (highest to lowest)
            test_results.sort(key=lambda x: x[4], reverse=True)
            
            # Add rows for this group
            first_row = True
            for test_id, date, model_info, badge_html, _, test_config in test_results:
                # Skip entries with no date (no results)
                if date is None:
                    continue
                    
                test_id_html = get_square(test_id, href=f"archive/{date}/{test_id}")
                model_html = get_rectangle(model_info) if model_info else "N/A"
                
                # Display prompt and rules only in the first row of each group
                if first_row:
                    prompt_display = prompt_file if prompt_file else "prompt.txt"
                    rules_display = rules if rules else "None"
                    inner_table += f'<tr><td>{prompt_display}</td><td>{rules_display}</td><td>{test_id_html}</td><td>{model_html}</td><td>{date}</td><td>{badge_html}</td></tr>'
                    first_row = False
                else:
                    inner_table += f'<tr><td></td><td></td><td>{test_id_html}</td><td>{model_html}</td><td>{date}</td><td>{badge_html}</td></tr>'
        
        inner_table += '</table>'
        
        # Skip benchmarks where all tests have no results
        if '<tr><td>' not in inner_table:
            continue
            
        row_data.append(inner_table)
        table_data.append(row_data)


    index_md = f"""
# Humanities Data Benchmark
Welcome to the **Humanities Data Benchmark** report page. This page provides an overview of all benchmark tests, 
results, and comparisons.

## Latest Benchmark Results

{create_html_table(table_headers, table_data)}


## About This Page
This benchmark suite is designed to test **AI models** on humanities data tasks. The tests run **weekly** and 
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
            test_run_md += get_badge("data", test_config['name'], "lightgrey", href=f"/benchmarks/{test_config['name']}") + "&nbsp;"
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

                        table_data.append([date, score_html, "<a href='/archive/" + date + "/" + test + "'>Details</a>"])

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
                get_square(test_id, href="tests/" + test_id),
                f'<a href="/benchmarks/{test_config["name"]}/">{test_config["name"]}</a>',
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
