import os
import shutil
import pillow_heif
from PIL import Image

NO_ALPHA_FORMATS = {
    "jpg", "jpeg", "bmp", "ico", "pcx", "tga", "sgi",
    "msp", "xbm", "ppm", "pfm", "dib", "palm", "mpo", "eps",
}

# These formats require 1-bit (binary) images
BINARY_FORMATS = {"msp", "xbm"}

# These formats require grayscale images
GRAYSCALE_FORMATS = {"palm"}


def make_dirs() -> None:
    """Creates input and output directories if they do not exist."""
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)


def format_bytes(size: int | float) -> str:
    """Converts byte size to human-readable string.

    Examples:
        500 -> "500 bytes"
        2048 -> "2.0 KB"

    Raises:
        ValueError: If size is negative.
    """
    if size < 0:
        raise ValueError("size must be non-negative")

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

    make_dirs()

    shutil.copy2(file_path, os.path.join("input", f"{file_base_name}{file_ext}"))

    if file_ext.lower() in {".heic", ".heif"}:
        return convert_heic(file_path, file_base_name, target_format)

    with Image.open(file_path) as img:
        converted = img
        if target_format in BINARY_FORMATS:
            converted = img.convert("1")
        elif target_format in GRAYSCALE_FORMATS:
            converted = img.convert("L")
        elif target_format in NO_ALPHA_FORMATS:
            if img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            ):
                converted = img.convert("RGB")

        out_path = os.path.join("output", f"{file_base_name}.{target_format}")
        converted.save(out_path)

        return os.path.abspath(out_path)


def convert_heic(file_path: str, file_base_name: str, target_format: str) -> str:
    """Converts HEIC file to target format using pillow-heif."""
    make_dirs()
    image = load_heif_as_pil(file_path)
    try:
        out_path = os.path.join("output", f"{file_base_name}.{target_format}")
        image.save(out_path)
        return os.path.abspath(out_path)
    finally:
        image.close()
