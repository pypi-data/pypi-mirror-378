import os

from PIL import Image


def resize_image(input_path: str, output_path: str, width: int, height: int):
    img = Image.open(input_path)
    resized = img.resize((width, height))
    resized.save(output_path)


def convert_format(input_path: str, output_path: str, format: str):
    img = Image.open(input_path)

    # Normalize format (JPEG vs JPG)
    format = format.lower()
    if format == "jpg":
        format = "jpeg"

    # Handle incompatible modes
    if format in ["jpeg", "jpg"]:
        # JPEG does not support transparency or palette
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
    elif format in ["png", "webp"]:
        # PNG & WEBP support transparency
        if img.mode == "P":  # palette
            img = img.convert("RGBA")
    else:
        # Fallback: try to keep RGB if possible
        if img.mode not in ("RGB", "RGBA", "L"):
            img = img.convert("RGB")

    # Save in target format
    img.save(output_path, format=format.upper())


def get_info(input_path: str):
    img = Image.open(input_path)
    return {"format": img.format, "mode": img.mode, "size": img.size}
