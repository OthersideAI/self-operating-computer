"""Offline image regressions; no display, mouse, keyboard or model calls."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image


class ScreenshotCompressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Only desktop capture dependencies are stubbed; Pillow and file IO are real.
        native_imports = patch.dict(
            sys.modules,
            {
                "pyautogui": MagicMock(),
                "Xlib": MagicMock(),
                "Xlib.display": MagicMock(),
                "Xlib.X": MagicMock(),
                "Xlib.Xutil": MagicMock(),
            },
        )
        native_imports.start()
        cls.addClassCleanup(native_imports.stop)
        cls.screenshot = importlib.import_module("operate.utils.screenshot")

    def assert_compressed(self, image, expected, **save_options):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.png"
            target = Path(directory) / "compressed.jpg"
            image.save(source, **save_options)
            with Image.open(source) as fixture:
                self.assertEqual(fixture.mode, image.mode)
                self.assertEqual(fixture.getpixel((8, 8)), image.getpixel((8, 8)))
            self.screenshot.compress_screenshot(source, target)
            with Image.open(target) as result:
                result.load()
                self.assertEqual(result.format, "JPEG")
                self.assertEqual(result.mode, "RGB")
                self.assertEqual(result.size, image.size)
                for actual, wanted in zip(result.getpixel((8, 8)), expected):
                    self.assertLessEqual(
                        abs(actual - wanted),
                        3,
                        f"pixel={result.getpixel((8, 8))}, expected={expected}",
                    )
            with Image.open(source) as original:
                self.assertEqual(original.mode, image.mode)

    def test_transparent_luminance_alpha(self):
        self.assert_compressed(Image.new("LA", (16, 16), (0, 0)), (255, 255, 255))

    def test_partial_luminance_alpha(self):
        self.assert_compressed(Image.new("LA", (16, 16), (0, 128)), (127, 127, 127))

    def test_transparent_palette(self):
        image = Image.new("P", (16, 16), 0)
        image.putpalette([255, 0, 0] + [0] * 765)
        self.assert_compressed(image, (255, 255, 255), transparency=0)

    def test_partial_palette_alpha(self):
        image = Image.new("P", (16, 16), 0)
        image.putpalette([255, 0, 0] + [0] * 765)
        self.assert_compressed(image, (255, 127, 127), transparency=bytes([128]))

    def test_partial_rgba(self):
        self.assert_compressed(
            Image.new("RGBA", (16, 16), (255, 0, 0, 128)), (255, 127, 127)
        )

    def test_rgb(self):
        self.assert_compressed(Image.new("RGB", (16, 16), (30, 80, 120)), (30, 80, 120))

    def test_grayscale(self):
        self.assert_compressed(Image.new("L", (16, 16), 100), (100, 100, 100))

    def test_opaque_palette(self):
        image = Image.new("P", (16, 16), 0)
        image.putpalette([30, 80, 120] + [0] * 765)
        self.assert_compressed(image, (30, 80, 120))


if __name__ == "__main__":
    unittest.main()
