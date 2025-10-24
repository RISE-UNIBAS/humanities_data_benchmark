"""Flask app for correcting ground truth data for benchmarks."""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
from pathlib import Path
import os

app = Flask(__name__)

# Base path to benchmarks
BENCHMARKS_PATH = Path("../../benchmarks")

def get_benchmark_path(benchmark_name):
    """Get the path to a benchmark directory."""
    return BENCHMARKS_PATH / benchmark_name

def get_status_file_path(benchmark_name):
    """Get the path to the status tracking file."""
    return get_benchmark_path(benchmark_name) / "ground_truth_status.json"

def load_status(benchmark_name):
    """Load the correction status for a benchmark."""
    status_file = get_status_file_path(benchmark_name)
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_status(benchmark_name, status):
    """Save the correction status for a benchmark."""
    status_file = get_status_file_path(benchmark_name)
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def get_all_items(benchmark_name):
    """Get all image/ground truth pairs for a benchmark."""
    benchmark_path = get_benchmark_path(benchmark_name)
    images_path = benchmark_path / "images"
    ground_truths_path = benchmark_path / "ground_truths"

    if not images_path.exists() or not ground_truths_path.exists():
        return []

    items = []
    status = load_status(benchmark_name)

    # Get all images
    for img_file in sorted(images_path.iterdir()):
        if not img_file.is_file():
            continue

        base_name = img_file.stem
        gt_file = ground_truths_path / f"{base_name}.json"

        if gt_file.exists():
            item_status = status.get(base_name, {})
            items.append({
                "id": base_name,
                "image_file": img_file.name,
                "gt_file": gt_file.name,
                "corrected": item_status.get("corrected", False),
                "last_modified": item_status.get("last_modified", "")
            })

    return items

def load_ground_truth(benchmark_name, item_id):
    """Load ground truth data for an item."""
    benchmark_path = get_benchmark_path(benchmark_name)
    gt_file = benchmark_path / "ground_truths" / f"{item_id}.json"

    if gt_file.exists():
        with open(gt_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_ground_truth(benchmark_name, item_id, data):
    """Save ground truth data for an item."""
    benchmark_path = get_benchmark_path(benchmark_name)
    gt_file = benchmark_path / "ground_truths" / f"{item_id}.json"

    with open(gt_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Update status
    status = load_status(benchmark_name)
    from datetime import datetime
    status[item_id] = {
        "corrected": True,
        "last_modified": datetime.now().isoformat()
    }
    save_status(benchmark_name, status)

@app.route('/')
def index():
    """Main page - list all items."""
    benchmark_name = request.args.get('benchmark', 'blacklist')
    items = get_all_items(benchmark_name)

    # Calculate statistics
    total = len(items)
    corrected = sum(1 for item in items if item['corrected'])

    return render_template('index.html',
                         benchmark=benchmark_name,
                         items=items,
                         total=total,
                         corrected=corrected)

@app.route('/api/item/<benchmark>/<item_id>')
def get_item(benchmark, item_id):
    """Get item data (ground truth)."""
    gt_data = load_ground_truth(benchmark, item_id)
    return jsonify(gt_data)

@app.route('/api/item/<benchmark>/<item_id>', methods=['POST'])
def save_item(benchmark, item_id):
    """Save item data (ground truth)."""
    data = request.json
    save_ground_truth(benchmark, item_id, data)
    return jsonify({"success": True})

@app.route('/images/<benchmark>/<filename>')
def serve_image(benchmark, filename):
    """Serve an image file."""
    benchmark_path = get_benchmark_path(benchmark)
    images_path = benchmark_path / "images"
    return send_from_directory(images_path, filename)

@app.route('/api/benchmarks')
def list_benchmarks():
    """List all available benchmarks."""
    benchmarks = []
    for benchmark_dir in BENCHMARKS_PATH.iterdir():
        if benchmark_dir.is_dir():
            images_dir = benchmark_dir / "images"
            gt_dir = benchmark_dir / "ground_truths"
            if images_dir.exists() and gt_dir.exists():
                benchmarks.append(benchmark_dir.name)
    return jsonify(benchmarks)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
