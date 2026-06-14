"""Format compatibility test: checks which target formats work from RGB and RGBA PNG sources."""

import os
import sys

import pytest
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from utils import convert_image

TARGET_FORMATS = [
    "blp", "bmp", "dds", "dib", "eps", "gif", "icns", "ico", "im",
    "jpg", "jp2", "mpo", "msp", "pcx", "pfm", "png", "ppm", "sgi",
    "spider", "tga", "tiff", "webp", "xbm", "palm", "pdf", "xv",
]


def _create_test_png(path: str, mode: str) -> None:
    """Creates a small test PNG image."""
    img = Image.new(mode, (10, 10), color=(255, 0, 0) if mode == "RGB" else (255, 0, 0, 128))
    img.save(path, format="PNG")


def _try_convert(src_path: str, fmt: str) -> tuple[str, str]:
    """Attempts conversion and returns (result, error_message)."""
    try:
        out = convert_image(src_path, fmt)
        if os.path.exists(out) and os.path.getsize(out) > 0:
            return ("pass", "")
        return ("fail", "Output file missing or empty")
    except Exception as exc:
        return ("fail", f"{type(exc).__name__}: {exc}")


def test_format_compatibility_table(tmp_path, monkeypatch, capsys) -> None:
    """Runs all format x mode combinations and prints a results table."""
    monkeypatch.chdir(tmp_path)

    rgb_src = str(tmp_path / "test_rgb.png")
    rgba_src = str(tmp_path / "test_rgba.png")
    _create_test_png(rgb_src, "RGB")
    _create_test_png(rgba_src, "RGBA")

    results: list[tuple[str, str, str, str]] = []

    for fmt in TARGET_FORMATS:
        rgb_result, rgb_err = _try_convert(rgb_src, fmt)
        rgba_result, rgba_err = _try_convert(rgba_src, fmt)
        note = rgb_err or rgba_err
        results.append((fmt, rgb_result, rgba_result, note))

    with capsys.disabled():
        print("\n")
        print(f"{'Format':<10} | {'RGB':<6} | {'RGBA':<6} | Notes")
        print("-" * 80)
        for fmt, rgb_r, rgba_r, note in results:
            rgb_sym = "pass" if rgb_r == "pass" else "FAIL"
            rgba_sym = "pass" if rgba_r == "pass" else "FAIL"
            print(f"{fmt:<10} | {rgb_sym:<6} | {rgba_sym:<6} | {note}")
        print("-" * 80)

    pass_count = sum(1 for _, r, a, _ in results if r == "pass" and a == "pass")
    total = len(results)
    print(f"\nFully passing: {pass_count}/{total}")

    failures = [(f, r, a, n) for f, r, a, n in results if r == "fail" or a == "fail"]
    if failures:
        msgs = [f"  {f}: RGB={r}, RGBA={a} | {n}" for f, r, a, n in failures]
        print("Failures:\n" + "\n".join(msgs))
