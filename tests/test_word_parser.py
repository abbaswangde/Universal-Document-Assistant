
import unittest
import tempfile
from pathlib import Path

from docx import Document

from app.ingestion.loaders.word_parser import parse_word


class TestWordParser(unittest.TestCase):

    def test_parse_word(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "sample.docx"

            document = Document()
            document.add_paragraph("Hello Universal Document Assistant")

            table = document.add_table(rows=1, cols=2)
            table.cell(0, 0).text = "Name"
            table.cell(0, 1).text = "Abbas"

            document.save(file_path)

            result = parse_word(file_path)

            self.assertIn(
                "Hello Universal Document Assistant",
                result
            )

            self.assertIn("Name | Abbas", result)

    def test_missing_file(self):

        with self.assertRaises(FileNotFoundError):
            parse_word("nonexistent.docx")


if __name__ == "__main__":
    unittest.main()
