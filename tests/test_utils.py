import os
import sys
import unittest

# Ensure src/ is importable
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from utils import format_bytes  # noqa: E402


class TestFormatBytes(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(format_bytes(0), "0 bytes")
        self.assertEqual(format_bytes(500), "500 bytes")

    def test_kilobytes(self):
        self.assertEqual(format_bytes(2048), "2.0 KB")

    def test_megabytes(self):
        self.assertEqual(format_bytes(1024 * 1024), "1.0 MB")


if __name__ == "__main__":
    unittest.main()
