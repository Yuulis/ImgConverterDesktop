import os
from typing import Tuple

import pillow_heif
from PIL import Image


def make_dirs():
    """Create input and output directories if they do not exist."""
    if not os.path.exists("input"):
        os.makedirs("input")
    if not os.path.exists("output"):
        os.makedirs("output")


def format_bytes(size: int) -> str:
    """Convert byte size to human-readable string.

    Examples:
        500 -> "500 bytes"
        2048 -> "2.0 KB"
    """
    for unit in ["bytes", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "bytes" else f"{size:.1f} {unit}"
        size /= 1024


def convert_image(file_path: str, target_format: str) -> str:
    """Convert an image file to the target format and save into output/.

    Args:
        file_path: Path to the source image file.
        target_format: Target image format (e.g., 'png', 'jpg').

    Returns:
        Path to the converted output file.

    Raises:
        Exception: If loading or conversion fails.
    """
    if not target_format:
        raise ValueError("target_format must be specified")

    file_base_name, file_ext = os.path.splitext(os.path.basename(file_path))
    target_format = target_format.lower()

    # Ensure directories exist
    make_dirs()

    # Save the original image to the input directory
    # If not an image, Image.open will raise an exception
    with Image.open(file_path) as img_in:
        img_in.save(os.path.join("input", f"{file_base_name}{file_ext}"))

    # HEIC handling
    if file_ext.lower() == ".heic":
        return convert_heic(file_path, file_base_name, target_format)

    # Non-HEIC via Pillow
    with Image.open(file_path) as img:
        # EPS requires conversion to RGB for saving in many formats
        if target_format == "eps":
            img = img.convert("RGB")
        out_path = os.path.join("output", f"{file_base_name}.{target_format}")
        img.save(out_path)
        return out_path


def convert_heic(file_path: str, file_base_name: str, target_format: str) -> str:
    """Convert HEIC file to target format using pillow-heif."""
    convert_target_file = pillow_heif.read_heif(file_path)
    image = None
    for img in convert_target_file:
        image = Image.frombytes(
            img.mode,
            img.size,
            img.data,
            "raw",
            img.mode,
            img.stride,
        )
    if image is None:
        raise ValueError("No image frames found in HEIC file")
    out_path = os.path.join("output", f"{file_base_name}.{target_format}")
    image.save(out_path)
    return out_path
