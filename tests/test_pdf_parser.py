
import unittest
import tempfile
from pathlib import Path

import pymupdf

from app.ingestion.loaders.pdf_parser import parse_pdf


class TestPDFParser(unittest.TestCase):

    def test_parse_pdf(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "sample.pdf"

            document = pymupdf.open()

            page = document.new_page()

            page.insert_text(
                (72, 72),
                "Universal Document Assistant PDF Test"
            )

            document.save(file_path)
            document.close()

            result = parse_pdf(file_path)

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)

            self.assertEqual(
                result[0]["source"],
                "sample.pdf"
            )

            self.assertEqual(
                result[0]["source_type"],
                "pdf"
            )

            self.assertEqual(
                result[0]["page"],
                1
            )

            self.assertIn(
                "Universal Document Assistant PDF Test",
                result[0]["text"]
            )

    def test_multiple_pages(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "multiple.pdf"

            document = pymupdf.open()

            page1 = document.new_page()
            page1.insert_text((72, 72), "First page content")

            page2 = document.new_page()
            page2.insert_text((72, 72), "Second page content")

            document.save(file_path)
            document.close()

            result = parse_pdf(file_path)

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["page"], 1)
            self.assertEqual(result[1]["page"], 2)

            self.assertIn("First page content", result[0]["text"])
            self.assertIn("Second page content", result[1]["text"])

    def test_missing_file(self):

        with self.assertRaises(FileNotFoundError):
            parse_pdf("nonexistent.pdf")

    def test_unsupported_format(self):

        with tempfile.NamedTemporaryFile(
            suffix=".txt"
        ) as temp_file:

            with self.assertRaises(ValueError):
                parse_pdf(temp_file.name)


if __name__ == "__main__":
    unittest.main()
