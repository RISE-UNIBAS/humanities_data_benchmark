#!/bin/bash
# Run the Flask correction interface

cd "$(dirname "$0")"

# Activate virtual environment if needed
# source ../../../.venv/bin/activate

# Install requirements if needed
# pip install -r requirements_flask.txt

# Run Flask app
python app.py
