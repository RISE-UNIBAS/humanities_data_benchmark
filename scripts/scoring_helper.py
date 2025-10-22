from typing import Any, Union
from pydantic import BaseModel
from rapidfuzz import fuzz

def get_all_keys(obj: Any, parent_key: str = '') -> list:
    """Recursively get all terminal (non-iterable) keys in a nested dictionary, list, or Pydantic model."""
    keys = []

    if isinstance(obj, BaseModel):  # Convert Pydantic models to dictionaries
        obj = obj.dict()

    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, (dict, list, BaseModel)):  # Skip non-terminal values
                keys.extend(get_all_keys(value, full_key))
            else:
                keys.append(full_key)  # Only add terminal values

    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            full_key = f"{parent_key}[{index}]"
            if isinstance(item, (dict, list, BaseModel)):  # Skip non-terminal values
                keys.extend(get_all_keys(item, full_key))
            else:
                keys.append(full_key)  # Only add terminal values

    else:  # If it's not iterable, it's a terminal value
        keys.append(parent_key)

    return keys


def get_score_color(score: float) -> str:
    """
    Convert a score (0.0 to 1.0) to a hex color from green (1.0) to red (0.0),
    passing through orange (~0.5).

    - 1.0 -> Green (`#00FF00`)
    - 0.5 -> Orange (`#FFA500`)
    - 0.0 -> Red (`#FF0000`)
    """
    # Clamp score between 0.0 and 1.0
    score = max(0.0, min(1.0, score))

    # Define RGB values for Red, Orange, and Green
    red = (255, 0, 0)  # #FF0000
    orange = (255, 165, 0)  # #FFA500
    green = (0, 255, 0)  # #00FF00

    if score >= 0.5:
        # Interpolate between Orange and Green
        ratio = (score - 0.5) * 2  # Normalize 0.5-1.0 to 0-1
        r = int(orange[0] + (green[0] - orange[0]) * ratio)
        g = int(orange[1] + (green[1] - orange[1]) * ratio)
        b = int(orange[2] + (green[2] - orange[2]) * ratio)
    else:
        # Interpolate between Red and Orange
        ratio = score * 2  # Normalize 0-0.5 to 0-1
        r = int(red[0] + (orange[0] - red[0]) * ratio)
        g = int(red[1] + (orange[1] - red[1]) * ratio)
        b = int(red[2] + (orange[2] - red[2]) * ratio)

    return f"#{r:02X}{g:02X}{b:02X}"


def calculate_fuzzy_score(test_value, gold_value):
    """Calculate a score based on the extracted GPT value and the gold standard value."""
    if test_value == gold_value:
        return 1.0

    if test_value is None or gold_value is None:
        return 0.0

    # Convert both values to strings for comparison (handles int/str mismatches like year fields)
    test_str = str(test_value) if test_value is not None else None
    gold_str = str(gold_value) if gold_value is not None else None

    # Check if string representations match exactly
    if test_str == gold_str:
        return 1.0

    # If either original value was not a string or number, return 0
    if not isinstance(test_value, (str, int, float)) or not isinstance(gold_value, (str, int, float)):
        return 0.0

    similarity = fuzz.ratio(test_str, gold_str)

    return similarity / 100.0


def get_nested_value(obj: Union[dict, BaseModel], path: str) -> Any:
    """Retrieve a value from a nested dictionary or Pydantic model based on a string path."""
    keys = path.replace("[", ".").replace("]", "").split(".")  # Normalize to dot notation
    for key in keys:
        if isinstance(obj, BaseModel):  # Handle Pydantic models
            obj = obj.dict()  # Convert to dict

        if isinstance(obj, dict):  # If it's a dict, get the key
            obj = obj.get(key, None)
        elif isinstance(obj, list):  # If it's a list, try accessing by index
            try:
                index = int(key)  # Convert key to integer index
                obj = obj[index]
            except (ValueError, IndexError):
                return None  # Invalid index
        else:
            return None  # Can't navigate further

        if obj is None:
            return None  # Key not found

    return obj  # Return final value

def remove_none(d):
    """ Recursively remove None values from a dictionary or list """

    if isinstance(d, dict):
        return {k: remove_none(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [remove_none(i) for i in d]
    else:
        return d