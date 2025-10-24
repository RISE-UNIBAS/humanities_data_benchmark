"""Generate Plotly visualization configs for benchmark data.

This module creates ready-to-use Plotly figure dictionaries that can be:
- Rendered interactively in browser with plotly.js
- Exported to static images (PNG, SVG) with plotly.io
"""

import json
from pathlib import Path
from collections import defaultdict

EXPORT_PATH = Path("../../ndr_export")
PRICING_PATH = Path("../../scripts/data/pricing.json")

# Color palettes
PROVIDER_COLORS = {
    "openai": "#10A37F",
    "anthropic": "#D4A373",
    "google": "#4285F4",
    "cohere": "#39594D",
    "mistral": "#FF7000",
    "meta": "#0668E1",
    "huggingface": "#FFD21E"
}

DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]


def load_benchmark_export():
    """Load the benchmark export JSON file."""
    export_file = EXPORT_PATH / "benchmark_export.json"
    if not export_file.exists():
        raise FileNotFoundError(f"Benchmark export not found: {export_file}")

    with open(export_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_pricing_data():
    """Load and parse pricing data, returning latest prices per model."""
    if not PRICING_PATH.exists():
        print(f"Warning: Pricing file not found: {PRICING_PATH}")
        return {}

    with open(PRICING_PATH, 'r', encoding='utf-8') as f:
        pricing_data = json.load(f)

    # Flatten pricing to get latest price for each model
    # Structure: {model_name: {"input": X, "output": Y, "provider": Z}}
    model_pricing = {}

    # Get dates sorted (most recent first)
    dates = sorted(pricing_data.get("pricing", {}).keys(), reverse=True)

    for date in dates:
        date_pricing = pricing_data["pricing"][date]
        for provider, models in date_pricing.items():
            for model_name, prices in models.items():
                # Only add if not already present (we want most recent)
                if model_name not in model_pricing:
                    model_pricing[model_name] = {
                        "input": prices.get("input_price", 0),
                        "output": prices.get("output_price", 0),
                        "provider": provider
                    }

    return model_pricing


def create_scatter_time_series(benchmark_data):
    """Create a scatter plot showing performance over time for a benchmark.

    Args:
        benchmark_data: Single benchmark dict with test_runs

    Returns:
        Plotly figure dictionary
    """
    benchmark_name = benchmark_data.get("name", "Unknown")
    test_runs = benchmark_data.get("test_runs", [])

    # Group by model for separate traces
    model_data = defaultdict(lambda: {"dates": [], "scores": [], "provider": None})

    for run in test_runs:
        if run.get("normalized_score") is None:
            continue

        model = run.get("model", "Unknown")
        model_data[model]["dates"].append(run.get("date"))
        model_data[model]["scores"].append(run.get("normalized_score"))
        if model_data[model]["provider"] is None:
            model_data[model]["provider"] = run.get("provider")

    # Create traces
    traces = []
    for idx, (model, data) in enumerate(sorted(model_data.items())):
        provider = data["provider"]
        color = PROVIDER_COLORS.get(provider, DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])

        traces.append({
            "type": "scatter",
            "mode": "markers+lines",
            "x": data["dates"],
            "y": data["scores"],
            "name": model,
            "marker": {
                "size": 8,
                "color": color,
                "line": {"width": 1, "color": "white"}
            },
            "line": {
                "width": 2,
                "color": color
            },
            "hovertemplate": "<b>%{fullData.name}</b><br>Date: %{x}<br>Score: %{y:.1f}<extra></extra>"
        })

    # Layout
    layout = {
        "title": {
            "text": f"<b>{benchmark_data.get('title_short', benchmark_name)}</b> - Performance Over Time",
            "font": {"size": 18}
        },
        "xaxis": {
            "title": "Date",
            "type": "date",
            "showgrid": True,
            "gridcolor": "#E5E5E5"
        },
        "yaxis": {
            "title": "Normalized Score (0-100)",
            "range": [0, 105],
            "showgrid": True,
            "gridcolor": "#E5E5E5"
        },
        "plot_bgcolor": "#FAFAFA",
        "paper_bgcolor": "white",
        "hovermode": "closest",
        "showlegend": True,
        "legend": {
            "orientation": "v",
            "yanchor": "top",
            "y": 1,
            "xanchor": "left",
            "x": 1.02
        },
        "margin": {"l": 60, "r": 150, "t": 60, "b": 60}
    }

    return {
        "data": traces,
        "layout": layout
    }


def create_heatmap_benchmarks_models(benchmarks_data):
    """Create a heatmap showing benchmark × model performance.

    Args:
        benchmarks_data: List of all benchmark dicts

    Returns:
        Plotly figure dictionary
    """
    # Collect all models and benchmarks
    all_models = set()
    benchmark_names = []
    benchmark_titles = {}

    for benchmark in benchmarks_data:
        if benchmark.get("display", True) == False:  # Skip hidden benchmarks
            continue

        benchmark_name = benchmark.get("name")
        benchmark_names.append(benchmark_name)
        benchmark_titles[benchmark_name] = benchmark.get("title_short", benchmark_name)

        for run in benchmark.get("test_runs", []):
            if run.get("model"):
                all_models.add(run.get("model"))

    all_models = sorted(all_models)

    # Build matrix: benchmark_names × all_models
    # Calculate average score for each benchmark-model combination
    matrix = []
    hover_text = []

    for benchmark_name in benchmark_names:
        benchmark = next((b for b in benchmarks_data if b.get("name") == benchmark_name), None)
        if not benchmark:
            continue

        row = []
        hover_row = []

        for model in all_models:
            # Find all runs for this benchmark-model combo
            runs = [r for r in benchmark.get("test_runs", [])
                   if r.get("model") == model and r.get("normalized_score") is not None]

            if runs:
                avg_score = sum(r["normalized_score"] for r in runs) / len(runs)
                row.append(avg_score)
                hover_row.append(f"<b>{benchmark_titles[benchmark_name]}</b><br>" +
                               f"Model: {model}<br>" +
                               f"Avg Score: {avg_score:.1f}<br>" +
                               f"Runs: {len(runs)}")
            else:
                row.append(None)
                hover_row.append(f"<b>{benchmark_titles[benchmark_name]}</b><br>" +
                               f"Model: {model}<br>No data")

        matrix.append(row)
        hover_text.append(hover_row)

    # Create heatmap trace
    trace = {
        "type": "heatmap",
        "z": matrix,
        "x": all_models,
        "y": [benchmark_titles[name] for name in benchmark_names],
        "colorscale": [
            [0, "#fee5d9"],
            [0.25, "#fcae91"],
            [0.5, "#fb6a4a"],
            [0.75, "#de2d26"],
            [1, "#a50f15"]
        ],
        "zmin": 0,
        "zmax": 100,
        "text": hover_text,
        "hovertemplate": "%{text}<extra></extra>",
        "colorbar": {
            "title": "Score",
            "thickness": 15,
            "len": 0.7
        }
    }

    # Layout
    layout = {
        "title": {
            "text": "<b>Benchmark × Model Performance</b>",
            "font": {"size": 20}
        },
        "xaxis": {
            "title": "Model",
            "tickangle": -45,
            "side": "bottom"
        },
        "yaxis": {
            "title": "Benchmark",
            "autorange": "reversed"
        },
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "margin": {"l": 150, "r": 80, "t": 80, "b": 150}
    }

    return {
        "data": [trace],
        "layout": layout
    }


def create_box_plot_by_provider(benchmarks_data):
    """Create box plots showing score distribution by provider.

    Args:
        benchmarks_data: List of all benchmark dicts

    Returns:
        Plotly figure dictionary
    """
    # Collect scores by provider
    provider_scores = defaultdict(list)

    for benchmark in benchmarks_data:
        if benchmark.get("display", True) == False:  # Skip hidden benchmarks
            continue

        for run in benchmark.get("test_runs", []):
            provider = run.get("provider")
            score = run.get("normalized_score")
            if provider and score is not None:
                provider_scores[provider].append(score)

    # Create box plot traces
    traces = []
    for provider in sorted(provider_scores.keys()):
        color = PROVIDER_COLORS.get(provider, "#888888")

        traces.append({
            "type": "box",
            "y": provider_scores[provider],
            "name": provider.capitalize(),
            "marker": {
                "color": color
            },
            "boxmean": "sd",  # Show mean and standard deviation
            "hovertemplate": "<b>%{fullData.name}</b><br>Score: %{y:.1f}<extra></extra>"
        })

    # Layout
    layout = {
        "title": {
            "text": "<b>Score Distribution by Provider</b>",
            "font": {"size": 20}
        },
        "yaxis": {
            "title": "Normalized Score (0-100)",
            "range": [0, 105],
            "showgrid": True,
            "gridcolor": "#E5E5E5"
        },
        "xaxis": {
            "title": "Provider"
        },
        "plot_bgcolor": "#FAFAFA",
        "paper_bgcolor": "white",
        "showlegend": False,
        "margin": {"l": 60, "r": 40, "t": 80, "b": 60}
    }

    return {
        "data": traces,
        "layout": layout
    }


def create_bar_chart_benchmark_difficulty(benchmarks_data):
    """Create bar chart showing average performance by benchmark (difficulty ranking).

    Args:
        benchmarks_data: List of all benchmark dicts

    Returns:
        Plotly figure dictionary
    """
    benchmark_stats = []

    for benchmark in benchmarks_data:
        if benchmark.get("display", True) == False:  # Skip hidden benchmarks
            continue

        scores = [r["normalized_score"] for r in benchmark.get("test_runs", [])
                 if r.get("normalized_score") is not None]

        if scores:
            avg_score = sum(scores) / len(scores)
            benchmark_stats.append({
                "name": benchmark.get("title_short", benchmark.get("name")),
                "avg_score": avg_score,
                "count": len(scores)
            })

    # Sort by average score
    benchmark_stats.sort(key=lambda x: x["avg_score"])

    # Create bar trace
    trace = {
        "type": "bar",
        "x": [b["avg_score"] for b in benchmark_stats],
        "y": [b["name"] for b in benchmark_stats],
        "orientation": "h",
        "marker": {
            "color": [b["avg_score"] for b in benchmark_stats],
            "colorscale": [
                [0, "#fee5d9"],
                [0.5, "#fb6a4a"],
                [1, "#a50f15"]
            ],
            "cmin": 0,
            "cmax": 100,
            "showscale": True,
            "colorbar": {
                "title": "Avg Score",
                "thickness": 15,
                "len": 0.5
            }
        },
        "text": [f"{b['avg_score']:.1f} ({b['count']} runs)" for b in benchmark_stats],
        "textposition": "outside",
        "hovertemplate": "<b>%{y}</b><br>Avg Score: %{x:.1f}<extra></extra>"
    }

    # Layout
    layout = {
        "title": {
            "text": "<b>Benchmark Difficulty Ranking</b><br><sub>Average normalized score (lower = harder)</sub>",
            "font": {"size": 20}
        },
        "xaxis": {
            "title": "Average Normalized Score",
            "range": [0, 105],
            "showgrid": True,
            "gridcolor": "#E5E5E5"
        },
        "yaxis": {
            "title": ""
        },
        "plot_bgcolor": "#FAFAFA",
        "paper_bgcolor": "white",
        "margin": {"l": 200, "r": 100, "t": 100, "b": 60}
    }

    return {
        "data": [trace],
        "layout": layout
    }


def create_radar_chart_providers(benchmarks_data):
    """Create a radar/spider chart comparing providers across benchmarks.

    Args:
        benchmarks_data: List of all benchmark dicts

    Returns:
        Plotly figure dictionary
    """
    # Filter benchmarks: only those that are displayed and not excluded from leaderboard
    included_benchmarks = []
    for benchmark in benchmarks_data:
        if benchmark.get("display", True) == False:
            continue
        if benchmark.get("exclude_from_leaderboard", False):
            continue
        included_benchmarks.append(benchmark)

    if not included_benchmarks:
        # Return empty figure if no benchmarks
        return {"data": [], "layout": {"title": "No benchmarks available"}}

    # Calculate average score per provider per benchmark
    # Structure: {provider: {benchmark_name: [scores]}}
    provider_benchmark_scores = defaultdict(lambda: defaultdict(list))

    for benchmark in included_benchmarks:
        benchmark_name = benchmark.get("name")
        for run in benchmark.get("test_runs", []):
            provider = run.get("provider")
            score = run.get("normalized_score")
            if provider and score is not None:
                provider_benchmark_scores[provider][benchmark_name].append(score)

    # Calculate averages
    provider_averages = {}  # {provider: {benchmark_name: avg_score, ...}}

    for provider, benchmark_scores in provider_benchmark_scores.items():
        provider_averages[provider] = {}
        for benchmark_name, scores in benchmark_scores.items():
            avg = sum(scores) / len(scores)
            provider_averages[provider][benchmark_name] = avg

    # Prepare benchmark names and titles
    benchmark_names = [b.get("name") for b in included_benchmarks]
    benchmark_titles = [b.get("title_short", b.get("name")) for b in included_benchmarks]

    # Create traces for each provider
    traces = []
    for idx, provider in enumerate(sorted(provider_averages.keys())):
        # Get scores for this provider across all benchmarks
        r_values = []
        for benchmark_name in benchmark_names:
            score = provider_averages[provider].get(benchmark_name, 0)  # 0 if provider didn't run on this benchmark
            r_values.append(score)

        # Close the polygon by repeating the first value
        theta = benchmark_titles + [benchmark_titles[0]]
        r = r_values + [r_values[0]]

        color = PROVIDER_COLORS.get(provider, DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])

        # Capitalize provider name for display
        provider_display = provider.capitalize()
        if provider in ["openai", "anthropic", "google", "meta"]:
            provider_display = {
                "openai": "OpenAI",
                "anthropic": "Anthropic",
                "google": "Google",
                "meta": "Meta"
            }[provider]

        traces.append({
            "type": "scatterpolar",
            "r": r,
            "theta": theta,
            "fill": "toself",
            "name": provider_display,
            "line": {
                "color": color,
                "width": 2
            },
            "marker": {
                "size": 8,
                "color": color
            },
            "opacity": 0.6,
            "hovertemplate": "<b>%{fullData.name}</b><br>%{theta}: %{r:.1f}<extra></extra>"
        })

    # Layout
    layout = {
        "title": {
            "text": "<b>Provider Performance Comparison</b><br><sub>Average scores across all models per provider</sub>",
            "font": {"size": 20}
        },
        "polar": {
            "radialaxis": {
                "visible": True,
                "range": [0, 100],
                "showline": True,
                "linewidth": 1,
                "gridcolor": "#E5E5E5"
            },
            "angularaxis": {
                "direction": "clockwise",
                "period": len(benchmark_titles)
            },
            "bgcolor": "#FAFAFA"
        },
        "showlegend": True,
        "legend": {
            "orientation": "v",
            "yanchor": "middle",
            "y": 0.5,
            "xanchor": "left",
            "x": 1.1,
            "font": {"size": 14}
        },
        "paper_bgcolor": "white",
        "margin": {"l": 80, "r": 200, "t": 120, "b": 80}
    }

    return {
        "data": traces,
        "layout": layout
    }


def create_cost_effectiveness_scatter(benchmarks_data, pricing_data):
    """Create a scatter plot showing cost-effectiveness (performance vs cost).

    Args:
        benchmarks_data: List of all benchmark dicts
        pricing_data: Dict of model pricing information

    Returns:
        Plotly figure dictionary
    """
    # Filter benchmarks
    included_benchmarks = []
    for benchmark in benchmarks_data:
        if benchmark.get("display", True) == False:
            continue
        if benchmark.get("exclude_from_leaderboard", False):
            continue
        included_benchmarks.append(benchmark)

    # Calculate average score per model across all benchmarks
    model_scores = defaultdict(list)
    model_providers = {}

    for benchmark in included_benchmarks:
        for run in benchmark.get("test_runs", []):
            model = run.get("model")
            score = run.get("normalized_score")
            provider = run.get("provider")
            if model and score is not None:
                model_scores[model].append(score)
                if model not in model_providers:
                    model_providers[model] = provider

    # Calculate model statistics and costs
    model_stats = []

    # Assume typical task: 1000 input tokens + 2000 output tokens
    # Cost is in $ per 1M tokens, so divide by 1000 to get per-task cost
    TYPICAL_INPUT_TOKENS = 1000
    TYPICAL_OUTPUT_TOKENS = 2000

    for model, scores in model_scores.items():
        if not scores:
            continue

        avg_score = sum(scores) / len(scores)
        provider = model_providers.get(model)

        # Get pricing for this model
        pricing = pricing_data.get(model)
        if not pricing:
            # Skip models without pricing data
            continue

        input_price = pricing["input"]
        output_price = pricing["output"]

        # Calculate estimated cost per task in cents
        estimated_cost = (
            (input_price * TYPICAL_INPUT_TOKENS / 1_000_000) +
            (output_price * TYPICAL_OUTPUT_TOKENS / 1_000_000)
        ) * 100  # Convert to cents for readability

        model_stats.append({
            "model": model,
            "avg_score": avg_score,
            "estimated_cost_cents": estimated_cost,
            "provider": provider,
            "num_runs": len(scores),
            "input_price": input_price,
            "output_price": output_price
        })

    if not model_stats:
        return {"data": [], "layout": {"title": "No data available for cost-effectiveness analysis"}}

    # Create scatter plot
    traces = []

    # Group by provider for better legend
    by_provider = defaultdict(list)
    for stat in model_stats:
        by_provider[stat["provider"]].append(stat)

    for provider in sorted(by_provider.keys()):
        models = by_provider[provider]

        x_values = [m["estimated_cost_cents"] for m in models]
        y_values = [m["avg_score"] for m in models]
        sizes = [min(m["num_runs"] * 2, 50) + 10 for m in models]  # Scale size by runs
        model_names = [m["model"] for m in models]

        # Create hover text
        hover_texts = []
        for m in models:
            hover_texts.append(
                f"<b>{m['model']}</b><br>" +
                f"Avg Score: {m['avg_score']:.1f}<br>" +
                f"Est. Cost: {m['estimated_cost_cents']:.2f}¢<br>" +
                f"Runs: {m['num_runs']}<br>" +
                f"Input: ${m['input_price']:.2f}/1M<br>" +
                f"Output: ${m['output_price']:.2f}/1M"
            )

        color = PROVIDER_COLORS.get(provider, "#888888")

        # Capitalize provider name
        provider_display = provider.capitalize()
        if provider in ["openai", "anthropic", "google", "meta"]:
            provider_display = {
                "openai": "OpenAI",
                "anthropic": "Anthropic",
                "google": "Google",
                "meta": "Meta"
            }[provider]

        traces.append({
            "type": "scatter",
            "mode": "markers",
            "x": x_values,
            "y": y_values,
            "name": provider_display,
            "text": model_names,
            "hovertext": hover_texts,
            "hoverinfo": "text",
            "marker": {
                "size": sizes,
                "color": color,
                "opacity": 0.7,
                "line": {
                    "width": 2,
                    "color": "white"
                }
            }
        })

    # Layout
    layout = {
        "title": {
            "text": "<b>Cost-Effectiveness Analysis</b><br>" +
                   "<sub>Performance vs. Estimated Cost (1k input + 2k output tokens)</sub>",
            "font": {"size": 20}
        },
        "xaxis": {
            "title": "Estimated Cost per Task (¢)",
            "type": "log",  # Log scale for better visualization
            "showgrid": True,
            "gridcolor": "#E5E5E5"
        },
        "yaxis": {
            "title": "Average Normalized Score (0-100)",
            "range": [0, 105],
            "showgrid": True,
            "gridcolor": "#E5E5E5"
        },
        "plot_bgcolor": "#FAFAFA",
        "paper_bgcolor": "white",
        "hovermode": "closest",
        "showlegend": True,
        "legend": {
            "orientation": "v",
            "yanchor": "top",
            "y": 1,
            "xanchor": "left",
            "x": 1.02
        },
        "annotations": [
            {
                "text": "← Better value",
                "x": 0.02,
                "y": 0.98,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 12, "color": "#666"},
                "align": "left"
            }
        ],
        "margin": {"l": 60, "r": 150, "t": 100, "b": 60}
    }

    return {
        "data": traces,
        "layout": layout
    }


def create_speed_performance_scatter(benchmarks_data):
    """Create a scatter plot showing speed vs performance.

    Args:
        benchmarks_data: List of all benchmark dicts

    Returns:
        Plotly figure dictionary
    """
    # We need to load test run results to get timing data
    # Since test_runs in benchmark_export don't have timing, we need to access results
    from pathlib import Path

    RESULTS_PATH = Path("../../results")

    # Filter benchmarks
    included_benchmarks = []
    for benchmark in benchmarks_data:
        if benchmark.get("display", True) == False:
            continue
        if benchmark.get("exclude_from_leaderboard", False):
            continue
        included_benchmarks.append(benchmark)

    # Calculate average score and speed per model across all benchmarks
    model_data = defaultdict(lambda: {"scores": [], "times": [], "provider": None})

    for benchmark in included_benchmarks:
        for run in benchmark.get("test_runs", []):
            test_id = run.get("test_id")
            model = run.get("model")
            score = run.get("normalized_score")
            provider = run.get("provider")
            date = run.get("date")

            if not all([test_id, model, score, date]):
                continue

            # Load timing data from results
            result_path = RESULTS_PATH / date / test_id
            request_files = list(result_path.glob("request_*.json"))

            if request_files:
                try:
                    with open(request_files[0], 'r', encoding='utf-8') as f:
                        request_data = json.load(f)
                        test_time = request_data.get("test_time")

                        if test_time is not None:
                            model_data[model]["scores"].append(score)
                            model_data[model]["times"].append(test_time)
                            if model_data[model]["provider"] is None:
                                model_data[model]["provider"] = provider
                except Exception as e:
                    continue

    # Calculate model statistics
    model_stats = []

    for model, data in model_data.items():
        if not data["scores"] or not data["times"]:
            continue

        avg_score = sum(data["scores"]) / len(data["scores"])
        avg_time = sum(data["times"]) / len(data["times"])

        model_stats.append({
            "model": model,
            "avg_score": avg_score,
            "avg_time": avg_time,
            "provider": data["provider"],
            "num_runs": len(data["scores"])
        })

    if not model_stats:
        return {"data": [], "layout": {"title": "No timing data available"}}

    # Create scatter plot
    traces = []

    # Group by provider
    by_provider = defaultdict(list)
    for stat in model_stats:
        by_provider[stat["provider"]].append(stat)

    for provider in sorted(by_provider.keys()):
        models = by_provider[provider]

        x_values = [m["avg_time"] for m in models]
        y_values = [m["avg_score"] for m in models]
        sizes = [min(m["num_runs"] * 2, 50) + 10 for m in models]
        model_names = [m["model"] for m in models]

        # Create hover text
        hover_texts = []
        for m in models:
            hover_texts.append(
                f"<b>{m['model']}</b><br>" +
                f"Avg Score: {m['avg_score']:.1f}<br>" +
                f"Avg Time: {m['avg_time']:.2f}s<br>" +
                f"Runs: {m['num_runs']}"
            )

        color = PROVIDER_COLORS.get(provider, "#888888")

        # Capitalize provider name
        provider_display = provider.capitalize()
        if provider in ["openai", "anthropic", "google", "meta"]:
            provider_display = {
                "openai": "OpenAI",
                "anthropic": "Anthropic",
                "google": "Google",
                "meta": "Meta"
            }[provider]

        traces.append({
            "type": "scatter",
            "mode": "markers",
            "x": x_values,
            "y": y_values,
            "name": provider_display,
            "text": model_names,
            "hovertext": hover_texts,
            "hoverinfo": "text",
            "marker": {
                "size": sizes,
                "color": color,
                "opacity": 0.7,
                "line": {
                    "width": 2,
                    "color": "white"
                }
            }
        })

    # Layout
    layout = {
        "title": {
            "text": "<b>Speed vs Performance Analysis</b><br>" +
                   "<sub>Average response time vs. average score</sub>",
            "font": {"size": 20}
        },
        "xaxis": {
            "title": "Average Response Time (seconds)",
            "showgrid": True,
            "gridcolor": "#E5E5E5"
        },
        "yaxis": {
            "title": "Average Normalized Score (0-100)",
            "range": [0, 105],
            "showgrid": True,
            "gridcolor": "#E5E5E5"
        },
        "plot_bgcolor": "#FAFAFA",
        "paper_bgcolor": "white",
        "hovermode": "closest",
        "showlegend": True,
        "legend": {
            "orientation": "v",
            "yanchor": "top",
            "y": 1,
            "xanchor": "left",
            "x": 1.02
        },
        "annotations": [
            {
                "text": "← Faster & Better",
                "x": 0.02,
                "y": 0.98,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 12, "color": "#666"},
                "align": "left"
            }
        ],
        "margin": {"l": 60, "r": 150, "t": 100, "b": 60}
    }

    return {
        "data": traces,
        "layout": layout
    }


def generate_visualizations():
    """Generate all visualization configs and add them to benchmark export."""

    print("Loading benchmark export...")
    benchmarks_data = load_benchmark_export()

    print("Loading pricing data...")
    pricing_data = load_pricing_data()

    print("Generating visualizations...")

    # Generate overview visualizations (not per-benchmark)
    overview_viz = {
        "heatmap_benchmarks_models": {
            "viz_type": "heatmap",
            "title": "Benchmark × Model Performance",
            "description": "Average performance of each model on each benchmark",
            "plotly_figure": create_heatmap_benchmarks_models(benchmarks_data)
        },
        "box_plot_by_provider": {
            "viz_type": "box_plot",
            "title": "Score Distribution by Provider",
            "description": "Distribution of scores across all benchmarks by provider",
            "plotly_figure": create_box_plot_by_provider(benchmarks_data)
        },
        "bar_chart_difficulty": {
            "viz_type": "bar_chart",
            "title": "Benchmark Difficulty Ranking",
            "description": "Benchmarks ranked by average performance (lower = harder)",
            "plotly_figure": create_bar_chart_benchmark_difficulty(benchmarks_data)
        },
        "radar_chart_providers": {
            "viz_type": "radar_chart",
            "title": "Provider Performance Comparison",
            "description": "Radar chart comparing providers across all benchmarks",
            "plotly_figure": create_radar_chart_providers(benchmarks_data)
        },
        "cost_effectiveness_scatter": {
            "viz_type": "scatter",
            "title": "Cost-Effectiveness Analysis",
            "description": "Performance vs. estimated cost per task",
            "plotly_figure": create_cost_effectiveness_scatter(benchmarks_data, pricing_data)
        },
        "speed_performance_scatter": {
            "viz_type": "scatter",
            "title": "Speed vs Performance Analysis",
            "description": "Average response time vs. average score",
            "plotly_figure": create_speed_performance_scatter(benchmarks_data)
        }
    }

    # Add per-benchmark visualizations
    for benchmark in benchmarks_data:
        if len(benchmark.get("test_runs", [])) == 0:
            continue

        benchmark_name = benchmark.get("name")

        # Time series scatter plot
        scatter_viz = {
            "viz_type": "scatter_time_series",
            "title": f"{benchmark.get('title_short', benchmark_name)} - Performance Over Time",
            "description": "Model performance trends over time",
            "plotly_figure": create_scatter_time_series(benchmark)
        }

        # Add to benchmark data
        if "visualizations" not in benchmark:
            benchmark["visualizations"] = {}

        benchmark["visualizations"]["scatter_time_series"] = scatter_viz

    # Save each overview visualization to its own JSON file
    for viz_name, viz_data in overview_viz.items():
        viz_file_path = EXPORT_PATH / f"{viz_name}.json"
        with open(viz_file_path, "w", encoding="utf-8") as f:
            json.dump(viz_data, f, indent=2, ensure_ascii=False)
        print(f"Saved {viz_name} to {viz_file_path}")

    # Update benchmark export with per-benchmark visualizations
    export_path = EXPORT_PATH / "benchmark_export.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(benchmarks_data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated benchmark export with visualizations: {export_path}")
    print(f"Generated {len(overview_viz)} overview visualizations")
    print(f"Added visualizations to {len([b for b in benchmarks_data if 'visualizations' in b])} benchmarks")


if __name__ == "__main__":
    generate_visualizations()
