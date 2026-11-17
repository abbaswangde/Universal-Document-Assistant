
import unittest
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

from app.ingestion.loaders.powerpoint_parser import parse_powerpoint


class TestPowerPointParser(unittest.TestCase):

    def test_parse_powerpoint(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "sample.pptx"

            presentation = Presentation()

            slide = presentation.slides.add_slide(
                presentation.slide_layouts[6]
            )

            textbox = slide.shapes.add_textbox(
                Inches(1),
                Inches(1),
                Inches(5),
                Inches(1)
            )

            textbox.text = "Universal Document Assistant"

            presentation.save(file_path)

            result = parse_powerpoint(file_path)

            self.assertIn("Slide 1", result)
            self.assertIn(
                "Universal Document Assistant",
                result
            )

    def test_missing_file(self):

        with self.assertRaises(FileNotFoundError):
            parse_powerpoint("nonexistent.pptx")

    def test_unsupported_format(self):

        with tempfile.NamedTemporaryFile(
            suffix=".pdf"
        ) as temp_file:

            with self.assertRaises(ValueError):
                parse_powerpoint(temp_file.name)


if __name__ == "__main__":
    unittest.main()
