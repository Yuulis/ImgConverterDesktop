import os
import sys
import tempfile
import unittest

from PIL import Image

# Ensure src/ is importable
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from utils import convert_image, make_dirs  # noqa: E402


class TestConvertImage(unittest.TestCase):
    def setUp(self):
        # Run tests in an isolated temporary directory
        self.tmpdir = tempfile.TemporaryDirectory()
        self.cwd = os.getcwd()
        os.chdir(self.tmpdir.name)
        make_dirs()

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmpdir.cleanup()

    def _create_sample_image(self, path: str, size=(10, 10), color=(255, 0, 0)):
        img = Image.new("RGB", size, color)
        img.save(path)

    def test_convert_png_to_jpg(self):
        src = os.path.join(self.tmpdir.name, "sample_src.png")
        self._create_sample_image(src)

        out_path = convert_image(src, "jpg")

        self.assertTrue(os.path.exists(out_path))
        self.assertTrue(os.path.exists(os.path.join("input", "sample_src.png")))

    def test_invalid_file_raises(self):
        bad = os.path.join(self.tmpdir.name, "not_image.txt")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("not an image")
        with self.assertRaises(Exception):
            convert_image(bad, "png")


if __name__ == "__main__":
    unittest.main()
