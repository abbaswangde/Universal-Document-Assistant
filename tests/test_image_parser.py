
import unittest
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from app.ingestion.loaders.image_parser import parse_image


class TestImageParser(unittest.TestCase):

    def test_parse_image(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "sample.png"

            image = Image.new(
                "RGB",
                (1000, 300),
                color="white"
            )

            draw = ImageDraw.Draw(image)

            draw.text(
                (30, 100),
                "Universal Document Assistant",
                fill="black"
            )

            image.save(file_path)

            result = parse_image(file_path)

            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)

            record = result[0]

            self.assertIn("text", record)
            self.assertIn("Universal", record["text"])
            self.assertEqual(record["source"], "sample.png")
            self.assertEqual(record["source_type"], "image")
            self.assertEqual(record["page"], 1)

    def test_missing_file(self):

        with self.assertRaises(FileNotFoundError):
            parse_image("nonexistent.png")

    def test_unsupported_format(self):

        with tempfile.NamedTemporaryFile(
            suffix=".pdf"
        ) as temp_file:

            with self.assertRaises(ValueError):
                parse_image(temp_file.name)


if __name__ == "__main__":
    unittest.main()
