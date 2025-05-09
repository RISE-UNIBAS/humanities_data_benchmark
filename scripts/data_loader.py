import json
import logging
import os

from PIL import Image


def read_file(path):
    try:
        with open(path, 'r', encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"File {path} not found.")
        return ""

def write_file(path, content):
    with open(path, 'w', encoding="utf-8") as file:
        if isinstance(content, dict):
            content = json.dumps(content, indent=4)
        file.write(content)


def resize_image(image_path: str,
                 temp_dir: str,
                 max_size: tuple = (1024, 1024)) -> str:
    """ Resize an image to fit within the max size.
    """
    img = Image.open(image_path)
    img.thumbnail(max_size)

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    filename = os.path.basename(image_path)
    resized_path = os.path.join(temp_dir, filename)

    img.save(resized_path, optimize=True, quality=85)
    return resized_path