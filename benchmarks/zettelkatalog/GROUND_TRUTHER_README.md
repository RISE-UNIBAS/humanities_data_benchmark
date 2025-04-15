# GroundTruther

A GUI tool for viewing images alongside their JSON metadata, allowing for easy correction of metadata.

## Features

- Load image and associated JSON metadata
- Display image with pan/zoom capabilities
- Edit JSON metadata via a dynamically generated form
- Support for complex data structures (nested objects, lists)
- Special handling for Author, Publication, and PersonalData fields
- Auto-detect and link associated image/JSON files
- Save corrected metadata
- Navigate between images in a folder
- Auto-save changes when moving between images
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
python ground_truther.py
```

## How to use

1. Click "Open Image" to load an image file, or "Open JSON" to load a JSON metadata file
2. The tool will attempt to find the corresponding metadata or image file automatically
   - For image files like `00604370.png`, it will look for `request_T66_00604370.json`
   - For JSON files like `request_T66_00604370.json`, it will look for `00604370.png` (or .jpg, etc.)
3. Edit the metadata in the form on the right
   - Text fields for simple data like title, type
   - Specialized editors for complex fields like author (first/last name)
   - List editors for collections like examinations
4. Navigate between images using the "Previous Image" and "Next Image" buttons (or left/right arrow keys)
5. Changes are automatically saved when navigating between images
6. Use Ctrl+S to manually save changes at any time

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
            "examinations": [
                {
                    "location": "string",
                    "count": number
                }
            ],
            "final_exam_location": "string",
            "final_exam_date": "string"
        }
    },
    "scores": {}
}
```

This tool is designed to work with the document structure specified in `dataclass.py` and can handle nested metadata fields including lists and complex objects. The form fields are generated dynamically based on the existing JSON structure.