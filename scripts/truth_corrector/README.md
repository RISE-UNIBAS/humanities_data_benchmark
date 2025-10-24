# Ground Truth Corrector

A Flask-based web application for manually correcting ground truth data for benchmarks.

## Features

- View images alongside their ground truth data
- Edit ground truth in a user-friendly form
- Track correction progress
- Auto-saves correction status to `ground_truth_status.json` in each benchmark

## Installation

```bash
pip install flask
```

## Usage

1. Navigate to the truth_corrector directory:
```bash
cd scripts/truth_corrector
```

2. Run the Flask app:
```bash
python app.py
```

3. Open your browser and go to:
```
http://localhost:5001/?benchmark=blacklist
```

4. Click on items in the sidebar to view and edit them

5. Make your corrections and click "Save & Mark as Corrected"

## Structure

- **app.py** - Flask application
- **templates/index.html** - Web interface
- **../../benchmarks/<benchmark>/ground_truth_status.json** - Tracks correction status

## Keyboard Shortcuts (Future)

- Arrow keys to navigate between items
- Ctrl+S to save
- Ctrl+Enter to save and move to next

## Notes

- The app expects each benchmark to have `images/` and `ground_truths/` directories
- Image and ground truth files must have the same base name (different extensions)
- Corrections are saved immediately to the ground truth JSON files
- Status tracking allows you to resume work later
