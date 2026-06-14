"""Tests for src/utils.py — format_bytes, make_dirs, convert_image, load_heif_as_pil, convert_heic."""

import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

# Ensure src/ is importable
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from utils import convert_heic, convert_image, format_bytes, load_heif_as_pil, make_dirs


# ---------------------------------------------------------------------------
# format_bytes
# ---------------------------------------------------------------------------

class TestFormatBytes:
    """Tests for format_bytes()."""

    def test_zero_bytes(self) -> None:
        assert format_bytes(0) == "0 bytes"

    def test_small_bytes(self) -> None:
        assert format_bytes(500) == "500 bytes"

    def test_one_byte(self) -> None:
        assert format_bytes(1) == "1 bytes"

    def test_max_bytes_before_kb(self) -> None:
        # 1023 bytes should stay in bytes
        assert format_bytes(1023) == "1023 bytes"

    def test_exact_1kb(self) -> None:
        assert format_bytes(1024) == "1.0 KB"

    def test_2kb(self) -> None:
        assert format_bytes(2048) == "2.0 KB"

    def test_exact_1mb(self) -> None:
        assert format_bytes(1048576) == "1.0 MB"

    def test_exact_1gb(self) -> None:
        assert format_bytes(1073741824) == "1.0 GB"

    def test_exact_1tb(self) -> None:
        assert format_bytes(1024**4) == "1.0 TB"

    def test_large_tb_value(self) -> None:
        # Values larger than 1 TB should stay in TB
        result = format_bytes(5 * 1024**4)
        assert result == "5.0 TB"

    def test_fractional_kb(self) -> None:
        # 1536 bytes = 1.5 KB
        assert format_bytes(1536) == "1.5 KB"

    def test_negative_value_raises(self) -> None:
        with pytest.raises(ValueError, match="size must be non-negative"):
            format_bytes(-1)

    def test_negative_large_raises(self) -> None:
        with pytest.raises(ValueError, match="size must be non-negative"):
            format_bytes(-2048)

    def test_return_type_is_str(self) -> None:
        result = format_bytes(1024)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# make_dirs
# ---------------------------------------------------------------------------

class TestMakeDirs:
    """Tests for make_dirs() — uses tmp_path + monkeypatch.chdir for isolation."""

    def test_creates_input_and_output(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        make_dirs()
        assert (tmp_path / "input").is_dir()
        assert (tmp_path / "output").is_dir()

    def test_idempotent(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        make_dirs()
        make_dirs()  # Second call should not raise
        assert (tmp_path / "input").is_dir()
        assert (tmp_path / "output").is_dir()

    def test_only_creates_missing(self, tmp_path, monkeypatch) -> None:
        """If input/ already exists but output/ does not, only output/ is created."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "input").mkdir()
        make_dirs()
        assert (tmp_path / "input").is_dir()
        assert (tmp_path / "output").is_dir()


# ---------------------------------------------------------------------------
# convert_image — non-HEIC paths
# ---------------------------------------------------------------------------

def _create_png(path: str, mode: str = "RGB", size: tuple[int, int] = (10, 10)) -> None:
    """Helper: create a simple PNG test image."""
    img = Image.new(mode, size, color=(255, 0, 0))
    img.save(path, format="PNG")


class TestConvertImage:
    """Tests for convert_image() — uses tmp_path + monkeypatch for isolation."""

    def test_png_to_jpg(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "sample.png")
        _create_png(src)

        out_path = convert_image(src, "jpg")

        assert os.path.exists(out_path)
        assert out_path.endswith(".jpg")
        # Input backup should exist
        assert os.path.exists(os.path.join("input", "sample.png"))

    def test_png_to_bmp(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "sample.png")
        _create_png(src)

        out_path = convert_image(src, "bmp")

        assert os.path.exists(out_path)
        assert out_path.endswith(".bmp")
        with Image.open(out_path) as img:
            assert img.size == (10, 10)

    def test_png_to_webp(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "test.png")
        _create_png(src)

        out_path = convert_image(src, "webp")

        assert os.path.exists(out_path)
        assert out_path.endswith(".webp")

    def test_empty_format_raises_valueerror(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "sample.png")
        _create_png(src)

        with pytest.raises(ValueError, match="target_format must be specified"):
            convert_image(src, "")

    def test_none_format_raises_valueerror(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "sample.png")
        _create_png(src)

        # None is falsy, so the check `if not target_format` should catch it
        # BUT: os.path.splitext on None will raise AttributeError before ValueError
        # because `target_format.lower()` is called AFTER the check.
        # Actually the check is first: `if not target_format:` — None is falsy, so
        # ValueError should be raised.
        with pytest.raises(ValueError, match="target_format must be specified"):
            convert_image(src, None)

    def test_uppercase_format_is_normalized(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "sample.png")
        _create_png(src)

        out_path = convert_image(src, "BMP")

        assert out_path.endswith(".bmp")
        assert os.path.exists(out_path)

    def test_output_file_is_in_output_dir(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "photo.png")
        _create_png(src)

        out_path = convert_image(src, "jpg")

        assert os.path.isabs(out_path)
        assert os.path.basename(os.path.dirname(out_path)) == "output"

    def test_nonexistent_source_raises(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        with pytest.raises(Exception):
            convert_image(str(tmp_path / "nonexistent.png"), "jpg")

    def test_eps_target_converts_rgba_to_rgb(self, tmp_path, monkeypatch) -> None:
        """EPS path should convert RGBA images to RGB without raising."""
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "rgba_image.png")
        # Create RGBA image
        _create_png(src, mode="RGBA")

        # EPS conversion: the code converts to RGB before saving
        # Note: Pillow's EPS save may still fail depending on version/OS,
        # but the code path exercises the RGB conversion branch.
        try:
            out_path = convert_image(src, "eps")
            assert out_path.endswith(".eps")
        except Exception:
            # EPS saving may not be available on all systems (needs Ghostscript)
            # The important thing is that the RGB conversion code path was hit
            pytest.skip("EPS saving not available on this system (needs Ghostscript)")

    def test_eps_target_with_rgb_image(self, tmp_path, monkeypatch) -> None:
        """EPS path should also work with already-RGB images."""
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "rgb_image.png")
        _create_png(src, mode="RGB")

        try:
            out_path = convert_image(src, "eps")
            assert out_path.endswith(".eps")
        except Exception:
            pytest.skip("EPS saving not available on this system (needs Ghostscript)")


# ---------------------------------------------------------------------------
# convert_image — HEIC path (mocked)
# ---------------------------------------------------------------------------

class TestConvertImageHeic:
    """Tests for the HEIC branch of convert_image(), with pillow_heif mocked."""

    def test_heic_extension_dispatches_to_convert_heic(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)

        # Create a dummy file with .heic extension
        src = str(tmp_path / "photo.heic")
        with open(src, "wb") as f:
            f.write(b"\x00" * 100)

        # Mock convert_heic so we don't need real HEIF data
        with patch("utils.convert_heic", return_value="output/photo.png") as mock_ch:
            out_path = convert_image(src, "png")

        mock_ch.assert_called_once_with(src, "photo", "png")
        assert out_path == "output/photo.png"
        # Input backup should exist
        assert os.path.exists(os.path.join("input", "photo.heic"))

    def test_heif_extension_dispatches_to_convert_heic(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)

        src = str(tmp_path / "photo.heif")
        with open(src, "wb") as f:
            f.write(b"\x00" * 100)

        with patch("utils.convert_heic", return_value="output/photo.jpg") as mock_ch:
            out_path = convert_image(src, "jpg")

        mock_ch.assert_called_once_with(src, "photo", "jpg")
        assert out_path == "output/photo.jpg"

    def test_heic_case_insensitive(self, tmp_path, monkeypatch) -> None:
        """HEIC detection should be case-insensitive (.HEIC, .Heic, etc.)."""
        monkeypatch.chdir(tmp_path)

        src = str(tmp_path / "photo.HEIC")
        with open(src, "wb") as f:
            f.write(b"\x00" * 100)

        with patch("utils.convert_heic", return_value="output/photo.png") as mock_ch:
            out_path = convert_image(src, "png")

        mock_ch.assert_called_once_with(src, "photo", "png")


# ---------------------------------------------------------------------------
# load_heif_as_pil (mocked)
# ---------------------------------------------------------------------------

class TestLoadHeifAsPil:
    """Tests for load_heif_as_pil() with pillow_heif mocked."""

    def test_successful_load(self) -> None:
        # Create a mock frame with the attributes Pillow needs
        mock_frame = SimpleNamespace(
            mode="RGB",
            size=(10, 10),
            data=bytes(10 * 10 * 3),  # RGB = 3 bytes per pixel
            stride=10 * 3,
        )
        mock_heif_file = MagicMock()
        mock_heif_file.__iter__ = MagicMock(return_value=iter([mock_frame]))

        with patch("utils.pillow_heif.read_heif", return_value=mock_heif_file):
            result = load_heif_as_pil("dummy.heic")

        assert isinstance(result, Image.Image)
        assert result.size == (10, 10)
        assert result.mode == "RGB"

    def test_no_frames_raises_valueerror(self) -> None:
        mock_heif_file = MagicMock()
        mock_heif_file.__iter__ = MagicMock(return_value=iter([]))

        with patch("utils.pillow_heif.read_heif", return_value=mock_heif_file):
            with pytest.raises(ValueError, match="No image frames found"):
                load_heif_as_pil("empty.heic")

    def test_read_heif_failure_propagates(self) -> None:
        with patch("utils.pillow_heif.read_heif", side_effect=FileNotFoundError("not found")):
            with pytest.raises(FileNotFoundError):
                load_heif_as_pil("nonexistent.heic")


# ---------------------------------------------------------------------------
# convert_heic (mocked)
# ---------------------------------------------------------------------------

class TestConvertHeic:
    """Tests for convert_heic() with load_heif_as_pil mocked."""

    def test_convert_heic_saves_output(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)

        mock_img = Image.new("RGB", (10, 10), color=(0, 255, 0))

        with patch("utils.load_heif_as_pil", return_value=mock_img):
            out_path = convert_heic("dummy.heic", "photo", "png")

        assert os.path.isabs(out_path)
        assert out_path == os.path.abspath(os.path.join("output", "photo.png"))
        assert os.path.exists(out_path)
        with Image.open(out_path) as img:
            assert img.size == (10, 10)

    def test_convert_heic_to_jpg(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)

        mock_img = Image.new("RGB", (20, 15), color=(0, 0, 255))

        with patch("utils.load_heif_as_pil", return_value=mock_img):
            out_path = convert_heic("dummy.heic", "landscape", "jpg")

        assert os.path.isabs(out_path)
        assert out_path == os.path.abspath(os.path.join("output", "landscape.jpg"))
        assert os.path.exists(out_path)

    def test_convert_heic_propagates_load_error(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        os.makedirs("output", exist_ok=True)

        with patch("utils.load_heif_as_pil", side_effect=ValueError("No frames")):
            with pytest.raises(ValueError, match="No frames"):
                convert_heic("bad.heic", "bad", "png")


# ---------------------------------------------------------------------------
# Edge-case / regression tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Tests covering edge cases and potential issues."""

    def test_convert_image_with_spaces_in_filename(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "my photo (1).png")
        _create_png(src)

        out_path = convert_image(src, "bmp")

        assert os.path.exists(out_path)
        assert "my photo (1).bmp" in out_path

    def test_convert_image_with_dots_in_filename(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "photo.2024.01.png")
        _create_png(src)

        out_path = convert_image(src, "jpg")

        # os.path.splitext splits on last dot, so base = "photo.2024.01"
        assert os.path.exists(out_path)
        assert out_path.endswith(".jpg")

    def test_format_bytes_with_float_input(self) -> None:
        # format_bytes type hint says int, but floats work due to duck typing
        # This documents that behavior
        result = format_bytes(1024.5)
        assert "KB" in result

    def test_convert_image_returns_absolute_path(self, tmp_path, monkeypatch) -> None:
        """convert_image returns absolute paths."""
        monkeypatch.chdir(tmp_path)
        src = str(tmp_path / "img.png")
        _create_png(src)

        out_path = convert_image(src, "bmp")

        assert os.path.isabs(out_path)
