import os
import shutil
import pillow_heif
from PIL import Image


def make_dirs():
    """Creates input and output directories if they do not exist."""
    
    if not os.path.exists("input"):
        os.makedirs("input")
    if not os.path.exists("output"):
        os.makedirs("output")


def format_bytes(size: int) -> str:
    """Converts byte size to human-readable string.

    Examples:
        500 -> "500 bytes"
        2048 -> "2.0 KB"
    """
    
    for unit in ["bytes", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "bytes" else f"{size:.1f} {unit}"
        size /= 1024


def load_heif_as_pil(file_path: str) -> Image.Image:
    """Loads the first frame from a HEIC/HEIF file as a PIL Image.

    Args:
        file_path: Path to the HEIC/HEIF image file.

    Returns:
        PIL Image of the first frame.

    Raises:
        ValueError: If no image frames are found in the file.
    """
    heif_file = pillow_heif.read_heif(file_path)
    frame = next(iter(heif_file), None)
    if frame is None:
        raise ValueError("No image frames found in HEIC file.")
    return Image.frombytes(
        frame.mode,
        frame.size,
        frame.data,
        "raw",
        frame.mode,
        frame.stride,
    )


def convert_image(file_path: str, target_format: str) -> str:
    """Converts an image file to the target format and saves it into output dir.

    Args:
        file_path: Path to the source image file.
        target_format: Target image format (e.g., 'png', 'jpg').

    Returns:
        Path to the converted output file.

    Raises:
        Exception: If loading or conversion fails.
    """

    if not target_format:
        raise ValueError("target_format must be specified.")

    file_base_name, file_ext = os.path.splitext(os.path.basename(file_path))
    target_format = target_format.lower()

    # Ensure directories exist
    make_dirs()

    # HEIC handling
    if file_ext.lower() in {".heic", ".heif"}:
        shutil.copy2(file_path, os.path.join("input", f"{file_base_name}{file_ext}"))
        return convert_heic(file_path, file_base_name, target_format)

    # Non-HEIC via Pillow — copy original bytes to input/ to avoid re-encoding
    shutil.copy2(file_path, os.path.join("input", f"{file_base_name}{file_ext}"))
    with Image.open(file_path) as img:
        # EPS requires conversion to RGB for saving in many formats
        if target_format == "eps":
            img = img.convert("RGB")

        out_path = os.path.join("output", f"{file_base_name}.{target_format}")
        img.save(out_path)

        return out_path


def convert_heic(file_path: str, file_base_name: str, target_format: str) -> str:
    """Converts HEIC file to target format using pillow-heif."""
    image = load_heif_as_pil(file_path)
    out_path = os.path.join("output", f"{file_base_name}.{target_format}")
    image.save(out_path)
    return out_path
