
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

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)

            record = result[0]

            self.assertIn(
                "Universal Document Assistant",
                record["text"]
            )

            self.assertEqual(record["source"], "sample.pptx")
            self.assertEqual(record["source_type"], "pptx")
            self.assertEqual(record["page"], 1)
            self.assertEqual(record["slide"], 1)

    def test_multiple_slides(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "multiple.pptx"

            presentation = Presentation()

            for index in range(3):

                slide = presentation.slides.add_slide(
                    presentation.slide_layouts[6]
                )

                textbox = slide.shapes.add_textbox(
                    Inches(1),
                    Inches(1),
                    Inches(5),
                    Inches(1)
                )

                textbox.text = f"Slide content {index + 1}"

            presentation.save(file_path)

            result = parse_powerpoint(file_path)

            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]["slide"], 1)
            self.assertEqual(result[1]["slide"], 2)
            self.assertEqual(result[2]["slide"], 3)

    def test_empty_presentation(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "empty.pptx"

            presentation = Presentation()
            presentation.save(file_path)

            result = parse_powerpoint(file_path)

            self.assertEqual(result, [])

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
