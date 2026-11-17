
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

            self.assertIn("Page 1", result)

            self.assertIn(
                "Universal Document Assistant PDF Test",
                result
            )

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
