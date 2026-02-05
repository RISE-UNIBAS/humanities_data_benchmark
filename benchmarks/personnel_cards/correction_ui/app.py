#!/usr/bin/env python3
"""
Flask-based Ground Truth Correction Interface for Personnel Cards

Usage:
    python app.py
    Then open http://localhost:5000 in your browser
"""

import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from PIL import Image
import io
import base64

app = Flask(__name__)

# Configuration
IMAGES_DIR = Path(__file__).parent.parent / "images"
GROUND_TRUTHS_DIR = Path(__file__).parent.parent / "ground_truths"


def get_image_files():
    """Get all image files from the images directory."""
    if not IMAGES_DIR.exists():
        return []

    image_files = sorted([
        f for f in IMAGES_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']
        and not f.name.startswith('.')
    ])
    return image_files


def get_ground_truth_path(image_path):
    """Get the corresponding ground truth JSON path for an image."""
    basename = image_path.stem
    return GROUND_TRUTHS_DIR / f"{basename}.json"


def load_ground_truth(json_path):
    """Load ground truth JSON from file."""
    if not json_path.exists():
        return {"rows": []}

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return {"rows": []}


def save_ground_truth(json_path, data):
    """Save ground truth JSON to file."""
    try:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving ground truth: {e}")
        return False


def get_image_base64(image_path):
    """Convert image to base64 for embedding in HTML, rotate if portrait."""
    try:
        img = Image.open(image_path)

        # Rotate if portrait
        width, height = img.size
        if height > width:
            img = img.rotate(90, expand=True)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


@app.route('/')
def index():
    """Main page - redirect to first image."""
    image_files = get_image_files()
    if not image_files:
        return "No images found", 404
    return redirect(url_for('edit_image', image_name=image_files[0].name))


@app.route('/image/<image_name>')
def edit_image(image_name):
    """Edit page for a specific image."""
    image_files = get_image_files()

    # Find current image
    image_path = None
    current_index = -1
    for i, img in enumerate(image_files):
        if img.name == image_name:
            image_path = img
            current_index = i
            break

    if image_path is None:
        return "Image not found", 404

    # Get ground truth
    gt_path = get_ground_truth_path(image_path)
    gt_data = load_ground_truth(gt_path)

    # Navigation info
    prev_image = image_files[current_index - 1].name if current_index > 0 else None
    next_image = image_files[current_index + 1].name if current_index < len(image_files) - 1 else None

    # Get image as base64
    image_data = get_image_base64(image_path)

    return render_template(
        'index.html',
        image_name=image_name,
        image_data=image_data,
        ground_truth=gt_data,
        prev_image=prev_image,
        next_image=next_image,
        current_index=current_index + 1,
        total_images=len(image_files),
        has_ground_truth=gt_path.exists()
    )


@app.route('/save/<image_name>', methods=['POST'])
def save_image(image_name):
    """Save ground truth for an image."""
    print(f"\n=== SAVE REQUEST for {image_name} ===")
    print(f"Form data keys: {list(request.form.keys())}")
    print(f"Full form data:")
    for key, value in request.form.items():
        print(f"  {key} = {value}")

    image_files = get_image_files()

    # Find image
    image_path = None
    for img in image_files:
        if img.name == image_name:
            image_path = img
            break

    if image_path is None:
        return "Image not found", 404

    # Parse form data into rows
    rows = []
    row_count = 0

    # Count how many rows we have
    while f'row_{row_count}_number' in request.form:
        row_count += 1

    print(f"Found {row_count} rows in form data")

    for i in range(row_count):
        row = {
            'row_number': int(request.form.get(f'row_{i}_number', i + 1))
        }

        for field_name in ['dienstliche_stellung', 'dienstort', 'gehaltsklasse',
                          'jahresgehalt_monatsgehalt_taglohn', 'datum_gehaltsänderung', 'bemerkungen']:
            diplomatic = request.form.get(f'row_{i}_{field_name}_diplomatic', '')
            interpretation = request.form.get(f'row_{i}_{field_name}_interpretation', '')
            is_crossed = f'row_{i}_{field_name}_crossed' in request.form

            row[field_name] = {
                'diplomatic_transcript': diplomatic,
                'interpretation': None if interpretation == '' else interpretation,
                'is_crossed_out': is_crossed
            }

        rows.append(row)

    data = {'rows': rows}
    print(f"Constructed data with {len(rows)} rows")

    # Save
    gt_path = get_ground_truth_path(image_path)
    print(f"Saving to: {gt_path}")
    if save_ground_truth(gt_path, data):
        print("Save successful!")
        return redirect(url_for('edit_image', image_name=image_name))
    else:
        print("Save failed!")
        return "Failed to save", 500


@app.route('/add_row/<image_name>', methods=['POST'])
def add_row(image_name):
    """Add a new row to the ground truth."""
    image_files = get_image_files()

    # Find image
    image_path = None
    for img in image_files:
        if img.name == image_name:
            image_path = img
            break

    if image_path is None:
        return jsonify({"success": False}), 404

    # Load current data
    gt_path = get_ground_truth_path(image_path)
    data = load_ground_truth(gt_path)

    # Add new row
    new_row = {
        'row_number': len(data.get('rows', [])) + 1,
        'dienstliche_stellung': {'diplomatic_transcript': '', 'interpretation': None, 'is_crossed_out': False},
        'dienstort': {'diplomatic_transcript': '', 'interpretation': None, 'is_crossed_out': False},
        'gehaltsklasse': {'diplomatic_transcript': '', 'interpretation': None, 'is_crossed_out': False},
        'jahresgehalt_monatsgehalt_taglohn': {'diplomatic_transcript': '', 'interpretation': None, 'is_crossed_out': False},
        'datum_gehaltsänderung': {'diplomatic_transcript': '', 'interpretation': None, 'is_crossed_out': False},
        'bemerkungen': {'diplomatic_transcript': '', 'interpretation': None, 'is_crossed_out': False}
    }

    data.setdefault('rows', []).append(new_row)

    # Save and redirect
    save_ground_truth(gt_path, data)
    return redirect(url_for('edit_image', image_name=image_name))


@app.route('/delete_row/<image_name>/<int:row_index>', methods=['POST'])
def delete_row(image_name, row_index):
    """Delete a row from the ground truth."""
    image_files = get_image_files()

    # Find image
    image_path = None
    for img in image_files:
        if img.name == image_name:
            image_path = img
            break

    if image_path is None:
        return jsonify({"success": False}), 404

    # Load current data
    gt_path = get_ground_truth_path(image_path)
    data = load_ground_truth(gt_path)

    # Delete row
    rows = data.get('rows', [])
    if 0 <= row_index < len(rows):
        rows.pop(row_index)
        # Renumber
        for i, row in enumerate(rows):
            row['row_number'] = i + 1

    # Save and redirect
    save_ground_truth(gt_path, data)
    return redirect(url_for('edit_image', image_name=image_name))


if __name__ == '__main__':
    # Disable reloader on Windows to avoid signal issues
    app.run(debug=True, port=5000, use_reloader=False)
