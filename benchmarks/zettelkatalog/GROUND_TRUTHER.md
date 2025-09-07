# GroundTruther

A GUI tool for viewing images alongside their JSON metadata, allowing for easy correction of metadata.

## Features

- Load image and associated JSON metadata
- Display image with pan/zoom capabilities
- Edit JSON metadata via a dynamically generated form
- Support for complex data structures (nested objects, lists)
- Special handling for Author, Publication, and PersonalData fields
- Auto-detect and link associated image/JSON files
- Save corrected metadata to separate output folder
- Configure input/output directories through GUI or command-line
- Navigate between images in a folder
- Auto-save changes when moving between images
- Remember settings between sessions
- Automatic JSON error repair
- Input files are never modified/overwritten
- Detailed logging for troubleshooting

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

The application requires Python 3.7+ and the following libraries:
- Pillow (PIL Fork) - For image processing
- Pydantic - For data validation and settings management
- Tkinter - For the GUI (usually included with Python)

## Usage

Run the application:
```
python ground_truther.py [options]
```

### Command Line Options

The application supports the following command-line options:

- `--image-dir PATH` - Directory containing image files
- `--json-dir PATH` - Directory containing input JSON files
- `--output-dir PATH` - Directory where JSON files will be saved
- `--prefix TEXT` - Prefix for JSON filenames (default: "request_T66_")
- `--reset-config` - Reset saved configuration to command line values

Example:
```
python ground_truther.py --image-dir /path/to/images --json-dir /path/to/json --output-dir /path/to/output
```

You can specify different directories for images, input JSON files, and output JSON files. This separation ensures your original files are never modified.

### Configuration Persistence

The application remembers your configuration settings between runs:

- Directory paths and prefix settings are automatically saved
- Settings are stored in a file at `~/.groundtruther_config.json`
- Configuration is automatically loaded on startup and saved:
  - When you close the application
  - When you change directories using the Browse buttons
  - When you click Apply Settings or Update Prefix buttons
  - When you select an output directory during saving

To reset your saved configuration, run with the `--reset-config` flag:
```
python ground_truther.py --reset-config
```

This will clear any saved settings and use the values provided on the command line.

### File Handling

The application carefully manages files to protect your data:

- **Input JSON files are never modified** - even when fixing JSON errors
- **Input and output are kept separate** - all edits are saved to the output directory
- **Automatic JSON repair** - corrupted JSON files are fixed in memory without modifying originals
- **Prefix only applies to output** - the specified prefix is only used for output filenames
- **Filename conflicts are prevented** - if a JSON with the same name exists in the output directory, the tool adds an "EDITED_" prefix

### GUI Configuration

The application now includes a configuration panel in the GUI where you can:

1. **Set the Image Directory** - Choose the folder containing your images
2. **Set the JSON Directory** - Choose the folder containing input JSON files
3. **Set the Output Directory** - Choose where to save edited JSON files
4. **Set the JSON Prefix** - Change the prefix used for JSON filenames (default: "request_T66_")

These settings can be changed at any time during your editing session. Click "Apply Settings" to save and activate your changes.

## How to use

1. Set up your directories in the Configuration panel at the top:
   - **Image Directory**: Where your images are stored
   - **JSON Directory**: Where input JSON files are stored
   - **Output Directory**: Where edited JSON files will be saved
   - **JSON Prefix**: The prefix to add to output JSON filenames

2. Click "Open Image" to load an image file, or "Open JSON" to load a JSON metadata file
   - The tool will scan directories and attempt to find matching files automatically
   - It can handle various naming patterns and doesn't require specific prefixes for input files
   - For fuzzy matches, it will ask you to confirm if it found the correct file

3. Edit the metadata in the form on the right
   - Text fields for simple data like title, type
   - Specialized editors for complex fields like author (first/last name)
   - List editors for collections
   
4. Save your edits with "Save JSON" button or Ctrl+S
   - Files are always saved to the output directory to protect originals
   - If no output directory is set, you'll be prompted to select one
   - Output filenames will use the prefix you specified in settings

5. Navigate between images using the "Previous Image" and "Next Image" buttons (or left/right arrow keys)
   - Changes are automatically saved when navigating between images
   - The same output directory and prefix settings will be used for all saved files

## Keyboard Shortcuts

- **Right Arrow**: Next image
- **Left Arrow**: Previous image
- **Ctrl+S**: Save JSON

## JSON Format

The tool works with JSON files that follow the structure defined in `dataclass.py`, with document metadata stored directly under the `response_text` key. The basic structure is:

```json
{
    "provider": "string",
    "model": "string",
    "test_time": number,
    "execution_time": "string",
    "response_text": {
        "author": {
            "last_name": "string",
            "first_name": "string"
        },
        "title": "string",
        "publication": {
            "place": "string",
            "year": number,
            "pages": "string",
            "publisher": "string",
            "format": "string"
        },
        "type": "string",
        "institution": "string",
        "language": "string",
        "notes": "string",
        "defense_date": "string",
        "advisor": "string",
        "department": "string",
        "director": "string",
        "library_reference": "string",
        "personal_data": {
            "birth_date": "string",
            "birth_place": "string",
            "residence": "string",
            "nationality": "string",
            "education": {
                "secondary": "string",
                "university": ["string", ...]
            },
            "final_exam_location": "string",
            "final_exam_date": "string"
        }
    },
    "scores": {}
}
```

This tool is designed to work with the document structure specified in `dataclass.py` and can handle nested metadata fields including lists and complex objects. The form fields are generated dynamically based on the existing JSON structure.