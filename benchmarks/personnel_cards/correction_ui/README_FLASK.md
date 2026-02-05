# Flask Ground Truth Correction Interface

A robust Flask-based web interface for editing personnel card ground truth annotations.

## Why Flask instead of Streamlit?

- **More stable**: No complex state management issues
- **Predictable**: Simple request/response model
- **Easy to debug**: Standard HTML forms and POST/GET requests
- **Reliable**: No reruns, no session state conflicts

## Setup

### Install dependencies

```bash
pip install -r requirements_flask.txt
```

Or install individually:
```bash
pip install Flask Pillow
```

## Running the Interface

### Option 1: Using the script
```bash
cd benchmarks/personnel_cards/correction_ui
./run_flask.sh
```

### Option 2: Direct Python
```bash
cd benchmarks/personnel_cards/correction_ui
python app.py
```

### Option 3: With your project venv
```bash
cd benchmarks/personnel_cards/correction_ui
source /path/to/your/.venv/bin/activate  # or .venv\Scripts\activate on Windows
python app.py
```

The interface will be available at: **http://localhost:5000**

## Features

### Image Display
- **Auto-rotation**: Portrait images automatically rotated to landscape
- **Always visible**: Image stays in view (simple two-column layout)
- **Base64 embedding**: No separate image serving needed

### Navigation
- **Previous/Next buttons**: Navigate between images
- **Progress indicator**: Shows current position (e.g., "Image 5 of 60")
- **Status indicator**: Shows if ground truth exists for current image

### Editor
- **Structured form**: Clean HTML form for all fields
- **Row management**: Add/delete rows with simple POST requests
- **Automatic saving**: Save button submits form and saves JSON
- **Reload button**: Refresh from disk without navigating away

### Data Fields (per row)
Each row contains:
- Row number
- dienstliche_stellung (diplomatic_transcript, interpretation, is_crossed_out)
- dienstort (diplomatic_transcript, interpretation, is_crossed_out)
- gehaltsklasse (diplomatic_transcript, interpretation, is_crossed_out)
- jahresgehalt_monatsgehalt_taglohn (diplomatic_transcript, interpretation, is_crossed_out)
- datum_gehaltsänderung (diplomatic_transcript, interpretation, is_crossed_out)
- bemerkungen (diplomatic_transcript, interpretation, is_crossed_out)

## How It Works

### Backend (Flask)
- `app.py`: Flask server with simple routes
  - `/`: Redirect to first image
  - `/image/<name>`: Display image and editor
  - `/save/<name>`: Save ground truth (POST)
  - `/add_row/<name>`: Add new row (POST)
  - `/delete_row/<name>/<index>`: Delete row (POST)

### Frontend (HTML/JS)
- `templates/index.html`: Single template with form
- Vanilla JavaScript collects form data and converts to JSON
- Simple CSS for clean, readable layout

### Data Flow
1. User opens page → Flask loads image and JSON
2. User edits form → JavaScript captures changes
3. User clicks Save → Form submits, Flask saves JSON
4. User clicks Next → Flask redirects to next image

## File Structure

```
correction_ui/
├── app.py                    # Flask server
├── templates/
│   └── index.html           # Main template
├── requirements_flask.txt   # Dependencies
├── run_flask.sh            # Run script
└── README_FLASK.md         # This file
```

## Troubleshooting

### Port already in use
If port 5000 is busy, edit `app.py` and change:
```python
app.run(debug=True, port=5000)  # Change to 5001, 8080, etc.
```

### Images not loading
- Check that `IMAGES_DIR` path is correct in `app.py`
- Ensure images exist in `benchmarks/personnel_cards/images/`

### Ground truth not saving
- Check that `GROUND_TRUTHS_DIR` path is correct
- Ensure write permissions for `benchmarks/personnel_cards/ground_truths/`

### Page not refreshing after action
- This is normal - actions like "Add Row" and "Delete Row" do a full page reload
- Save button also does a full page reload after saving

## Development

To run in debug mode (auto-reload on code changes):
```python
app.run(debug=True, port=5000)  # Already set by default
```

To run in production mode:
```python
app.run(debug=False, port=5000)
```
